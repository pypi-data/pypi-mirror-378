"""Custom exceptions for ClickHouse migration."""


class MigrationError(Exception):
    """Base exception for migration errors."""
    pass


class ConnectionError(MigrationError):
    """Exception raised when connection to ClickHouse fails."""
    pass


class QueryError(MigrationError):
    """Exception raised when query execution fails."""
    pass


class ConfigurationError(MigrationError):
    """Exception raised when configuration is invalid."""
    pass


class ValidationError(MigrationError):
    """Exception raised when data validation fails."""
    pass


class CheckpointError(MigrationError):
    """Exception raised when checkpoint operations fail."""
    pass


class SchemaError(MigrationError):
    """Exception raised when schema operations fail."""
    pass


class DataIntegrityError(MigrationError):
    """Exception raised when data integrity checks fail."""
    pass