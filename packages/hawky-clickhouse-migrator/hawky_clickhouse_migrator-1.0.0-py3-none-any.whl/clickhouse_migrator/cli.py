"""Command-line interface for ClickHouse migration tool."""

import logging
import sys
from pathlib import Path
from typing import List, Optional

import click
from rich.console import Console
from rich.logging import RichHandler

from .core.config import MigrationConfig
from .core.migrator import ClickHouseMigrator
from .utils.exceptions import MigrationError, ConfigurationError
from .utils.schema_transformer import ClickHouseEngineTransformer

# Initialize console and logging
console = Console()


def setup_logging(level: str = "INFO", log_file: Optional[str] = None):
    """Setup logging configuration."""
    log_level = getattr(logging, level.upper(), logging.INFO)

    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            RichHandler(console=console, rich_tracebacks=True),
        ]
    )

    # Add file handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)
        logging.getLogger().addHandler(file_handler)

    # Suppress overly verbose logs
    logging.getLogger("clickhouse_connect").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


@click.group()
@click.version_option(version="1.0.0", prog_name="clickhouse-migrator")
@click.option("--log-level", default="INFO", help="Logging level", type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]))
@click.option("--log-file", help="Log file path")
@click.pass_context
def cli(ctx, log_level: str, log_file: Optional[str]):
    """
    ClickHouse Migrator - A reliable CLI tool for migrating data between ClickHouse instances.

    This tool supports migrating data from ClickHouse Cloud to self-hosted instances
    and vice versa, with features like custom queries, progress tracking, and resume capability.
    """
    ctx.ensure_object(dict)
    ctx.obj['log_level'] = log_level
    ctx.obj['log_file'] = log_file

    setup_logging(log_level, log_file)


@cli.command()
@click.argument("source_uri", required=True)
@click.argument("target_uri", required=True)
@click.option("--tables", "-t", multiple=True, help="Specific tables to migrate (default: all tables)")
@click.option("--exclude-tables", multiple=True, help="Tables to exclude from migration")
@click.option("--query", "-q", help="Custom SQL query for data selection")
@click.option("--batch-size", default=100000, help="Batch size for data migration", type=int)
@click.option("--workers", "-w", default=4, help="Number of parallel workers", type=int)
@click.option("--no-schema", is_flag=True, help="Skip schema migration")
@click.option("--no-data", is_flag=True, help="Skip data migration")
@click.option("--drop-target", is_flag=True, help="Drop target tables before migration")
@click.option("--verify", is_flag=True, default=True, help="Verify data integrity after migration")
@click.option("--resume", is_flag=True, help="Resume from previous checkpoint")
@click.option("--checkpoint-file", help="Custom checkpoint file path")
@click.option("--dry-run", is_flag=True, help="Perform a dry run without actual data migration")
@click.option("--config", "-c", help="Configuration file path")
@click.pass_context
def migrate(
    ctx,
    source_uri: str,
    target_uri: str,
    tables: tuple,
    exclude_tables: tuple,
    query: Optional[str],
    batch_size: int,
    workers: int,
    no_schema: bool,
    no_data: bool,
    drop_target: bool,
    verify: bool,
    resume: bool,
    checkpoint_file: Optional[str],
    dry_run: bool,
    config: Optional[str],
):
    """
    Migrate data between ClickHouse instances.

    SOURCE_URI: Source ClickHouse connection URI
    TARGET_URI: Target ClickHouse connection URI

    URI Format: clickhouse://user:password@host:port/database

    Examples:
      clickhouse-migrator migrate \\
        clickhouse://user:pass@cloud-host:8443/mydb \\
        clickhouse://user:pass@localhost:8123/mydb

      clickhouse-migrator migrate \\
        https://user:pass@cloud.clickhouse.com:8443/mydb \\
        http://localhost:8123/mydb \\
        --tables users orders --batch-size 50000

      clickhouse-migrator migrate \\
        clickhouse://user:pass@source:8123/db \\
        clickhouse://user:pass@target:8123/db \\
        --query "SELECT * FROM users WHERE created_at > '2024-01-01'"
    """
    try:
        logger = logging.getLogger(__name__)
        logger.info("Starting ClickHouse migration...")

        # Load configuration
        if config:
            # Load from configuration file
            migration_config = MigrationConfig.from_file(config)
            logger.info(f"Loaded configuration from {config}")
        else:
            # Create configuration from CLI arguments
            migration_config = MigrationConfig.from_cli_args(
                source_uri=source_uri,
                target_uri=target_uri,
                tables=list(tables) if tables else None,
                query=query,
                batch_size=batch_size,
                workers=workers,
                migrate_schema=not no_schema,
                migrate_data=not no_data,
                verify_data=verify,
                resume=resume,
                checkpoint_file=checkpoint_file,
                dry_run=dry_run,
                exclude_tables=list(exclude_tables) if exclude_tables else [],
            )

            # Apply drop_target setting to all tables
            if drop_target:
                for table_config in migration_config.tables:
                    table_config.drop_target = True

        # Validate configuration
        config_errors = migration_config.validate_connections()
        if config_errors:
            for error in config_errors:
                console.print(f"[red]Configuration Error:[/red] {error}")
            return False

        # Display migration plan
        console.print("\n[bold blue]Migration Plan:[/bold blue]")
        console.print(f"[blue]Source:[/blue] {migration_config.source.uri}")
        console.print(f"[blue]Target:[/blue] {migration_config.target.uri}")
        console.print(f"[blue]Migrate Schema:[/blue] {migration_config.migrate_schema}")
        console.print(f"[blue]Migrate Data:[/blue] {migration_config.migrate_data}")
        console.print(f"[blue]Batch Size:[/blue] {migration_config.batch.size:,}")
        console.print(f"[blue]Parallel Workers:[/blue] {migration_config.batch.parallel_workers}")
        console.print(f"[blue]Dry Run:[/blue] {migration_config.dry_run}")

        if migration_config.tables:
            table_names = [table.name for table in migration_config.tables]
            console.print(f"[blue]Tables:[/blue] {', '.join(table_names)}")

        if migration_config.exclude_tables:
            console.print(f"[blue]Excluded Tables:[/blue] {', '.join(migration_config.exclude_tables)}")

        # Confirm migration
        if not dry_run:
            if not click.confirm("\nProceed with migration?"):
                console.print("[yellow]Migration cancelled.[/yellow]")
                return

        # Run migration
        migrator = ClickHouseMigrator(migration_config, console)
        success = migrator.run_migration()

        if success:
            console.print("\n[bold green]Migration completed successfully![/bold green]")
            return True
        else:
            console.print("\n[bold red]Migration failed![/bold red]")
            return False

    except ConfigurationError as e:
        console.print(f"[red]Configuration Error:[/red] {e}")
        return False
    except MigrationError as e:
        console.print(f"[red]Migration Error:[/red] {e}")
        return False
    except KeyboardInterrupt:
        console.print("\n[yellow]Migration interrupted by user.[/yellow]")
        return False
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {e}")
        logging.exception("Unexpected error during migration")
        return False


@cli.command()
@click.argument("uri", required=True)
@click.option("--database", "-d", help="Specific database to list tables from")
def list_tables(uri: str, database: Optional[str]):
    """
    List tables in a ClickHouse instance.

    URI: ClickHouse connection URI

    Examples:
      clickhouse-migrator list-tables clickhouse://user:pass@host:8123/mydb
      clickhouse-migrator list-tables https://user:pass@cloud.clickhouse.com:8443/mydb
    """
    try:
        from .core.connection import ClickHouseConnection

        logger = logging.getLogger(__name__)
        logger.info(f"Connecting to {uri}")

        # Create connection
        conn = ClickHouseConnection(uri)
        conn.connect()

        # Get database list
        if database:
            databases = [database]
        else:
            databases = conn.get_databases()

        console.print(f"\n[bold blue]Available Tables:[/bold blue]")

        for db in databases:
            tables = conn.get_tables(db)
            console.print(f"\n[blue]Database: {db}[/blue]")

            if not tables:
                console.print("  [yellow]No tables found[/yellow]")
            else:
                for table in tables:
                    # Get row count
                    try:
                        row_count = conn.get_table_count(db, table)
                        console.print(f"  • {table} ({row_count:,} rows)")
                    except Exception:
                        console.print(f"  • {table} (row count unavailable)")

        conn.close()

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        return False


@cli.command()
@click.argument("uri", required=True)
@click.argument("table", required=True)
@click.option("--database", "-d", help="Database name (default: from URI)")
@click.option("--limit", "-l", default=10, help="Number of sample rows to display", type=int)
def inspect_table(uri: str, table: str, database: Optional[str], limit: int):
    """
    Inspect a table structure and sample data.

    URI: ClickHouse connection URI
    TABLE: Table name to inspect

    Examples:
      clickhouse-migrator inspect-table clickhouse://user:pass@host:8123/mydb users
      clickhouse-migrator inspect-table https://user:pass@cloud.clickhouse.com:8443/mydb orders --limit 5
    """
    try:
        from .core.connection import ClickHouseConnection
        from rich.table import Table

        logger = logging.getLogger(__name__)

        # Create connection
        conn = ClickHouseConnection(uri)
        conn.connect()

        db = database or conn.connection_params.get('database', 'default')

        # Get table info
        table_info = conn.get_table_info(db, table)
        row_count = conn.get_table_count(db, table)

        # Display table structure
        console.print(f"\n[bold blue]Table: {db}.{table}[/bold blue]")
        console.print(f"[blue]Total Rows:[/blue] {row_count:,}")

        # Column information
        structure_table = Table(title="Table Structure")
        structure_table.add_column("Column", style="cyan")
        structure_table.add_column("Type", style="magenta")
        structure_table.add_column("Default", style="green")

        for col_info in table_info['columns']:
            name, type_name, default_kind, default_expr = col_info[:4]
            default_text = f"{default_kind}: {default_expr}" if default_expr else ""
            structure_table.add_row(name, type_name, default_text)

        console.print(structure_table)

        # Sample data
        if limit > 0 and row_count > 0:
            sample_query = f"SELECT * FROM `{db}`.`{table}` LIMIT {limit}"
            result = conn.execute_query(sample_query)

            if result.result_rows:
                sample_table = Table(title=f"Sample Data (First {len(result.result_rows)} rows)")

                # Add columns
                for col_name in table_info['column_names']:
                    sample_table.add_column(col_name, style="white")

                # Add rows
                for row in result.result_rows:
                    sample_table.add_row(*[str(val) if val is not None else "NULL" for val in row])

                console.print(sample_table)

        conn.close()

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        return False


@cli.command()
@click.argument("source_uri", required=True)
@click.argument("target_uri", required=True)
def test_connection(source_uri: str, target_uri: str):
    """
    Test connections to source and target ClickHouse instances.

    SOURCE_URI: Source ClickHouse connection URI
    TARGET_URI: Target ClickHouse connection URI
    """
    try:
        from .core.connection import ClickHouseConnection

        logger = logging.getLogger(__name__)

        console.print("[bold blue]Testing Connections...[/bold blue]")

        # Test source connection
        console.print(f"\n[blue]Testing source connection:[/blue] {source_uri}")
        try:
            source_conn = ClickHouseConnection(source_uri)
            if source_conn.test_connection():
                console.print("[green]✓ Source connection successful[/green]")

                # Show basic info
                databases = source_conn.get_databases()
                console.print(f"  Available databases: {', '.join(databases)}")
            else:
                console.print("[red]✗ Source connection failed[/red]")
                return False
        except Exception as e:
            console.print(f"[red]✗ Source connection error: {e}[/red]")
            return False
        finally:
            source_conn.close()

        # Test target connection
        console.print(f"\n[blue]Testing target connection:[/blue] {target_uri}")
        try:
            target_conn = ClickHouseConnection(target_uri)
            if target_conn.test_connection():
                console.print("[green]✓ Target connection successful[/green]")

                # Show basic info
                databases = target_conn.get_databases()
                console.print(f"  Available databases: {', '.join(databases)}")
            else:
                console.print("[red]✗ Target connection failed[/red]")
                return False
        except Exception as e:
            console.print(f"[red]✗ Target connection error: {e}[/red]")
            return False
        finally:
            target_conn.close()

        console.print("\n[bold green]All connections successful![/bold green]")
        return True

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        return False


@cli.command()
@click.argument("source_uri", required=True)
@click.argument("target_uri", required=True)
def check_compatibility(source_uri: str, target_uri: str):
    """
    Check schema compatibility between source and target ClickHouse instances.

    This command analyzes engine compatibility and suggests transformations needed
    for migration between ClickHouse Cloud and self-hosted instances.

    SOURCE_URI: Source ClickHouse connection URI
    TARGET_URI: Target ClickHouse connection URI
    """
    try:
        from .core.connection import ClickHouseConnection
        from rich.table import Table

        logger = logging.getLogger(__name__)

        console.print("[bold blue]Analyzing Compatibility...[/bold blue]")

        # Create connections
        console.print(f"\n[blue]Connecting to source:[/blue] {source_uri}")
        source_conn = ClickHouseConnection(source_uri)
        source_conn.connect()

        console.print(f"[blue]Connecting to target:[/blue] {target_uri}")
        target_conn = ClickHouseConnection(target_uri)
        target_conn.connect()

        # Analyze compatibility
        transformer = ClickHouseEngineTransformer()
        analysis = transformer.analyze_compatibility(source_conn, target_conn)

        # Display results
        console.print(f"\n[bold green]Compatibility Analysis Results[/bold green]")
        console.print(f"[blue]Source engines found:[/blue] {len(analysis['source_engines'])}")
        console.print(f"[blue]Target engines found:[/blue] {len(analysis['target_engines'])}")

        if analysis['cloud_engines_found']:
            console.print(f"\n[yellow]ClickHouse Cloud engines detected:[/yellow]")
            for engine in analysis['cloud_engines_found']:
                console.print(f"  • {engine}")

        if analysis['transformation_needed']:
            console.print(f"\n[red]⚠️  Schema transformation required![/red]")
            console.print(f"[yellow]Incompatible engines:[/yellow]")
            for engine in analysis['engines_to_transform']:
                target_engine = transformer.engine_mapping.get(engine, 'Unknown')
                console.print(f"  • {engine} → {target_engine}")

            console.print(f"\n[green]✅ Good news![/green] The migration tool can automatically transform these engines.")
            console.print("Run your migration with the standard command - transformations will be applied automatically.")
        else:
            console.print(f"\n[bold green]✅ All engines are compatible![/bold green]")
            console.print("No schema transformations needed for migration.")

        # Show engine comparison table
        engine_table = Table(title="Engine Compatibility Matrix")
        engine_table.add_column("Engine", style="cyan")
        engine_table.add_column("Source", style="green")
        engine_table.add_column("Target", style="magenta")
        engine_table.add_column("Status", style="white")

        all_engines = analysis['source_engines'].union(analysis['target_engines'])
        for engine in sorted(all_engines):
            source_has = "✅" if engine in analysis['source_engines'] else "❌"
            target_has = "✅" if engine in analysis['target_engines'] else "❌"

            if engine in analysis['source_engines'] and engine not in analysis['target_engines']:
                if engine in transformer.engine_mapping:
                    status = f"→ {transformer.engine_mapping[engine]}"
                else:
                    status = "⚠️ Manual fix needed"
            elif engine in analysis['target_engines']:
                status = "✅ Compatible"
            else:
                status = "N/A"

            engine_table.add_row(engine, source_has, target_has, status)

        console.print(engine_table)

        source_conn.close()
        target_conn.close()

        return True

    except Exception as e:
        console.print(f"[red]Error during compatibility check:[/red] {e}")
        return False


@cli.command()
@click.option("--output", "-o", default="migration-config.yaml", help="Output configuration file path")
def generate_config(output: str):
    """
    Generate a sample configuration file.

    This creates a template configuration file that you can customize for your migration needs.
    """
    try:
        config_template = """
# ClickHouse Migration Configuration
# This file configures the migration between ClickHouse instances

# Source database connection
source:
  uri: "clickhouse://user:password@source-host:8123/database"
  timeout: 30
  max_retries: 3

# Target database connection
target:
  uri: "clickhouse://user:password@target-host:8123/database"
  timeout: 30
  max_retries: 3

# Tables to migrate (leave empty to migrate all tables)
tables:
  - name: "users"
    # Optional: custom query for data selection
    # query: "SELECT * FROM users WHERE active = 1"
    # Optional: WHERE clause for filtering
    # where_clause: "created_at > '2024-01-01'"
    create_table: true
    drop_target: false

  - name: "orders"
    create_table: true
    drop_target: false

# Tables to exclude from migration
exclude_tables:
  - "temp_table"
  - "backup_table"

# Migration settings
migrate_schema: true
migrate_data: true
verify_data: true
dry_run: false

# Batch processing configuration
batch:
  size: 100000              # Rows per batch
  parallel_workers: 4       # Number of parallel workers
  memory_limit_mb: 1024     # Memory limit per worker

# Progress tracking configuration
progress:
  update_interval: 1000     # Progress update every N rows
  log_level: "INFO"
  checkpoint_interval: 50000 # Create checkpoint every N rows

# Resume configuration
resume: false
# checkpoint_file: "custom_checkpoint.json"
"""

        output_path = Path(output)
        output_path.write_text(config_template.strip())

        console.print(f"[green]Configuration template created:[/green] {output}")
        console.print("\nEdit the configuration file with your connection details and run:")
        console.print(f"[blue]clickhouse-migrator migrate --config {output}[/blue]")

    except Exception as e:
        console.print(f"[red]Error creating configuration file:[/red] {e}")
        return False


def main():
    """Main entry point for the CLI."""
    try:
        cli()
    except Exception as e:
        console.print(f"[red]Fatal error:[/red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()