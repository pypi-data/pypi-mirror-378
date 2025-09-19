"""Tests for ClickHouse connection handling."""

import pytest
from unittest.mock import Mock, patch, MagicMock

from clickhouse_migrator.core.connection import ClickHouseConnection
from clickhouse_migrator.utils.exceptions import ConnectionError, QueryError


class TestClickHouseConnection:
    """Test ClickHouseConnection class."""

    def test_parse_uri_basic(self):
        """Test basic URI parsing."""
        conn = ClickHouseConnection("clickhouse://user:pass@localhost:8123/test")
        params = conn.connection_params

        assert params['host'] == 'localhost'
        assert params['port'] == 8123
        assert params['username'] == 'user'
        assert params['password'] == 'pass'
        assert params['database'] == 'test'
        assert params['secure'] is False

    def test_parse_uri_secure(self):
        """Test secure URI parsing."""
        conn = ClickHouseConnection("clickhouses://user:pass@host:8443/db")
        params = conn.connection_params

        assert params['host'] == 'host'
        assert params['port'] == 8443
        assert params['username'] == 'user'
        assert params['password'] == 'pass'
        assert params['database'] == 'db'
        assert params['secure'] is True

    def test_parse_uri_https(self):
        """Test HTTPS URI parsing."""
        conn = ClickHouseConnection("https://user:pass@cloud.clickhouse.com:8443/mydb")
        params = conn.connection_params

        assert params['host'] == 'cloud.clickhouse.com'
        assert params['port'] == 8443
        assert params['username'] == 'user'
        assert params['password'] == 'pass'
        assert params['database'] == 'mydb'
        assert params['secure'] is True

    def test_parse_uri_defaults(self):
        """Test URI parsing with default values."""
        conn = ClickHouseConnection("clickhouse://")
        params = conn.connection_params

        assert params['host'] == 'localhost'
        assert params['port'] == 8123
        assert params['username'] == 'default'
        assert params['password'] == ''
        assert params['database'] == 'default'
        assert params['secure'] is False

    def test_parse_uri_query_params(self):
        """Test URI parsing with query parameters."""
        uri = "clickhouse://user:pass@host:8123/db?compress=true&connect_timeout=60"
        conn = ClickHouseConnection(uri)
        params = conn.connection_params

        assert params['compress'] is True
        assert params['connect_timeout'] == 60

    def test_parse_uri_invalid_scheme(self):
        """Test parsing invalid URI scheme."""
        with pytest.raises(ConnectionError):
            ClickHouseConnection("invalid://user:pass@host:8123/db")

    @patch('clickhouse_migrator.core.connection.clickhouse_connect.create_client')
    def test_connect_success(self, mock_create_client):
        """Test successful connection."""
        mock_client = Mock()
        mock_create_client.return_value = mock_client

        conn = ClickHouseConnection("clickhouse://user:pass@localhost:8123/test")
        client = conn.connect()

        assert client == mock_client
        mock_create_client.assert_called_once()
        mock_client.command.assert_called_once_with('SELECT 1')

    @patch('clickhouse_migrator.core.connection.clickhouse_connect.create_client')
    def test_connect_failure(self, mock_create_client):
        """Test connection failure."""
        mock_create_client.side_effect = Exception("Connection failed")

        conn = ClickHouseConnection("clickhouse://user:pass@localhost:8123/test")

        with pytest.raises(ConnectionError, match="Failed to connect to ClickHouse"):
            conn.connect()

    @patch('clickhouse_migrator.core.connection.clickhouse_connect.create_client')
    def test_test_connection_success(self, mock_create_client):
        """Test successful connection test."""
        mock_client = Mock()
        mock_create_client.return_value = mock_client

        conn = ClickHouseConnection("clickhouse://user:pass@localhost:8123/test")
        result = conn.test_connection()

        assert result is True

    @patch('clickhouse_migrator.core.connection.clickhouse_connect.create_client')
    def test_test_connection_failure(self, mock_create_client):
        """Test connection test failure."""
        mock_client = Mock()
        mock_client.command.side_effect = Exception("Connection test failed")
        mock_create_client.return_value = mock_client

        conn = ClickHouseConnection("clickhouse://user:pass@localhost:8123/test")
        result = conn.test_connection()

        assert result is False

    def test_execute_query_success(self):
        """Test successful query execution."""
        mock_client = Mock()
        mock_result = Mock()
        mock_result.result_rows = [('test_value',)]
        mock_client.query.return_value = mock_result

        conn = ClickHouseConnection("clickhouse://user:pass@localhost:8123/test")
        conn._client = mock_client

        result = conn.execute_query("SELECT 'test_value'")

        assert result == mock_result
        mock_client.query.assert_called_once_with("SELECT 'test_value'", parameters=None)

    def test_execute_query_failure(self):
        """Test query execution failure."""
        mock_client = Mock()
        mock_client.query.side_effect = Exception("Query failed")

        conn = ClickHouseConnection("clickhouse://user:pass@localhost:8123/test")
        conn._client = mock_client

        with pytest.raises(QueryError, match="Query execution failed"):
            conn.execute_query("SELECT invalid")

    def test_execute_command_success(self):
        """Test successful command execution."""
        mock_client = Mock()
        mock_client.command.return_value = "OK"

        conn = ClickHouseConnection("clickhouse://user:pass@localhost:8123/test")
        conn._client = mock_client

        result = conn.execute_command("CREATE TABLE test (id UInt32)")

        assert result == "OK"
        mock_client.command.assert_called_once_with("CREATE TABLE test (id UInt32)", parameters=None)

    def test_execute_command_failure(self):
        """Test command execution failure."""
        mock_client = Mock()
        mock_client.command.side_effect = Exception("Command failed")

        conn = ClickHouseConnection("clickhouse://user:pass@localhost:8123/test")
        conn._client = mock_client

        with pytest.raises(QueryError, match="Command execution failed"):
            conn.execute_command("INVALID COMMAND")

    def test_get_table_info(self):
        """Test getting table information."""
        mock_client = Mock()
        mock_result = Mock()
        mock_result.result_rows = [
            ('id', 'UInt32', '', '', '', '', ''),
            ('name', 'String', '', '', '', '', ''),
            ('created_at', 'DateTime', '', '', '', '', '')
        ]
        mock_client.query.return_value = mock_result

        conn = ClickHouseConnection("clickhouse://user:pass@localhost:8123/test")
        conn._client = mock_client

        table_info = conn.get_table_info("test_db", "users")

        assert table_info['columns'] == mock_result.result_rows
        assert table_info['column_names'] == ['id', 'name', 'created_at']
        assert table_info['column_types'] == ['UInt32', 'String', 'DateTime']

    def test_get_create_table_statement(self):
        """Test getting CREATE TABLE statement."""
        mock_client = Mock()
        mock_result = Mock()
        mock_result.result_rows = [("CREATE TABLE test.users (id UInt32, name String) ENGINE = MergeTree()",)]
        mock_client.query.return_value = mock_result

        conn = ClickHouseConnection("clickhouse://user:pass@localhost:8123/test")
        conn._client = mock_client

        create_statement = conn.get_create_table_statement("test_db", "users")

        assert create_statement == "CREATE TABLE test.users (id UInt32, name String) ENGINE = MergeTree()"

    def test_get_table_count(self):
        """Test getting table row count."""
        mock_client = Mock()
        mock_result = Mock()
        mock_result.result_rows = [(12345,)]
        mock_client.query.return_value = mock_result

        conn = ClickHouseConnection("clickhouse://user:pass@localhost:8123/test")
        conn._client = mock_client

        count = conn.get_table_count("test_db", "users")

        assert count == 12345

    def test_get_table_count_with_where(self):
        """Test getting table row count with WHERE clause."""
        mock_client = Mock()
        mock_result = Mock()
        mock_result.result_rows = [(500,)]
        mock_client.query.return_value = mock_result

        conn = ClickHouseConnection("clickhouse://user:pass@localhost:8123/test")
        conn._client = mock_client

        count = conn.get_table_count("test_db", "users", "active = 1")

        assert count == 500
        # Verify the WHERE clause was included in the query
        mock_client.query.assert_called_once()
        call_args = mock_client.query.call_args[0][0]
        assert "WHERE active = 1" in call_args

    def test_get_databases(self):
        """Test getting database list."""
        mock_client = Mock()
        mock_result = Mock()
        mock_result.result_rows = [('db1',), ('db2',), ('db3',)]
        mock_client.query.return_value = mock_result

        conn = ClickHouseConnection("clickhouse://user:pass@localhost:8123/test")
        conn._client = mock_client

        databases = conn.get_databases()

        assert databases == ['db1', 'db2', 'db3']

    def test_get_tables(self):
        """Test getting table list."""
        mock_client = Mock()
        mock_result = Mock()
        mock_result.result_rows = [('users',), ('orders',), ('products',)]
        mock_client.query.return_value = mock_result

        conn = ClickHouseConnection("clickhouse://user:pass@localhost:8123/test")
        conn._client = mock_client

        tables = conn.get_tables("test_db")

        assert tables == ['users', 'orders', 'products']

    def test_insert_data_batch_success(self):
        """Test successful batch data insertion."""
        mock_client = Mock()
        conn = ClickHouseConnection("clickhouse://user:pass@localhost:8123/test")
        conn._client = mock_client

        data = [(1, 'Alice'), (2, 'Bob'), (3, 'Charlie')]
        column_names = ['id', 'name']

        conn.insert_data_batch("test_db", "users", data, column_names)

        mock_client.insert.assert_called_once_with("`test_db`.`users`", data, column_names=column_names)

    def test_insert_data_batch_without_columns(self):
        """Test batch data insertion without column names."""
        mock_client = Mock()
        conn = ClickHouseConnection("clickhouse://user:pass@localhost:8123/test")
        conn._client = mock_client

        data = [(1, 'Alice'), (2, 'Bob')]

        conn.insert_data_batch("test_db", "users", data)

        mock_client.insert.assert_called_once_with("`test_db`.`users`", data)

    def test_insert_data_batch_failure(self):
        """Test batch data insertion failure."""
        mock_client = Mock()
        mock_client.insert.side_effect = Exception("Insert failed")

        conn = ClickHouseConnection("clickhouse://user:pass@localhost:8123/test")
        conn._client = mock_client

        data = [(1, 'Alice')]

        with pytest.raises(QueryError, match="Batch insert failed"):
            conn.insert_data_batch("test_db", "users", data)

    def test_close_connection(self):
        """Test closing connection."""
        mock_client = Mock()
        conn = ClickHouseConnection("clickhouse://user:pass@localhost:8123/test")
        conn._client = mock_client

        conn.close()

        mock_client.close.assert_called_once()
        assert conn._client is None

    def test_close_connection_with_error(self):
        """Test closing connection with error."""
        mock_client = Mock()
        mock_client.close.side_effect = Exception("Close error")

        conn = ClickHouseConnection("clickhouse://user:pass@localhost:8123/test")
        conn._client = mock_client

        # Should not raise exception, just log warning
        conn.close()

        assert conn._client is None

    def test_context_manager(self):
        """Test context manager functionality."""
        mock_client = Mock()

        with patch.object(ClickHouseConnection, 'connect', return_value=mock_client):
            with ClickHouseConnection("clickhouse://user:pass@localhost:8123/test") as conn:
                assert conn._client == mock_client

            # Connection should be closed after exiting context
            mock_client.close.assert_called_once()