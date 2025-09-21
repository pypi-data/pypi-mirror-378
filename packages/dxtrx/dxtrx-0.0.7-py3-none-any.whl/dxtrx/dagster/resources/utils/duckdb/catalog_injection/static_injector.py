from __future__ import annotations

from typing import Dict, Any, List

from .base import CatalogInjector, Action


class StaticViewInjector(CatalogInjector):
    def __init__(self, cfg: Dict[str, Any]):
        self._cfg = cfg or {}

    def name(self) -> str:
        return "static"

    def requires_extensions(self) -> List[str]:
        return ["httpfs"]

    def prepare(self, conn, config: Dict[str, Any]) -> None:
        # Ensure S3 credential chain secret exists when using httpfs
        # The caller should have loaded httpfs already; we rely on DuckDB's credential chain.
        conn.execute(
            "CREATE SECRET IF NOT EXISTS (TYPE s3, PROVIDER credential_chain)"
        )

    def plan(self, conn, config: Dict[str, Any]) -> List[Action]:
        actions: List[Action] = []
        views = (self._cfg or {}).get("views") or []
        for idx, v in enumerate(views):
            schema = v.get("schema")
            name = v.get("name")
            glob = v.get("glob")
            options = v.get("options") or {}
            if not schema or not name or not glob:
                # skip invalid entries quietly
                continue

            schema_sql = f'CREATE SCHEMA IF NOT EXISTS "{schema.replace("\"", "\"\"")}"'
            actions.append(
                Action(
                    id=f"schema:{schema}",
                    kind="CREATE_SCHEMA",
                    sql=schema_sql,
                )
            )

            opt_kv = []
            for k, val in options.items():
                if isinstance(val, str):
                    opt_kv.append(f"{k}='{val.replace("'", "''")}'")
                else:
                    opt_kv.append(f"{k}={val}")
            opt_sql = ", ".join(opt_kv)
            read_fn = f"read_parquet('{glob.replace("'", "''")}'" + (f", {opt_sql}" if opt_sql else "") + ")"

            view_sql = (
                f'CREATE OR REPLACE VIEW "{schema.replace("\"", "\"\"")}"."{name.replace("\"", "\"\"")}" '
                f"AS SELECT * FROM {read_fn}"
            )

            actions.append(
                Action(
                    id=f"view:{schema}.{name}",
                    kind="CREATE_OR_REPLACE_VIEW",
                    sql=view_sql,
                    depends_on=[f"schema:{schema}"]
                )
            )
        return actions


