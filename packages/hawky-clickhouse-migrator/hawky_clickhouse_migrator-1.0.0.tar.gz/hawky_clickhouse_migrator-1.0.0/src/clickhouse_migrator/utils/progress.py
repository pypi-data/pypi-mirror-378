"""Progress tracking utilities for ClickHouse migration."""

import json
import logging
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, Any

from rich.console import Console
from rich.progress import (
    Progress,
    BarColumn,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
    SpinnerColumn,
    TaskID,
)
from rich.table import Table
from rich.live import Live

logger = logging.getLogger(__name__)


@dataclass
class TableProgress:
    """Progress information for a single table."""
    table_name: str
    total_rows: int = 0
    processed_rows: int = 0
    batch_size: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: str = "pending"  # pending, running, completed, failed
    error_message: Optional[str] = None
    bytes_processed: int = 0
    last_checkpoint: int = 0

    @property
    def progress_percentage(self) -> float:
        """Calculate progress percentage."""
        if self.total_rows == 0:
            return 0.0
        return (self.processed_rows / self.total_rows) * 100

    @property
    def elapsed_time(self) -> Optional[timedelta]:
        """Calculate elapsed time."""
        if not self.start_time:
            return None
        end = self.end_time or datetime.now()
        return end - self.start_time

    @property
    def estimated_remaining(self) -> Optional[timedelta]:
        """Estimate remaining time."""
        if not self.start_time or self.processed_rows == 0:
            return None

        elapsed = self.elapsed_time
        if not elapsed or elapsed.total_seconds() == 0:
            return None

        rate = self.processed_rows / elapsed.total_seconds()
        if rate == 0:
            return None

        remaining_rows = self.total_rows - self.processed_rows
        remaining_seconds = remaining_rows / rate
        return timedelta(seconds=remaining_seconds)

    @property
    def rows_per_second(self) -> float:
        """Calculate processing rate in rows per second."""
        if not self.start_time or self.processed_rows == 0:
            return 0.0

        elapsed = self.elapsed_time
        if not elapsed or elapsed.total_seconds() == 0:
            return 0.0

        return self.processed_rows / elapsed.total_seconds()


class MigrationProgress:
    """Manages progress tracking for ClickHouse migration."""

    def __init__(self, console: Optional[Console] = None):
        """Initialize progress tracker."""
        self.console = console or Console()
        self.tables: Dict[str, TableProgress] = {}
        self.overall_start_time: Optional[datetime] = None
        self.overall_end_time: Optional[datetime] = None
        self.total_tables: int = 0
        self.completed_tables: int = 0
        self.failed_tables: int = 0

        # Rich progress components
        self._progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.1f}%"),
            "•",
            TextColumn("{task.completed}/{task.total} rows"),
            "•",
            TransferSpeedColumn(),
            "•",
            TimeRemainingColumn(),
            console=self.console,
            expand=True,
        )
        self._task_ids: Dict[str, TaskID] = {}
        self._live: Optional[Live] = None

    def start(self):
        """Start progress tracking."""
        self.overall_start_time = datetime.now()
        self._progress.start()

    def stop(self):
        """Stop progress tracking."""
        self.overall_end_time = datetime.now()
        self._progress.stop()
        if self._live:
            self._live.stop()

    def add_table(self, table_name: str, total_rows: int, batch_size: int = 0):
        """Add a table to track."""
        self.tables[table_name] = TableProgress(
            table_name=table_name,
            total_rows=total_rows,
            batch_size=batch_size,
            start_time=datetime.now(),
            status="running"
        )

        task_id = self._progress.add_task(
            f"Migrating {table_name}",
            total=total_rows,
            completed=0
        )
        self._task_ids[table_name] = task_id
        self.total_tables += 1

    def update_table(self, table_name: str, processed_rows: int, bytes_processed: int = 0):
        """Update progress for a table."""
        if table_name not in self.tables:
            logger.warning(f"Table {table_name} not found in progress tracker")
            return

        table_progress = self.tables[table_name]
        table_progress.processed_rows = processed_rows
        table_progress.bytes_processed += bytes_processed

        if table_name in self._task_ids:
            self._progress.update(
                self._task_ids[table_name],
                completed=processed_rows
            )

    def complete_table(self, table_name: str, success: bool = True, error_message: Optional[str] = None):
        """Mark a table as completed."""
        if table_name not in self.tables:
            return

        table_progress = self.tables[table_name]
        table_progress.end_time = datetime.now()
        table_progress.status = "completed" if success else "failed"
        table_progress.error_message = error_message

        if success:
            self.completed_tables += 1
            table_progress.processed_rows = table_progress.total_rows
        else:
            self.failed_tables += 1

        if table_name in self._task_ids:
            if success:
                self._progress.update(
                    self._task_ids[table_name],
                    completed=table_progress.total_rows
                )
            else:
                self._progress.update(
                    self._task_ids[table_name],
                    description=f"Failed: {table_name}"
                )

    def create_checkpoint(self, checkpoint_file: str):
        """Save current progress to checkpoint file."""
        try:
            checkpoint_data = {
                "timestamp": datetime.now().isoformat(),
                "overall_start_time": self.overall_start_time.isoformat() if self.overall_start_time else None,
                "total_tables": self.total_tables,
                "completed_tables": self.completed_tables,
                "failed_tables": self.failed_tables,
                "tables": {
                    name: {
                        **asdict(progress),
                        "start_time": progress.start_time.isoformat() if progress.start_time else None,
                        "end_time": progress.end_time.isoformat() if progress.end_time else None,
                    }
                    for name, progress in self.tables.items()
                }
            }

            checkpoint_path = Path(checkpoint_file)
            checkpoint_path.parent.mkdir(parents=True, exist_ok=True)

            with open(checkpoint_path, 'w') as f:
                json.dump(checkpoint_data, f, indent=2)

            logger.info(f"Checkpoint saved to {checkpoint_file}")

        except Exception as e:
            logger.error(f"Failed to create checkpoint: {e}")

    def load_checkpoint(self, checkpoint_file: str) -> bool:
        """Load progress from checkpoint file."""
        try:
            checkpoint_path = Path(checkpoint_file)
            if not checkpoint_path.exists():
                return False

            with open(checkpoint_path, 'r') as f:
                checkpoint_data = json.load(f)

            # Restore overall progress
            if checkpoint_data.get("overall_start_time"):
                self.overall_start_time = datetime.fromisoformat(checkpoint_data["overall_start_time"])

            self.total_tables = checkpoint_data.get("total_tables", 0)
            self.completed_tables = checkpoint_data.get("completed_tables", 0)
            self.failed_tables = checkpoint_data.get("failed_tables", 0)

            # Restore table progress
            for table_name, table_data in checkpoint_data.get("tables", {}).items():
                progress = TableProgress(
                    table_name=table_data["table_name"],
                    total_rows=table_data["total_rows"],
                    processed_rows=table_data["processed_rows"],
                    batch_size=table_data["batch_size"],
                    status=table_data["status"],
                    error_message=table_data.get("error_message"),
                    bytes_processed=table_data.get("bytes_processed", 0),
                    last_checkpoint=table_data.get("last_checkpoint", 0),
                )

                if table_data.get("start_time"):
                    progress.start_time = datetime.fromisoformat(table_data["start_time"])
                if table_data.get("end_time"):
                    progress.end_time = datetime.fromisoformat(table_data["end_time"])

                self.tables[table_name] = progress

            logger.info(f"Checkpoint loaded from {checkpoint_file}")
            return True

        except Exception as e:
            logger.error(f"Failed to load checkpoint: {e}")
            return False

    def get_summary(self) -> Dict[str, Any]:
        """Get migration summary."""
        total_rows = sum(table.total_rows for table in self.tables.values())
        processed_rows = sum(table.processed_rows for table in self.tables.values())
        total_bytes = sum(table.bytes_processed for table in self.tables.values())

        elapsed_time = None
        if self.overall_start_time:
            end_time = self.overall_end_time or datetime.now()
            elapsed_time = end_time - self.overall_start_time

        return {
            "total_tables": self.total_tables,
            "completed_tables": self.completed_tables,
            "failed_tables": self.failed_tables,
            "pending_tables": self.total_tables - self.completed_tables - self.failed_tables,
            "total_rows": total_rows,
            "processed_rows": processed_rows,
            "progress_percentage": (processed_rows / total_rows * 100) if total_rows > 0 else 0,
            "total_bytes_processed": total_bytes,
            "elapsed_time": str(elapsed_time) if elapsed_time else None,
            "overall_rate_rows_per_second": (processed_rows / elapsed_time.total_seconds()) if elapsed_time and elapsed_time.total_seconds() > 0 else 0,
        }

    def display_summary_table(self):
        """Display a summary table of migration progress."""
        table = Table(title="Migration Progress Summary")

        table.add_column("Table", style="cyan", no_wrap=True)
        table.add_column("Status", style="magenta")
        table.add_column("Progress", justify="right", style="green")
        table.add_column("Rows", justify="right", style="blue")
        table.add_column("Rate (rows/s)", justify="right", style="yellow")
        table.add_column("Time Elapsed", justify="right", style="white")

        for table_progress in self.tables.values():
            status_color = {
                "pending": "yellow",
                "running": "blue",
                "completed": "green",
                "failed": "red"
            }.get(table_progress.status, "white")

            progress_text = f"{table_progress.progress_percentage:.1f}%"
            rows_text = f"{table_progress.processed_rows:,}/{table_progress.total_rows:,}"
            rate_text = f"{table_progress.rows_per_second:.0f}"
            elapsed_text = str(table_progress.elapsed_time).split('.')[0] if table_progress.elapsed_time else "N/A"

            table.add_row(
                table_progress.table_name,
                f"[{status_color}]{table_progress.status.title()}[/{status_color}]",
                progress_text,
                rows_text,
                rate_text,
                elapsed_text
            )

        self.console.print(table)

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()