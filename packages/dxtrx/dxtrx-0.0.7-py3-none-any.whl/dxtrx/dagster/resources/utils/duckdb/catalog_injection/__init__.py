"""Catalog injection SPI for DuckDB.

Provides a minimal, extensible interface for injecting external catalogs into
DuckDB by emitting idempotent DDL (schemas, views, attaches).
"""

from .base import Action, Result, Health, CatalogInjector

__all__ = [
    "Action",
    "Result",
    "Health",
    "CatalogInjector",
]


