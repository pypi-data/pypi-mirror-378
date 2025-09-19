"""Tests for CLI functionality."""

import tempfile
import os
from unittest.mock import Mock, patch
from pathlib import Path

import pytest
from click.testing import CliRunner

from clickhouse_migrator.cli import cli, setup_logging


class TestCLI:
    """Test CLI functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_cli_version(self):
        """Test CLI version display."""
        result = self.runner.invoke(cli, ['--version'])
        assert result.exit_code == 0
        assert "0.1.0" in result.output

    def test_cli_help(self):
        """Test CLI help display."""
        result = self.runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert "ClickHouse Migrator" in result.output
        assert "migrate" in result.output

    def test_migrate_help(self):
        """Test migrate command help."""
        result = self.runner.invoke(cli, ['migrate', '--help'])
        assert result.exit_code == 0
        assert "SOURCE_URI" in result.output
        assert "TARGET_URI" in result.output

    def test_list_tables_help(self):
        """Test list-tables command help."""
        result = self.runner.invoke(cli, ['list-tables', '--help'])
        assert result.exit_code == 0
        assert "List tables" in result.output

    @patch('clickhouse_migrator.cli.ClickHouseMigrator')
    def test_migrate_basic(self, mock_migrator_class):
        """Test basic migration command."""
        mock_migrator = Mock()
        mock_migrator.run_migration.return_value = True
        mock_migrator_class.return_value = mock_migrator

        result = self.runner.invoke(cli, [
            'migrate',
            'clickhouse://user:pass@source:8123/db',
            'clickhouse://user:pass@target:8123/db',
            '--dry-run'
        ], input='y\n')

        assert result.exit_code == 0
        mock_migrator.run_migration.assert_called_once()

    @patch('clickhouse_migrator.cli.ClickHouseMigrator')
    def test_migrate_with_tables(self, mock_migrator_class):
        """Test migration with specific tables."""
        mock_migrator = Mock()
        mock_migrator.run_migration.return_value = True
        mock_migrator_class.return_value = mock_migrator

        result = self.runner.invoke(cli, [
            'migrate',
            'clickhouse://user:pass@source:8123/db',
            'clickhouse://user:pass@target:8123/db',
            '--tables', 'users',
            '--tables', 'orders',
            '--batch-size', '50000',
            '--workers', '2',
            '--dry-run'
        ])

        assert result.exit_code == 0
        mock_migrator.run_migration.assert_called_once()

        # Verify configuration was created correctly
        call_args = mock_migrator_class.call_args
        config = call_args[0][0]  # First positional argument
        assert config.batch.size == 50000
        assert config.batch.parallel_workers == 2
        assert len(config.tables) == 2

    @patch('clickhouse_migrator.cli.ClickHouseMigrator')
    def test_migrate_with_query(self, mock_migrator_class):
        """Test migration with custom query."""
        mock_migrator = Mock()
        mock_migrator.run_migration.return_value = True
        mock_migrator_class.return_value = mock_migrator

        result = self.runner.invoke(cli, [
            'migrate',
            'clickhouse://user:pass@source:8123/db',
            'clickhouse://user:pass@target:8123/db',
            '--query', 'SELECT * FROM users WHERE active = 1',
            '--dry-run'
        ])

        assert result.exit_code == 0

        call_args = mock_migrator_class.call_args
        config = call_args[0][0]
        assert len(config.tables) == 1
        assert config.tables[0].query == 'SELECT * FROM users WHERE active = 1'

    @patch('clickhouse_migrator.cli.MigrationConfig.from_file')
    @patch('clickhouse_migrator.cli.ClickHouseMigrator')
    def test_migrate_with_config_file(self, mock_migrator_class, mock_from_file):
        """Test migration with configuration file."""
        mock_config = Mock()
        mock_config.validate_connections.return_value = []
        mock_from_file.return_value = mock_config

        mock_migrator = Mock()
        mock_migrator.run_migration.return_value = True
        mock_migrator_class.return_value = mock_migrator

        # Create temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_path = f.name

        try:
            result = self.runner.invoke(cli, [
                'migrate',
                'clickhouse://user:pass@source:8123/db',
                'clickhouse://user:pass@target:8123/db',
                '--config', config_path,
                '--dry-run'
            ])

            assert result.exit_code == 0
            mock_from_file.assert_called_once_with(config_path)
        finally:
            if os.path.exists(config_path):
                os.unlink(config_path)

    def test_migrate_missing_arguments(self):
        """Test migration with missing required arguments."""
        result = self.runner.invoke(cli, ['migrate'])
        assert result.exit_code != 0
        assert "Missing argument" in result.output

    def test_migrate_cancel(self):
        """Test canceling migration when prompted."""
        result = self.runner.invoke(cli, [
            'migrate',
            'clickhouse://user:pass@source:8123/db',
            'clickhouse://user:pass@target:8123/db'
        ], input='n\n')

        assert result.exit_code == 0
        assert "cancelled" in result.output

    @patch('clickhouse_migrator.cli.ClickHouseMigrator')
    def test_migrate_failure(self, mock_migrator_class):
        """Test migration failure."""
        mock_migrator = Mock()
        mock_migrator.run_migration.return_value = False
        mock_migrator_class.return_value = mock_migrator

        result = self.runner.invoke(cli, [
            'migrate',
            'clickhouse://user:pass@source:8123/db',
            'clickhouse://user:pass@target:8123/db',
            '--dry-run'
        ])

        assert result.exit_code == 0  # CLI doesn't exit with error code for migration failures
        mock_migrator.run_migration.assert_called_once()

    @patch('clickhouse_migrator.core.connection.ClickHouseConnection')
    def test_list_tables_success(self, mock_connection_class):
        """Test successful table listing."""
        mock_conn = Mock()
        mock_conn.get_databases.return_value = ['db1', 'db2']
        mock_conn.get_tables.return_value = ['users', 'orders']
        mock_conn.get_table_count.return_value = 1000
        mock_connection_class.return_value = mock_conn

        result = self.runner.invoke(cli, [
            'list-tables',
            'clickhouse://user:pass@host:8123/db'
        ])

        assert result.exit_code == 0
        assert "users" in result.output
        assert "orders" in result.output
        mock_conn.connect.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('clickhouse_migrator.core.connection.ClickHouseConnection')
    def test_list_tables_specific_database(self, mock_connection_class):
        """Test listing tables for specific database."""
        mock_conn = Mock()
        mock_conn.get_tables.return_value = ['table1', 'table2']
        mock_conn.get_table_count.return_value = 500
        mock_connection_class.return_value = mock_conn

        result = self.runner.invoke(cli, [
            'list-tables',
            'clickhouse://user:pass@host:8123/db',
            '--database', 'specific_db'
        ])

        assert result.exit_code == 0
        mock_conn.get_tables.assert_called_with('specific_db')

    @patch('clickhouse_migrator.core.connection.ClickHouseConnection')
    def test_list_tables_connection_error(self, mock_connection_class):
        """Test list-tables with connection error."""
        mock_connection_class.side_effect = Exception("Connection failed")

        result = self.runner.invoke(cli, [
            'list-tables',
            'clickhouse://user:pass@host:8123/db'
        ])

        assert result.exit_code == 0
        assert "Error" in result.output

    @patch('clickhouse_migrator.core.connection.ClickHouseConnection')
    def test_inspect_table_success(self, mock_connection_class):
        """Test successful table inspection."""
        mock_conn = Mock()
        mock_conn.connection_params = {'database': 'test_db'}
        mock_conn.get_table_info.return_value = {
            'columns': [
                ('id', 'UInt32', '', '', '', '', ''),
                ('name', 'String', '', '', '', '', '')
            ],
            'column_names': ['id', 'name'],
            'column_types': ['UInt32', 'String']
        }
        mock_conn.get_table_count.return_value = 1000

        mock_result = Mock()
        mock_result.result_rows = [(1, 'Alice'), (2, 'Bob')]
        mock_conn.execute_query.return_value = mock_result

        mock_connection_class.return_value = mock_conn

        result = self.runner.invoke(cli, [
            'inspect-table',
            'clickhouse://user:pass@host:8123/db',
            'users'
        ])

        assert result.exit_code == 0
        assert "users" in result.output
        assert "1,000" in result.output  # Row count
        mock_conn.connect.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('clickhouse_migrator.core.connection.ClickHouseConnection')
    def test_inspect_table_error(self, mock_connection_class):
        """Test inspect-table with error."""
        mock_connection_class.side_effect = Exception("Table not found")

        result = self.runner.invoke(cli, [
            'inspect-table',
            'clickhouse://user:pass@host:8123/db',
            'nonexistent'
        ])

        assert result.exit_code == 0
        assert "Error" in result.output

    @patch('clickhouse_migrator.core.connection.ClickHouseConnection')
    def test_test_connection_success(self, mock_connection_class):
        """Test successful connection test."""
        mock_source_conn = Mock()
        mock_source_conn.test_connection.return_value = True
        mock_source_conn.get_databases.return_value = ['db1', 'db2']

        mock_target_conn = Mock()
        mock_target_conn.test_connection.return_value = True
        mock_target_conn.get_databases.return_value = ['db1']

        mock_connection_class.side_effect = [mock_source_conn, mock_target_conn]

        result = self.runner.invoke(cli, [
            'test-connection',
            'clickhouse://user:pass@source:8123/db',
            'clickhouse://user:pass@target:8123/db'
        ])

        assert result.exit_code == 0
        assert "successful" in result.output
        mock_source_conn.test_connection.assert_called_once()
        mock_target_conn.test_connection.assert_called_once()

    @patch('clickhouse_migrator.core.connection.ClickHouseConnection')
    def test_test_connection_failure(self, mock_connection_class):
        """Test connection test failure."""
        mock_conn = Mock()
        mock_conn.test_connection.return_value = False
        mock_connection_class.return_value = mock_conn

        result = self.runner.invoke(cli, [
            'test-connection',
            'clickhouse://user:pass@source:8123/db',
            'clickhouse://user:pass@target:8123/db'
        ])

        assert result.exit_code == 0
        assert "failed" in result.output

    def test_generate_config_success(self):
        """Test successful configuration generation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, 'test-config.yaml')

            result = self.runner.invoke(cli, [
                'generate-config',
                '--output', config_path
            ])

            assert result.exit_code == 0
            assert os.path.exists(config_path)

            # Verify config file contains expected content
            with open(config_path, 'r') as f:
                content = f.read()
                assert "source:" in content
                assert "target:" in content
                assert "tables:" in content
                assert "batch:" in content

    def test_generate_config_default_output(self):
        """Test configuration generation with default output."""
        with tempfile.TemporaryDirectory():
            # Change to temp directory
            original_cwd = os.getcwd()
            try:
                os.chdir(tempfile.gettempdir())

                result = self.runner.invoke(cli, ['generate-config'])

                assert result.exit_code == 0

                # Clean up generated file
                default_path = "migration-config.yaml"
                if os.path.exists(default_path):
                    os.unlink(default_path)
            finally:
                os.chdir(original_cwd)


class TestSetupLogging:
    """Test logging setup functionality."""

    def test_setup_logging_default(self):
        """Test default logging setup."""
        setup_logging()
        # Should not raise any exceptions

    def test_setup_logging_with_level(self):
        """Test logging setup with specific level."""
        setup_logging(level="DEBUG")
        # Should not raise any exceptions

    def test_setup_logging_with_file(self):
        """Test logging setup with file output."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            log_file = f.name

        try:
            setup_logging(level="INFO", log_file=log_file)
            assert os.path.exists(log_file)
        finally:
            if os.path.exists(log_file):
                os.unlink(log_file)