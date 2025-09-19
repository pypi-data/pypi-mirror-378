"""ClickHouse connection management."""

import logging
from typing import Any, Dict, List, Optional, Tuple, Union
from urllib.parse import urlparse

import clickhouse_connect
from clickhouse_connect.driver import Client
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from ..utils.exceptions import ConnectionError, QueryError

logger = logging.getLogger(__name__)


class ClickHouseConnection:
    """Manages ClickHouse database connections with retry logic and connection pooling."""

    def __init__(self, uri: str, **kwargs):
        """
        Initialize ClickHouse connection.

        Args:
            uri: ClickHouse connection URI (clickhouse://user:pass@host:port/database)
            **kwargs: Additional connection parameters
        """
        self.uri = uri
        self.connection_params = self._parse_uri(uri)
        self.connection_params.update(kwargs)
        self._client: Optional[Client] = None

    def _parse_uri(self, uri: str) -> Dict[str, Any]:
        """Parse ClickHouse URI into connection parameters."""
        try:
            parsed = urlparse(uri)

            if parsed.scheme not in ['clickhouse', 'clickhouses', 'http', 'https']:
                raise ValueError(f"Unsupported scheme: {parsed.scheme}")

            params = {
                'host': parsed.hostname or 'localhost',
                'port': parsed.port or (8443 if parsed.scheme in ['clickhouses', 'https'] else 8123),
                'username': parsed.username or 'default',
                'password': parsed.password or '',
                'database': parsed.path.lstrip('/') or 'default',
                'secure': parsed.scheme in ['clickhouses', 'https'],
            }

            # Parse query parameters
            if parsed.query:
                from urllib.parse import parse_qs
                query_params = parse_qs(parsed.query)
                for key, values in query_params.items():
                    if values:
                        # Convert common parameters
                        if key in ['compress', 'secure']:
                            params[key] = values[0].lower() in ('true', '1', 'yes')
                        elif key in ['connect_timeout', 'send_receive_timeout']:
                            params[key] = int(values[0])
                        else:
                            params[key] = values[0]

            return params

        except Exception as e:
            raise ConnectionError(f"Failed to parse URI '{uri}': {e}")

    @retry(
        retry=retry_if_exception_type((ConnectionError, OSError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def connect(self) -> Client:
        """Establish connection to ClickHouse with retry logic."""
        try:
            logger.info(f"Connecting to ClickHouse at {self.connection_params['host']}:{self.connection_params['port']}")

            self._client = clickhouse_connect.create_client(**self.connection_params)

            # Test connection with a simple query
            self._client.command('SELECT 1')

            logger.info("Successfully connected to ClickHouse")
            return self._client

        except Exception as e:
            logger.error(f"Failed to connect to ClickHouse: {e}")
            raise ConnectionError(f"Failed to connect to ClickHouse: {e}")

    @property
    def client(self) -> Client:
        """Get the ClickHouse client, connecting if necessary."""
        if not self._client:
            self.connect()
        return self._client

    def test_connection(self) -> bool:
        """Test if the connection is working."""
        try:
            self.client.command('SELECT 1')
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

    def execute_query(self, query: str, parameters: Optional[Dict] = None) -> Any:
        """Execute a query with error handling."""
        try:
            logger.debug(f"Executing query: {query[:100]}...")
            return self.client.query(query, parameters=parameters)
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise QueryError(f"Query execution failed: {e}")

    def execute_command(self, command: str, parameters: Optional[Dict] = None) -> Any:
        """Execute a command (non-query) with error handling."""
        try:
            logger.debug(f"Executing command: {command[:100]}...")
            return self.client.command(command, parameters=parameters)
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            raise QueryError(f"Command execution failed: {e}")

    def get_table_info(self, database: str, table: str) -> Dict[str, Any]:
        """Get detailed information about a table."""
        query = """
        SELECT
            name,
            type,
            default_kind,
            default_expression,
            comment,
            codec_expression,
            ttl_expression
        FROM system.columns
        WHERE database = %(database)s AND table = %(table)s
        ORDER BY position
        """

        result = self.execute_query(query, {'database': database, 'table': table})

        return {
            'columns': result.result_rows,
            'column_names': [row[0] for row in result.result_rows],
            'column_types': [row[1] for row in result.result_rows],
        }

    def get_create_table_statement(self, database: str, table: str) -> str:
        """Get the CREATE TABLE statement for a table."""
        query = f"SHOW CREATE TABLE `{database}`.`{table}`"
        result = self.execute_query(query)
        return result.result_rows[0][0] if result.result_rows else ""

    def get_table_count(self, database: str, table: str, where_clause: str = "") -> int:
        """Get the row count for a table."""
        query = f"SELECT COUNT(*) FROM `{database}`.`{table}`"
        if where_clause:
            query += f" WHERE {where_clause}"

        result = self.execute_query(query)
        return result.result_rows[0][0] if result.result_rows else 0

    def get_databases(self) -> List[str]:
        """Get list of databases."""
        query = "SELECT name FROM system.databases WHERE name NOT IN ('system', 'information_schema', 'INFORMATION_SCHEMA')"
        result = self.execute_query(query)
        return [row[0] for row in result.result_rows]

    def get_tables(self, database: str) -> List[str]:
        """Get list of tables in a database."""
        query = "SELECT name FROM system.tables WHERE database = %(database)s"
        result = self.execute_query(query, {'database': database})
        return [row[0] for row in result.result_rows]

    def insert_data_batch(self, database: str, table: str, data: List[Tuple], column_names: Optional[List[str]] = None):
        """Insert data in batch."""
        try:
            if column_names:
                self.client.insert(f"`{database}`.`{table}`", data, column_names=column_names)
            else:
                self.client.insert(f"`{database}`.`{table}`", data)
        except Exception as e:
            logger.error(f"Batch insert failed: {e}")
            raise QueryError(f"Batch insert failed: {e}")

    def close(self):
        """Close the connection."""
        if self._client:
            try:
                self._client.close()
                logger.info("ClickHouse connection closed")
            except Exception as e:
                logger.warning(f"Error closing connection: {e}")
            finally:
                self._client = None

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()