#!/usr/bin/env python3
"""
Basic migration example using the ClickHouse Migrator programmatically.

This example shows how to use the migrator as a Python library
instead of using the CLI interface.
"""

import logging
from rich.console import Console

from clickhouse_migrator import ClickHouseMigrator, MigrationConfig


def main():
    """Run a basic migration example."""
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    console = Console()

    console.print("[bold blue]ClickHouse Migration Example[/bold blue]")

    # Create migration configuration
    config = MigrationConfig.from_cli_args(
        source_uri="clickhouse://default:@localhost:8123/source_db",
        target_uri="clickhouse://default:@localhost:8123/target_db",
        tables=["users", "orders"],
        batch_size=10000,
        workers=2,
        verify_data=True
    )

    console.print(f"[green]Source:[/green] {config.source.uri}")
    console.print(f"[green]Target:[/green] {config.target.uri}")
    console.print(f"[green]Tables:[/green] {[t.name for t in config.tables]}")

    # Create and run migrator
    migrator = ClickHouseMigrator(config, console)

    try:
        success = migrator.run_migration()

        if success:
            console.print("[bold green]Migration completed successfully![/bold green]")

            # Print migration statistics
            stats = migrator.get_migration_stats()
            console.print(f"[blue]Total tables:[/blue] {stats['total_tables']}")
            console.print(f"[blue]Migrated rows:[/blue] {stats['migrated_rows']:,}")

        else:
            console.print("[bold red]Migration failed![/bold red]")
            stats = migrator.get_migration_stats()
            if stats["failed_tables"]:
                console.print(f"[red]Failed tables:[/red] {', '.join(stats['failed_tables'])}")

    except KeyboardInterrupt:
        console.print("[yellow]Migration interrupted by user.[/yellow]")
    except Exception as e:
        console.print(f"[red]Migration error:[/red] {e}")


if __name__ == "__main__":
    main()