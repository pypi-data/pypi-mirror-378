import pathlib
from dataclasses import field
from typing import Optional, Iterable, List, Tuple, Any, Callable, Dict

import numpy as np
import pandas as pd
import polars as pl
import duckdb
import dagster as dg

from pydantic import BaseModel

from dxtrx.utils.jinja import Jinja2TemplateEngine
from dxtrx.utils.sql import format_sql_multistatement
from dxtrx.dagster.resources.sql import SQLBaseResource
from dxtrx.utils.types import DataFrameType, OutputType, DEFAULT_OUTPUT_TYPE
from dxtrx.utils.dataframe_conversion import convert_output, ensure_pandas
from dxtrx.dagster.resources.utils.duckdb.extensions import ensure_extensions_loaded
from dxtrx.dagster.resources.utils.duckdb.catalog_injection.base import Action
from dxtrx.dagster.resources.utils.duckdb.catalog_injection.glue_injector import GlueParquetInjector
from dxtrx.dagster.resources.utils.duckdb.catalog_injection.static_injector import StaticViewInjector


DEFAULT_DUCKDB_EXTENSIONS: List[str] = ["httpfs", "postgres"]


class DuckDBResource(SQLBaseResource):
    """
    DuckDB-only Dagster resource with:
      - Pinned connection
      - Jinja templating + multi-statement execution
      - Auto-reconnect retry
      - DataFrame uploads (fast: register + CTAS/INSERT)
      - Optional startup catalog injection via `catalog_injections` (Glue/Static)

    Catalog injection:
      Provide `catalog_injections` as a list of dicts, each with a `type` key
      ("glue" | "static") and injector-specific configuration. On startup,
      we build, prepare, plan, and apply idempotent actions. You can also call
      `inject_catalogs()` manually against the pinned connection.
    """

    # Config
    file_path: Optional[str] = None        # path to .duckdb, or ":memory:"
    base_dir: Optional[str] = None         # optional: resolve file_path relative to this base

    duckdb_extensions: List[str] = field(default_factory=lambda: DEFAULT_DUCKDB_EXTENSIONS)
    duckdb_install_extensions: bool = False  # kept for parity (not used here)
    extra_startup_sql: Optional[List[str]] = field(default_factory=list)

    # Catalog injection
    catalog_injections: Optional[List[Dict[str, Any]]] = field(default_factory=list)
    injection_mode: str = "startup"  # "startup" | "manual"
    dry_run: bool = False
    httpfs: Optional[Dict[str, Any]] = None  # reserved for future explicit creds; default uses credential chain

    # Behavior
    strict_fail_on_disconnect: bool = False

    # Internals
    _conn: Optional[duckdb.DuckDBPyConnection] = None
    _logger: Any = None
    _template_engine: Jinja2TemplateEngine = None
    _resolved_file_path: Optional[str] = None

    def _validate_params(self):
        """
        Validates configuration parameters for the DuckDB resource.

        Parity with the SQLAlchemy resource's validation approach:
        - Ensure types are correct
        - Validate complex structures like iceberg_catalogs
        - Allow in-memory default when file_path is not provided
        """
        # file_path and base_dir can be None or str
        if self.file_path is not None and not isinstance(self.file_path, str):
            raise ValueError("'file_path' must be a string or None")
        if self.base_dir is not None and not isinstance(self.base_dir, str):
            raise ValueError("'base_dir' must be a string or None")

        # duckdb_extensions must be a list[str] (if provided)
        if self.duckdb_extensions is not None:
            if not isinstance(self.duckdb_extensions, list) or not all(isinstance(ext, str) for ext in self.duckdb_extensions):
                raise ValueError("'duckdb_extensions' must be a list of strings")

        # extra_startup_sql must be a list[str] (if provided)
        if self.extra_startup_sql is not None:
            if not isinstance(self.extra_startup_sql, list) or not all(isinstance(stmt, str) for stmt in self.extra_startup_sql):
                raise ValueError("'extra_startup_sql' must be a list of strings")

        # catalog_injections must be a list[dict]
        if self.catalog_injections is not None:
            if not isinstance(self.catalog_injections, list):
                raise ValueError("'catalog_injections' must be a list of dicts")
            for idx, inj in enumerate(self.catalog_injections):
                if not isinstance(inj, dict):
                    raise ValueError(f"catalog_injections[{idx}] must be a dict")
                t = inj.get("type")
                if t not in {None, "glue", "static"}:
                    raise ValueError(f"Unsupported injector type: {t}")

        # Flags
        if not isinstance(self.strict_fail_on_disconnect, bool):
            raise ValueError("'strict_fail_on_disconnect' must be a boolean")

    # ------------- Lifecycle -------------

    def setup_for_execution(self, context: dg.InitResourceContext):
        self._logger = dg.get_dagster_logger("duckdb")
        self._template_engine = Jinja2TemplateEngine()

        # Validate provided configuration prior to applying defaults
        self._validate_params()

        # Compute resolved (non-mutating) file path
        candidate_path = self.file_path or ":memory:"
        if candidate_path != ":memory:":
            candidate_path = self._resolve_path(candidate_path, self.base_dir)
        self._resolved_file_path = candidate_path

        self._create_pinned_connection()

    def _resolve_path(self, path: str, base_dir: Optional[str]) -> str:
        p = pathlib.Path(path)
        if not p.is_absolute():
            base = pathlib.Path(base_dir) if base_dir else pathlib.Path.cwd()
            p = (base / p).resolve()
        return str(p)

    def renew_connection(self):
        """Manually recreate the pinned connection."""
        if self._conn is not None:
            try:
                self._conn.close()
            except Exception as e:
                if self._logger:
                    self._logger.debug(f"Error closing existing DuckDB conn: {e}")
        self._create_pinned_connection()

    def _create_pinned_connection(self):
        # Use resolved path to avoid mutating pydantic fields on Pythonic resources
        file_path = self._resolved_file_path or self.file_path or ":memory:"
        self._conn = duckdb.connect(file_path)

        # Optional startup SQL (PRAGMAs, etc.)
        for stmt in self.extra_startup_sql or []:
            self._conn.execute(stmt)

        # Startup injection if configured
        if (self.injection_mode or "startup") == "startup" and self.catalog_injections:
            try:
                self.inject_catalogs()
            except Exception as e:
                # keep setup resilient; surface error and continue
                if self._logger:
                    self._logger.error(f"Catalog injection failed during startup: {e}")

    # ------------- Helpers -------------

    def _with_auto_reconnect(self, op: Callable, *args, **kwargs):
        try:
            return op(*args, **kwargs)
        except duckdb.Error as e:
            if self.strict_fail_on_disconnect:
                raise
            # Best-effort reconnect then retry once
            if self._logger:
                self._logger.warning(f"DuckDB error encountered, attempting reconnect: {e}")
            self.renew_connection()
            return op(*args, **kwargs)

    @staticmethod
    def _sql_quote(value: str) -> str:
        """Basic SQL single-quote escaping for literals."""
        return "'" + value.replace("'", "''") + "'"

    @staticmethod
    def _ident_quote(ident: str) -> str:
        """Basic identifier quoting with double-quotes."""
        return '"' + ident.replace('"', '""') + '"'

    # ------------- Injection SPI integration -------------

    def _build_injectors(self, injections: Optional[List[Dict[str, Any]]]) -> List[Any]:
        inj_cfgs = injections if injections is not None else (self.catalog_injections or [])
        instances: List[Any] = []
        for inj in inj_cfgs:
            t = (inj or {}).get("type")
            cfg = dict(inj or {})
            cfg.pop("type", None)
            if t == "glue":
                instances.append(GlueParquetInjector(cfg))
            elif t == "static":
                instances.append(StaticViewInjector(cfg))
            else:
                # unsupported types are ignored silently
                continue
        return instances

    def _toposort_actions(self, actions: List[Action]) -> List[Action]:
        by_id = {a.id: a for a in actions}
        incoming = {a.id: set(a.depends_on or []) for a in actions}
        ready = [a for a in actions if not incoming[a.id]]
        ordered: List[Action] = []
        while ready:
            node = ready.pop(0)
            ordered.append(node)
            # remove edges
            for aid, deps in list(incoming.items()):
                if node.id in deps:
                    deps.remove(node.id)
                    if not deps and by_id[aid] not in ordered and by_id[aid] not in ready:
                        ready.append(by_id[aid])
        # append remaining in original order (cycle-safe fallback)
        seen = {a.id for a in ordered}
        for a in actions:
            if a.id not in seen:
                ordered.append(a)
        return ordered

    # Public API
    def inject_catalogs(
        self,
        injections: Optional[List[Dict[str, Any]]] = None,
        dry_run: Optional[bool] = None,
    ) -> None:
        conn = self._conn
        assert conn is not None, "Connection is not initialized"

        injectors = self._build_injectors(injections)
        # Aggregate extensions
        req_exts: List[str] = []
        for inj in injectors:
            for ext in inj.requires_extensions() or []:
                if ext not in req_exts:
                    req_exts.append(ext)
        if req_exts:
            ensure_extensions_loaded(conn, req_exts)

        # Ensure S3 credential chain secret when httpfs is used
        if "httpfs" in req_exts:
            try:
                conn.execute("CREATE SECRET IF NOT EXISTS (TYPE s3, PROVIDER credential_chain)")
            except Exception:
                pass

        effective_dry_run = self.dry_run if dry_run is None else dry_run

        for inj in injectors:
            try:
                conn.execute("BEGIN")
                inj.prepare(conn, {})
                actions = inj.plan(conn, {})
                actions = self._toposort_actions(actions)
                if effective_dry_run:
                    # Log minimal summary
                    if self._logger:
                        self._logger.info(
                            f"[duckdb][inject:{inj.name()}] planned actions: {len(actions)}"
                        )
                    conn.execute("ROLLBACK")
                    continue
                result = inj.apply(conn, actions)
                conn.execute("COMMIT")
                if self._logger:
                    self._logger.info(
                        f"[duckdb][inject:{inj.name()}] applied={result.applied_count} skipped={result.skipped_count} errors={len(result.errors)}"
                    )
                    if result.errors:
                        for e in result.errors[:5]:
                            self._logger.warning(f"[duckdb][inject:{inj.name()}] {e}")
            except Exception as e:
                try:
                    conn.execute("ROLLBACK")
                except Exception:
                    pass
                if self._logger:
                    self._logger.error(f"[duckdb][inject:{inj.name()}] failed: {e}")

    def set_httpfs_credentials(self, opts: Dict[str, Any] | None = None) -> None:
        """Load httpfs and configure S3 credential chain secret.

        Currently we only support DuckDB's credential chain provider.
        """
        conn = self._conn
        assert conn is not None, "Connection is not initialized"
        ensure_extensions_loaded(conn, ["httpfs"])
        try:
            conn.execute("CREATE SECRET IF NOT EXISTS (TYPE s3, PROVIDER credential_chain)")
        except Exception:
            pass

    def _resolve_full_context(self, run_context: dict) -> dict:
        return run_context

    def _resolve_query_or_query_file(
        self,
        query: Optional[str],
        query_file: Optional[str],
        context: dict,
        fail_if_multiquery: bool = False,
    ) -> List[str]:
        if query:
            template_string = query
        elif query_file:
            with open(query_file, "rt") as f:
                template_string = f.read()
        else:
            raise ValueError("Must provide either 'query' or 'query_file'")

        rendered = self._template_engine.render_string(
            template_string, self._resolve_full_context(context)
        )
        queries = format_sql_multistatement(rendered)

        if len(queries) == 0:
            raise ValueError("No actual queries found in the provided template string")
        if fail_if_multiquery and len(queries) > 1:
            raise ValueError("This operation is not supported for multistatement queries")
        return queries

    # ------------- Public API -------------

    def get_connection(self) -> duckdb.DuckDBPyConnection:
        """Return the pinned DuckDB connection."""
        return self._conn

    def run_query(
        self,
        query: Optional[str] = None,
        query_file: Optional[str] = None,
        params: Optional[dict] = None,
        atomic: bool = False,
    ) -> bool:
        def _op():
            queries = self._resolve_query_or_query_file(query, query_file, params or {}, False)

            if atomic:
                self._conn.execute("BEGIN")

            try:
                for q in queries:
                    if params:
                        # For ordinary statements (NOT ATTACH), DuckDB supports parameters.
                        self._conn.execute(q, params)
                    else:
                        self._conn.execute(q)
                if atomic:
                    self._conn.execute("COMMIT")
            except Exception:
                if atomic:
                    self._conn.execute("ROLLBACK")
                raise

            return True

        return self._with_auto_reconnect(_op)

    def get_query_results(
        self,
        query: Optional[str] = None,
        query_file: Optional[str] = None,
        params: Optional[dict] = None,
    ) -> List[Tuple]:
        def _op():
            qs = self._resolve_query_or_query_file(query, query_file, params or {}, True)
            cur = self._conn.execute(qs[0], params or {})
            return cur.fetchall()

        return self._with_auto_reconnect(_op)

    def get_query_results_as_df(
        self,
        query: Optional[str] = None,
        query_file: Optional[str] = None,
        params: Optional[dict] = None,
        output_type: OutputType = DEFAULT_OUTPUT_TYPE,
    ) -> DataFrameType:
        def _op():
            qs = self._resolve_query_or_query_file(query, query_file, params or {}, True)
            cur = self._conn.execute(qs[0], params or {})
            try:
                # Prefer Arrow path if available
                at = cur.fetch_arrow_table()
                df = at.to_pandas()
            except Exception:
                df = cur.fetch_df()
            return df

        pandas_df = self._with_auto_reconnect(_op)
        return convert_output(pandas_df, output_type)

    def check_if_table_exists(self, table_name: str, schema: str = "main") -> bool:
        def _op():
            # Check both tables and views for parity
            q = """
            SELECT 1
            FROM information_schema.tables
            WHERE table_schema = ? AND table_name = ?
            UNION ALL
            SELECT 1
            FROM information_schema.views
            WHERE table_schema = ? AND table_name = ?
            LIMIT 1
            """
            res = self._conn.execute(q, [schema, table_name, schema, table_name]).fetchall()
            return len(res) > 0

        return self._with_auto_reconnect(_op)

    def upload_df_to_table(
        self,
        df: DataFrameType,
        table_name: str,
        if_exists: str = "replace",
        schema: str = "main",
        json_columns: Optional[List[str]] = None,
        override_dtypes: Optional[dict] = None,
    ):
        json_columns = json_columns or []
        override_dtypes = override_dtypes or {}

        def _op():
            pandas_df = ensure_pandas(df).copy()

            # Apply dtype overrides
            for col, dtype in override_dtypes.items():
                if col in pandas_df.columns:
                    pandas_df[col] = pandas_df[col].astype(dtype)

            # Basic JSON handling: pre-serialize to text, cast on CTAS/INSERT if needed later.
            for col in json_columns:
                if col in pandas_df.columns:
                    pandas_df[col] = pandas_df[col].apply(
                        lambda x: None if x is None else (x if isinstance(x, str) else pd.io.json.dumps(x))
                    )

            # Temp view name (safe-ish)
            tmp_view = f"tmp_df_{abs(hash((table_name, len(pandas_df), tuple(pandas_df.columns))))}"

            # Register as view
            self._conn.register(tmp_view, pandas_df)

            fq_table = f'{self._ident_quote(schema)}.{self._ident_quote(table_name)}'

            if if_exists not in {"replace", "append", "fail"}:
                raise ValueError("if_exists must be one of: 'replace', 'append', 'fail'")

            # Ensure schema exists (DuckDB auto-creates main; CREATE SCHEMA IF NOT EXISTS is fine)
            self._conn.execute(f"CREATE SCHEMA IF NOT EXISTS {self._ident_quote(schema)}")

            table_exists = self.check_if_table_exists(table_name, schema=schema)

            if if_exists == "fail" and table_exists:
                raise ValueError(f"Table {schema}.{table_name} already exists")

            if if_exists == "replace":
                if table_exists:
                    self._conn.execute(f"DROP TABLE {fq_table}")
                self._conn.execute(f"CREATE TABLE {fq_table} AS SELECT * FROM {self._ident_quote(tmp_view)}")
            elif if_exists == "append":
                if not table_exists:
                    self._conn.execute(f"CREATE TABLE {fq_table} AS SELECT * FROM {self._ident_quote(tmp_view)}")
                else:
                    self._conn.execute(f"INSERT INTO {fq_table} SELECT * FROM {self._ident_quote(tmp_view)}")

            # Unregister to free memory
            try:
                self._conn.unregister(tmp_view)
            except Exception:
                pass

        self._with_auto_reconnect(_op)

    def upload_iterable_to_table(
        self,
        iterable: Iterable,
        table_name: str,
        schema: str = "main",
        json_columns: Optional[List[str]] = None,
        override_dtypes: Optional[dict] = None,
    ):
        items = []
        for item in iterable:
            if isinstance(item, dict):
                items.append(item)
            elif isinstance(item, BaseModel):
                items.append(item.model_dump())
            else:
                raise ValueError(f"Item is not a dict nor BaseModel: {item}")

        if not items:
            return

        df = pd.DataFrame(items, columns=items[0].keys()).replace({None: np.nan})
        self.upload_df_to_table(
            df,
            table_name=table_name,
            schema=schema,
            json_columns=json_columns or [],
            override_dtypes=override_dtypes or {},
        )

    def upload_single_row_to_table(
        self,
        row: dict,
        table_name: str,
        schema: str = "main",
        json_columns: Optional[List[str]] = None,
        override_dtypes: Optional[dict] = None,
    ):
        self.upload_df_to_table(
            pd.DataFrame([row]),
            table_name=table_name,
            schema=schema,
            json_columns=json_columns or [],
            override_dtypes=override_dtypes or {},
        )
