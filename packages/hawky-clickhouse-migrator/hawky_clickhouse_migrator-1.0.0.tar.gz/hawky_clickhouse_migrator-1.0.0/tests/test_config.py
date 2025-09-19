"""Tests for configuration management."""

import pytest
import tempfile
import os
from pathlib import Path

from clickhouse_migrator.core.config import (
    MigrationConfig,
    DatabaseConfig,
    MigrationTableConfig,
    MigrationBatchConfig,
)


class TestDatabaseConfig:
    """Test DatabaseConfig class."""

    def test_basic_config(self):
        """Test basic database configuration."""
        config = DatabaseConfig(uri="clickhouse://user:pass@localhost:8123/test")
        assert config.uri == "clickhouse://user:pass@localhost:8123/test"
        assert config.timeout == 30
        assert config.max_retries == 3

    def test_custom_config(self):
        """Test custom database configuration."""
        config = DatabaseConfig(
            uri="https://user:pass@cloud.clickhouse.com:8443/mydb",
            timeout=60,
            max_retries=5
        )
        assert config.uri == "https://user:pass@cloud.clickhouse.com:8443/mydb"
        assert config.timeout == 60
        assert config.max_retries == 5


class TestMigrationConfig:
    """Test MigrationConfig class."""

    def test_from_cli_args_basic(self):
        """Test creating config from basic CLI arguments."""
        config = MigrationConfig.from_cli_args(
            source_uri="clickhouse://user:pass@source:8123/db",
            target_uri="clickhouse://user:pass@target:8123/db"
        )

        assert config.source.uri == "clickhouse://user:pass@source:8123/db"
        assert config.target.uri == "clickhouse://user:pass@target:8123/db"
        assert config.batch.size == 100000
        assert config.batch.parallel_workers == 4
        assert config.migrate_schema is True
        assert config.migrate_data is True

    def test_from_cli_args_with_tables(self):
        """Test creating config with specific tables."""
        config = MigrationConfig.from_cli_args(
            source_uri="clickhouse://user:pass@source:8123/db",
            target_uri="clickhouse://user:pass@target:8123/db",
            tables=["users", "orders"],
            batch_size=50000,
            workers=2
        )

        assert len(config.tables) == 2
        assert config.tables[0].name == "users"
        assert config.tables[1].name == "orders"
        assert config.batch.size == 50000
        assert config.batch.parallel_workers == 2

    def test_from_cli_args_with_query(self):
        """Test creating config with custom query."""
        config = MigrationConfig.from_cli_args(
            source_uri="clickhouse://user:pass@source:8123/db",
            target_uri="clickhouse://user:pass@target:8123/db",
            query="SELECT * FROM users WHERE active = 1"
        )

        assert len(config.tables) == 1
        assert config.tables[0].name == "custom_query"
        assert config.tables[0].query == "SELECT * FROM users WHERE active = 1"

    def test_validate_connections_valid(self):
        """Test connection validation with valid URIs."""
        config = MigrationConfig.from_cli_args(
            source_uri="clickhouse://user:pass@source:8123/db",
            target_uri="https://user:pass@target:8443/db"
        )

        errors = config.validate_connections()
        assert len(errors) == 0

    def test_validate_connections_invalid(self):
        """Test connection validation with invalid URIs."""
        config = MigrationConfig.from_cli_args(
            source_uri="",
            target_uri="invalid://uri"
        )

        errors = config.validate_connections()
        assert len(errors) > 0
        assert any("source URI is required" in error for error in errors)

    def test_get_checkpoint_file_default(self):
        """Test default checkpoint file generation."""
        config = MigrationConfig.from_cli_args(
            source_uri="clickhouse://user:pass@source:8123/db",
            target_uri="clickhouse://user:pass@target:8123/db"
        )

        checkpoint_file = config.get_checkpoint_file()
        assert checkpoint_file.startswith("migration_checkpoint_")
        assert checkpoint_file.endswith(".json")

    def test_get_checkpoint_file_custom(self):
        """Test custom checkpoint file."""
        config = MigrationConfig.from_cli_args(
            source_uri="clickhouse://user:pass@source:8123/db",
            target_uri="clickhouse://user:pass@target:8123/db",
            checkpoint_file="custom_checkpoint.json"
        )

        checkpoint_file = config.get_checkpoint_file()
        assert checkpoint_file == "custom_checkpoint.json"

    def test_to_file_and_from_file(self):
        """Test saving and loading configuration file."""
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            temp_path = f.name

        try:
            # Create config
            original_config = MigrationConfig.from_cli_args(
                source_uri="clickhouse://user:pass@source:8123/db",
                target_uri="clickhouse://user:pass@target:8123/db",
                tables=["users", "orders"],
                batch_size=75000,
                workers=3
            )

            # Save to file
            original_config.to_file(temp_path)

            # Load from file
            loaded_config = MigrationConfig.from_file(temp_path)

            # Compare
            assert loaded_config.source.uri == original_config.source.uri
            assert loaded_config.target.uri == original_config.target.uri
            assert loaded_config.batch.size == original_config.batch.size
            assert loaded_config.batch.parallel_workers == original_config.batch.parallel_workers
            assert len(loaded_config.tables) == len(original_config.tables)

        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_from_file_not_found(self):
        """Test loading from non-existent file."""
        with pytest.raises(FileNotFoundError):
            MigrationConfig.from_file("non_existent_file.yaml")


class TestMigrationTableConfig:
    """Test MigrationTableConfig class."""

    def test_basic_table_config(self):
        """Test basic table configuration."""
        config = MigrationTableConfig(name="users")
        assert config.name == "users"
        assert config.query is None
        assert config.where_clause is None
        assert config.create_table is True
        assert config.drop_target is False

    def test_custom_table_config(self):
        """Test custom table configuration."""
        config = MigrationTableConfig(
            name="orders",
            query="SELECT * FROM orders WHERE status = 'active'",
            where_clause="created_at > '2024-01-01'",
            create_table=False,
            drop_target=True,
            chunk_column="id"
        )

        assert config.name == "orders"
        assert config.query == "SELECT * FROM orders WHERE status = 'active'"
        assert config.where_clause == "created_at > '2024-01-01'"
        assert config.create_table is False
        assert config.drop_target is True
        assert config.chunk_column == "id"


class TestMigrationBatchConfig:
    """Test MigrationBatchConfig class."""

    def test_default_batch_config(self):
        """Test default batch configuration."""
        config = MigrationBatchConfig()
        assert config.size == 100000
        assert config.parallel_workers == 4
        assert config.memory_limit_mb == 1024

    def test_custom_batch_config(self):
        """Test custom batch configuration."""
        config = MigrationBatchConfig(
            size=50000,
            parallel_workers=8,
            memory_limit_mb=2048
        )
        assert config.size == 50000
        assert config.parallel_workers == 8
        assert config.memory_limit_mb == 2048

    def test_batch_config_validation(self):
        """Test batch configuration validation."""
        # Test minimum values
        with pytest.raises(ValueError):
            MigrationBatchConfig(size=500)  # Below minimum

        with pytest.raises(ValueError):
            MigrationBatchConfig(parallel_workers=0)  # Below minimum

        with pytest.raises(ValueError):
            MigrationBatchConfig(memory_limit_mb=50)  # Below minimum