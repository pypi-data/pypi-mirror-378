"""
ClickHouse Migrator - A reliable CLI tool for migrating data between ClickHouse instances.

This package provides tools to migrate data, schema, and configurations between
ClickHouse Cloud and self-hosted ClickHouse instances with support for:
- Custom query-based data selection
- Real-time progress tracking
- Batch processing for large datasets
- Resume capability for interrupted migrations
- Schema and metadata migration
"""

__version__ = "1.0.0"
__author__ = "ClickHouse Migration Team"
__email__ = "contact@clickhouse-migrator.dev"

from .core.migrator import ClickHouseMigrator
from .core.connection import ClickHouseConnection
from .core.config import MigrationConfig

__all__ = [
    "ClickHouseMigrator",
    "ClickHouseConnection",
    "MigrationConfig",
    "__version__",
]