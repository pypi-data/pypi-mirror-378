from __future__ import annotations

from typing import Iterable


def ensure_extensions_loaded(conn, extensions: Iterable[str]) -> None:
    """Install and load DuckDB extensions once.

    For each extension name in `extensions`, attempts to INSTALL (best-effort)
    and then LOAD it. Errors propagate from LOAD.
    """
    seen = set()
    for ext in extensions or []:
        if not ext or ext in seen:
            continue
        seen.add(ext)
        try:
            conn.execute(f"INSTALL {ext}")
        except Exception:
            # INSTALL can fail if already available; ignore
            pass
        conn.execute(f"LOAD {ext}")


