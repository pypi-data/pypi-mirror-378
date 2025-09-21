from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Sequence, Dict, Any


@dataclass(frozen=True)
class Action:
    id: str
    kind: str  # CREATE_SCHEMA | CREATE_OR_REPLACE_VIEW | ATTACH
    sql: str
    depends_on: Optional[Sequence[str]] = None


@dataclass
class Result:
    applied_count: int
    skipped_count: int
    errors: List[str]


@dataclass
class Health:
    ok: bool
    details: Dict[str, Any]


class CatalogInjector:
    def name(self) -> str:
        raise NotImplementedError

    def requires_extensions(self) -> List[str]:
        return []

    def prepare(self, conn, config: Dict[str, Any]) -> None:
        pass

    def plan(self, conn, config: Dict[str, Any]) -> List[Action]:
        raise NotImplementedError

    def apply(self, conn, actions: List[Action]) -> Result:
        applied = 0
        skipped = 0
        errors: List[str] = []
        for action in actions:
            try:
                conn.execute(action.sql)
                applied += 1
            except Exception as e:
                # Best-effort idempotency: treat known already-exists as skip
                msg = str(e)
                if "already exists" in msg or "Duplicate key" in msg or "already attached" in msg:
                    skipped += 1
                else:
                    errors.append(f"{action.id}: {e}")
        return Result(applied_count=applied, skipped_count=skipped, errors=errors)

    def refresh(self, conn, scope: Optional[Dict[str, Any]] = None) -> Optional[Result]:
        return None


