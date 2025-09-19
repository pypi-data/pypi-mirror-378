"""Configuration management for ClickHouse migration."""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from pydantic import BaseModel, Field, validator


class DatabaseConfig(BaseModel):
    """Configuration for a single database connection."""
    uri: str = Field(..., description="ClickHouse connection URI")
    database: Optional[str] = Field(None, description="Override database name")
    timeout: int = Field(30, description="Connection timeout in seconds")
    max_retries: int = Field(3, description="Maximum number of connection retries")


class MigrationBatchConfig(BaseModel):
    """Configuration for batch processing."""
    size: int = Field(100000, description="Number of rows per batch", ge=1000, le=10000000)
    parallel_workers: int = Field(4, description="Number of parallel workers", ge=1, le=32)
    memory_limit_mb: int = Field(1024, description="Memory limit per worker in MB", ge=100, le=16384)


class MigrationProgressConfig(BaseModel):
    """Configuration for progress tracking."""
    update_interval: int = Field(1000, description="Progress update interval in rows", ge=100)
    log_level: str = Field("INFO", description="Logging level")
    checkpoint_interval: int = Field(50000, description="Checkpoint creation interval", ge=1000)


class MigrationTableConfig(BaseModel):
    """Configuration for table migration."""
    name: str = Field(..., description="Table name")
    query: Optional[str] = Field(None, description="Custom query for data selection")
    where_clause: Optional[str] = Field(None, description="WHERE clause for filtering data")
    create_table: bool = Field(True, description="Whether to create the table structure")
    drop_target: bool = Field(False, description="Whether to drop target table if exists")
    chunk_column: Optional[str] = Field(None, description="Column to use for chunking large tables")


class MigrationConfig(BaseModel):
    """Main configuration class for ClickHouse migration."""

    # Connection configurations
    source: DatabaseConfig = Field(..., description="Source database configuration")
    target: DatabaseConfig = Field(..., description="Target database configuration")

    # Migration settings
    tables: List[MigrationTableConfig] = Field(default_factory=list, description="Tables to migrate")
    exclude_tables: List[str] = Field(default_factory=list, description="Tables to exclude from migration")
    migrate_schema: bool = Field(True, description="Whether to migrate table schemas")
    migrate_data: bool = Field(True, description="Whether to migrate data")

    # Performance settings
    batch: MigrationBatchConfig = Field(default_factory=MigrationBatchConfig)
    progress: MigrationProgressConfig = Field(default_factory=MigrationProgressConfig)

    # Resume settings
    resume: bool = Field(False, description="Whether to resume from previous checkpoint")
    checkpoint_file: Optional[str] = Field(None, description="Path to checkpoint file")

    # Advanced settings
    verify_data: bool = Field(True, description="Whether to verify data integrity after migration")
    dry_run: bool = Field(False, description="Whether to perform a dry run")

    # Schema transformation settings
    transform_engines: bool = Field(True, description="Whether to automatically transform incompatible engines")
    engine_transformation_mode: str = Field("cloud_to_selfhosted", description="Engine transformation mode")

    @validator('tables', pre=True)
    def parse_tables(cls, v):
        """Parse table configurations."""
        if isinstance(v, list) and v and isinstance(v[0], str):
            return [MigrationTableConfig(name=table) for table in v]
        return v

    @classmethod
    def from_file(cls, config_path: str) -> "MigrationConfig":
        """Load configuration from a YAML file."""
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        return cls(**data)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MigrationConfig":
        """Create configuration from dictionary."""
        return cls(**data)

    @classmethod
    def from_cli_args(
        cls,
        source_uri: str,
        target_uri: str,
        tables: Optional[List[str]] = None,
        query: Optional[str] = None,
        batch_size: int = 100000,
        workers: int = 4,
        **kwargs
    ) -> "MigrationConfig":
        """Create configuration from CLI arguments."""

        table_configs = []
        if tables:
            for table in tables:
                table_configs.append(MigrationTableConfig(name=table, query=query))
        elif query:
            # If only query is provided, we'll need to determine the table name
            table_configs.append(MigrationTableConfig(name="custom_query", query=query))

        config_data = {
            "source": {"uri": source_uri},
            "target": {"uri": target_uri},
            "tables": table_configs,
            "batch": {"size": batch_size, "parallel_workers": workers},
            **kwargs
        }

        return cls(**config_data)

    def to_file(self, config_path: str):
        """Save configuration to a YAML file."""
        path = Path(config_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(
                self.dict(exclude_none=True),
                f,
                default_flow_style=False,
                sort_keys=False,
                indent=2
            )

    def get_checkpoint_file(self) -> str:
        """Get the checkpoint file path."""
        if self.checkpoint_file:
            return self.checkpoint_file

        # Generate default checkpoint file name
        import hashlib
        content = f"{self.source.uri}_{self.target.uri}"
        hash_suffix = hashlib.md5(content.encode()).hexdigest()[:8]
        return f"migration_checkpoint_{hash_suffix}.json"

    def validate_connections(self) -> List[str]:
        """Validate connection configurations."""
        errors = []

        # Basic URI validation
        for name, config in [("source", self.source), ("target", self.target)]:
            if not config.uri:
                errors.append(f"{name} URI is required")
            elif not any(scheme in config.uri for scheme in ['clickhouse://', 'http://', 'https://']):
                errors.append(f"{name} URI must start with clickhouse://, http://, or https://")

        return errors

    class Config:
        """Pydantic configuration."""
        extra = "forbid"
        validate_assignment = True