"""Core migration engine for ClickHouse data migration."""

import logging
import math
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional, Tuple

from rich.console import Console

from .config import MigrationConfig
from .connection import ClickHouseConnection
from ..utils.exceptions import MigrationError, SchemaError, DataIntegrityError
from ..utils.progress import MigrationProgress
from ..utils.schema_transformer import ClickHouseEngineTransformer

logger = logging.getLogger(__name__)


class ClickHouseMigrator:
    """Main migration engine for ClickHouse data transfer."""

    def __init__(self, config: MigrationConfig, console: Optional[Console] = None):
        """
        Initialize the migrator.

        Args:
            config: Migration configuration
            console: Rich console for output (optional)
        """
        self.config = config
        self.console = console or Console()
        self.progress = MigrationProgress(console=self.console)

        # Initialize connections
        self.source_conn = ClickHouseConnection(config.source.uri)
        self.target_conn = ClickHouseConnection(config.target.uri)

        # Initialize schema transformer
        self.schema_transformer = ClickHouseEngineTransformer(config.engine_transformation_mode)

        # Migration state
        self._migration_stats = {
            "total_tables": 0,
            "total_rows": 0,
            "migrated_rows": 0,
            "failed_tables": [],
            "start_time": None,
            "end_time": None,
        }

    def validate_connections(self) -> bool:
        """Validate both source and target connections."""
        try:
            logger.info("Validating source connection...")
            if not self.source_conn.test_connection():
                raise MigrationError("Source connection validation failed")

            logger.info("Validating target connection...")
            if not self.target_conn.test_connection():
                raise MigrationError("Target connection validation failed")

            logger.info("All connections validated successfully")
            return True

        except Exception as e:
            logger.error(f"Connection validation failed: {e}")
            return False

    def discover_tables(self) -> List[str]:
        """Discover tables to migrate from source database."""
        try:
            # If specific tables are configured, use those
            if self.config.tables:
                return [table.name for table in self.config.tables if table.name != "custom_query"]

            # Otherwise, discover all tables from source
            source_db = self.source_conn.connection_params.get('database', 'default')
            all_tables = self.source_conn.get_tables(source_db)

            # Filter out excluded tables
            if self.config.exclude_tables:
                all_tables = [table for table in all_tables if table not in self.config.exclude_tables]

            logger.info(f"Discovered {len(all_tables)} tables to migrate: {all_tables}")
            return all_tables

        except Exception as e:
            logger.error(f"Failed to discover tables: {e}")
            raise MigrationError(f"Table discovery failed: {e}")

    def migrate_schema(self, table_name: str) -> bool:
        """Migrate table schema from source to target."""
        try:
            logger.info(f"Migrating schema for table: {table_name}")

            source_db = self.source_conn.connection_params.get('database', 'default')
            target_db = self.target_conn.connection_params.get('database', 'default')

            # Get CREATE TABLE statement from source
            create_statement = self.source_conn.get_create_table_statement(source_db, table_name)
            if not create_statement:
                raise SchemaError(f"Could not retrieve CREATE TABLE statement for {table_name}")

            # Modify the CREATE TABLE statement for target database
            # Replace database name in the statement
            modified_statement = create_statement.replace(f"`{source_db}`.`{table_name}`", f"`{target_db}`.`{table_name}`")

            # Transform engines for compatibility (e.g., SharedMergeTree -> MergeTree)
            if self.config.transform_engines and self.schema_transformer.is_transformation_needed(modified_statement, self.target_conn):
                logger.info(f"Schema transformation needed for table {table_name}")
                modified_statement = self.schema_transformer.transform_create_statement(modified_statement)
                logger.info(f"Schema transformed for compatibility")

            # Check if we should drop the target table first
            table_config = self._get_table_config(table_name)
            if table_config and table_config.drop_target:
                drop_statement = f"DROP TABLE IF EXISTS `{target_db}`.`{table_name}`"
                self.target_conn.execute_command(drop_statement)
                logger.info(f"Dropped existing table {table_name}")

            # Execute CREATE TABLE on target
            self.target_conn.execute_command(modified_statement)
            logger.info(f"Schema migrated successfully for table: {table_name}")

            return True

        except Exception as e:
            logger.error(f"Schema migration failed for table {table_name}: {e}")
            raise SchemaError(f"Schema migration failed for {table_name}: {e}")

    def _get_table_config(self, table_name: str):
        """Get configuration for a specific table."""
        for table_config in self.config.tables:
            if table_config.name == table_name:
                return table_config
        return None

    def _build_data_query(self, table_name: str, offset: int = 0, limit: Optional[int] = None) -> str:
        """Build query to select data from source table."""
        table_config = self._get_table_config(table_name)
        source_db = self.source_conn.connection_params.get('database', 'default')

        # Use custom query if specified
        if table_config and table_config.query:
            query = table_config.query
            # Add LIMIT and OFFSET if not already present
            if limit and "LIMIT" not in query.upper():
                query += f" LIMIT {limit}"
            if offset and "OFFSET" not in query.upper():
                query += f" OFFSET {offset}"
            return query

        # Build standard SELECT query
        query = f"SELECT * FROM `{source_db}`.`{table_name}`"

        # Add WHERE clause if specified
        if table_config and table_config.where_clause:
            query += f" WHERE {table_config.where_clause}"

        # Add chunking based on a column if specified
        if table_config and table_config.chunk_column:
            # This is a simplified chunking approach
            # In production, you might want more sophisticated chunking
            query += f" ORDER BY `{table_config.chunk_column}`"

        # Add LIMIT and OFFSET for batching
        if limit:
            query += f" LIMIT {limit}"
        if offset:
            query += f" OFFSET {offset}"

        return query

    def migrate_table_data(self, table_name: str) -> bool:
        """Migrate data for a single table."""
        try:
            logger.info(f"Starting data migration for table: {table_name}")

            source_db = self.source_conn.connection_params.get('database', 'default')
            target_db = self.target_conn.connection_params.get('database', 'default')

            # Get table information
            table_info = self.source_conn.get_table_info(source_db, table_name)
            column_names = table_info['column_names']

            # Get total row count
            table_config = self._get_table_config(table_name)
            where_clause = table_config.where_clause if table_config else ""
            total_rows = self.source_conn.get_table_count(source_db, table_name, where_clause)

            if total_rows == 0:
                logger.info(f"Table {table_name} is empty, skipping data migration")
                self.progress.add_table(table_name, 0)
                self.progress.complete_table(table_name, success=True)
                return True

            logger.info(f"Table {table_name} has {total_rows:,} rows to migrate")

            # Add to progress tracking
            self.progress.add_table(table_name, total_rows, self.config.batch.size)

            # Migrate data in batches
            batch_size = self.config.batch.size
            total_batches = math.ceil(total_rows / batch_size)
            migrated_rows = 0

            for batch_num in range(total_batches):
                offset = batch_num * batch_size
                limit = min(batch_size, total_rows - offset)

                try:
                    # Fetch batch from source
                    query = self._build_data_query(table_name, offset, limit)
                    logger.debug(f"Executing batch query: {query}")

                    result = self.source_conn.execute_query(query)
                    batch_data = result.result_rows

                    if not batch_data:
                        logger.warning(f"Empty batch {batch_num + 1}/{total_batches} for table {table_name}")
                        continue

                    # Insert batch into target
                    self.target_conn.insert_data_batch(
                        target_db,
                        table_name,
                        batch_data,
                        column_names
                    )

                    migrated_rows += len(batch_data)
                    self.progress.update_table(table_name, migrated_rows)

                    # Create checkpoint periodically
                    if migrated_rows % self.config.progress.checkpoint_interval == 0:
                        checkpoint_file = self.config.get_checkpoint_file()
                        self.progress.create_checkpoint(checkpoint_file)

                    logger.debug(f"Migrated batch {batch_num + 1}/{total_batches} "
                               f"({len(batch_data)} rows) for table {table_name}")

                except Exception as e:
                    logger.error(f"Failed to migrate batch {batch_num + 1} for table {table_name}: {e}")
                    self.progress.complete_table(table_name, success=False, error_message=str(e))
                    return False

            # Verify data integrity if enabled
            if self.config.verify_data:
                if not self._verify_table_data(table_name, total_rows):
                    self.progress.complete_table(table_name, success=False, error_message="Data verification failed")
                    return False

            self.progress.complete_table(table_name, success=True)
            logger.info(f"Successfully migrated {migrated_rows:,} rows for table: {table_name}")

            return True

        except Exception as e:
            logger.error(f"Data migration failed for table {table_name}: {e}")
            self.progress.complete_table(table_name, success=False, error_message=str(e))
            return False

    def _verify_table_data(self, table_name: str, expected_count: int) -> bool:
        """Verify data integrity after migration."""
        try:
            logger.info(f"Verifying data integrity for table: {table_name}")

            target_db = self.target_conn.connection_params.get('database', 'default')
            actual_count = self.target_conn.get_table_count(target_db, table_name)

            if actual_count != expected_count:
                raise DataIntegrityError(
                    f"Row count mismatch for table {table_name}: "
                    f"expected {expected_count}, got {actual_count}"
                )

            logger.info(f"Data verification passed for table: {table_name}")
            return True

        except Exception as e:
            logger.error(f"Data verification failed for table {table_name}: {e}")
            return False

    def migrate_tables_parallel(self, table_names: List[str]) -> Dict[str, bool]:
        """Migrate multiple tables in parallel."""
        results = {}
        max_workers = self.config.batch.parallel_workers

        logger.info(f"Starting parallel migration of {len(table_names)} tables with {max_workers} workers")

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit migration tasks
            future_to_table = {
                executor.submit(self.migrate_table_data, table_name): table_name
                for table_name in table_names
            }

            # Process completed tasks
            for future in as_completed(future_to_table):
                table_name = future_to_table[future]
                try:
                    success = future.result()
                    results[table_name] = success
                    if not success:
                        self._migration_stats["failed_tables"].append(table_name)
                except Exception as e:
                    logger.error(f"Parallel migration failed for table {table_name}: {e}")
                    results[table_name] = False
                    self._migration_stats["failed_tables"].append(table_name)

        return results

    def run_migration(self) -> bool:
        """Run the complete migration process."""
        try:
            logger.info("Starting ClickHouse migration...")
            self._migration_stats["start_time"] = time.time()

            # Validate configuration
            config_errors = self.config.validate_connections()
            if config_errors:
                for error in config_errors:
                    logger.error(f"Configuration error: {error}")
                return False

            # Validate connections
            if not self.validate_connections():
                return False

            # Load checkpoint if resuming
            if self.config.resume:
                checkpoint_file = self.config.get_checkpoint_file()
                if self.progress.load_checkpoint(checkpoint_file):
                    logger.info("Resumed from checkpoint")

            # Discover tables to migrate
            table_names = self.discover_tables()
            if not table_names:
                logger.warning("No tables found to migrate")
                return True

            self._migration_stats["total_tables"] = len(table_names)

            # Start progress tracking
            with self.progress:
                # Migrate schemas first if enabled
                if self.config.migrate_schema:
                    logger.info("Migrating table schemas...")
                    for table_name in table_names:
                        table_config = self._get_table_config(table_name)
                        if not table_config or table_config.create_table:
                            try:
                                self.migrate_schema(table_name)
                            except Exception as e:
                                logger.error(f"Schema migration failed for {table_name}: {e}")
                                if not self.config.dry_run:
                                    self._migration_stats["failed_tables"].append(table_name)
                                    continue

                # Migrate data if enabled and not dry run
                if self.config.migrate_data and not self.config.dry_run:
                    logger.info("Migrating table data...")

                    if self.config.batch.parallel_workers > 1:
                        # Parallel migration
                        migration_results = self.migrate_tables_parallel(table_names)
                    else:
                        # Sequential migration
                        migration_results = {}
                        for table_name in table_names:
                            migration_results[table_name] = self.migrate_table_data(table_name)

                    # Update stats
                    successful_tables = sum(1 for success in migration_results.values() if success)
                    self._migration_stats["migrated_tables"] = successful_tables

                # Final checkpoint
                checkpoint_file = self.config.get_checkpoint_file()
                self.progress.create_checkpoint(checkpoint_file)

                # Display final summary
                self.progress.display_summary_table()

            self._migration_stats["end_time"] = time.time()

            # Print final summary
            self._print_final_summary()

            # Return success if no tables failed
            return len(self._migration_stats["failed_tables"]) == 0

        except Exception as e:
            logger.error(f"Migration failed with error: {e}")
            return False

        finally:
            # Close connections
            self.source_conn.close()
            self.target_conn.close()

    def _print_final_summary(self):
        """Print final migration summary."""
        stats = self._migration_stats
        elapsed_time = stats["end_time"] - stats["start_time"] if stats["start_time"] and stats["end_time"] else 0

        self.console.print("\n" + "="*60)
        self.console.print("[bold green]MIGRATION COMPLETED[/bold green]")
        self.console.print("="*60)

        summary = self.progress.get_summary()

        self.console.print(f"[blue]Total Tables:[/blue] {summary['total_tables']}")
        self.console.print(f"[green]Completed:[/green] {summary['completed_tables']}")
        self.console.print(f"[red]Failed:[/red] {summary['failed_tables']}")
        self.console.print(f"[yellow]Pending:[/yellow] {summary['pending_tables']}")
        self.console.print(f"[blue]Total Rows Processed:[/blue] {summary['processed_rows']:,}")
        self.console.print(f"[blue]Total Bytes Processed:[/blue] {summary['total_bytes_processed']:,}")
        self.console.print(f"[blue]Average Rate:[/blue] {summary['overall_rate_rows_per_second']:.0f} rows/sec")
        self.console.print(f"[blue]Total Time:[/blue] {elapsed_time:.2f} seconds")

        if stats["failed_tables"]:
            self.console.print(f"\n[red]Failed Tables:[/red] {', '.join(stats['failed_tables'])}")

        self.console.print("="*60)

    def get_migration_stats(self) -> Dict[str, Any]:
        """Get current migration statistics."""
        return {
            **self._migration_stats,
            "progress_summary": self.progress.get_summary(),
        }