from __future__ import annotations

import re
from typing import Dict, Any, List, Optional

from .base import CatalogInjector, Action


class GlueParquetInjector(CatalogInjector):
    def __init__(self, cfg: Dict[str, Any]):
        self._cfg = cfg or {}

    def name(self) -> str:
        return "glue"

    def requires_extensions(self) -> List[str]:
        return ["httpfs"]

    def prepare(self, conn, config: Dict[str, Any]) -> None:
        # Ensure S3 credential chain secret exists; httpfs must be loaded by caller
        conn.execute(
            "CREATE SECRET IF NOT EXISTS (TYPE s3, PROVIDER credential_chain)"
        )

    def _to_identifier(self, ident: str) -> str:
        return '"' + ident.replace('"', '""') + '"'

    def _convert_projection_template_to_glob(self, template: str) -> str:
        # Replace ${key} style placeholders with * and ensure parquet suffix
        glob = re.sub(r"\$\{[^}]+\}", "*", template)
        if not glob.endswith(".parquet"):
            if glob.endswith("/"):
                glob = glob + "*.parquet"
            else:
                glob = glob.rstrip("/") + "/**/*.parquet"
        return glob

    def _infer_glob_and_options(self, location: str, has_hive_style: bool) -> tuple[str, Dict[str, Any]]:
        if has_hive_style:
            return (location.rstrip('/') + "/**/*.parquet", {"hive_partitioning": 1})
        return (location.rstrip('/') + "/**/*.parquet", {})

    def plan(self, conn, config: Dict[str, Any]) -> List[Action]:
        # NOTE: This is a minimal stub: caller is expected to provide a resolved list of tables
        # in cfg to avoid adding boto3 dependency here. Structure:
        # {
        #   "databases": ["db1", ...],
        #   "tables": [{"database": "db1", "name": "t", "location": "s3://...", "format": "parquet",
        #               "projection_template": Optional[str], "hive_style": Optional[bool]}]
        # }
        actions: List[Action] = []

        databases = self._cfg.get("databases") or []
        tables = self._cfg.get("tables") or []

        # Create schemas for each database
        for db in databases:
            actions.append(Action(
                id=f"schema:{db}",
                kind="CREATE_SCHEMA",
                sql=f'CREATE SCHEMA IF NOT EXISTS {self._to_identifier(db)}'
            ))

        for t in tables:
            db = t.get("database")
            name = t.get("name")
            fmt = (t.get("format") or "").lower()
            if not db or not name:
                continue
            if fmt and fmt != "parquet":
                # skip non-parquet
                continue

            location: Optional[str] = t.get("location")
            if not location or not location.startswith("s3://"):
                continue

            projection_template = t.get("projection_template")
            hive_style: bool = bool(t.get("hive_style"))

            if projection_template:
                glob = self._convert_projection_template_to_glob(projection_template)
                opts = {}
            else:
                glob, opts = self._infer_glob_and_options(location, hive_style)

            opt_kv = []
            for k, val in opts.items():
                if isinstance(val, str):
                    opt_kv.append(f"{k}='{val.replace("'", "''")}'")
                else:
                    opt_kv.append(f"{k}={val}")
            opt_sql = ", ".join(opt_kv)
            read_fn = f"read_parquet('{glob.replace("'", "''")}'" + (f", {opt_sql}" if opt_sql else "") + ")"

            view_sql = (
                f"CREATE OR REPLACE VIEW {self._to_identifier(db)}.{self._to_identifier(name)} "
                f"AS SELECT * FROM {read_fn}"
            )

            actions.append(Action(
                id=f"view:{db}.{name}",
                kind="CREATE_OR_REPLACE_VIEW",
                sql=view_sql,
                depends_on=[f"schema:{db}"]
            ))

        return actions


