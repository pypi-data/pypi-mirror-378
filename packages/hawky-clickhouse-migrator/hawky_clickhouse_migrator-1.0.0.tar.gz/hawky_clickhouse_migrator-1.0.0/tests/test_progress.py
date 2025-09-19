"""Tests for progress tracking functionality."""

import json
import tempfile
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest

from clickhouse_migrator.utils.progress import TableProgress, MigrationProgress


class TestTableProgress:
    """Test TableProgress class."""

    def test_basic_table_progress(self):
        """Test basic table progress creation."""
        progress = TableProgress(
            table_name="users",
            total_rows=1000,
            batch_size=100
        )

        assert progress.table_name == "users"
        assert progress.total_rows == 1000
        assert progress.batch_size == 100
        assert progress.processed_rows == 0
        assert progress.status == "pending"

    def test_progress_percentage(self):
        """Test progress percentage calculation."""
        progress = TableProgress(table_name="test", total_rows=1000)

        # No progress
        assert progress.progress_percentage == 0.0

        # 50% progress
        progress.processed_rows = 500
        assert progress.progress_percentage == 50.0

        # 100% progress
        progress.processed_rows = 1000
        assert progress.progress_percentage == 100.0

        # Handle division by zero
        progress.total_rows = 0
        assert progress.progress_percentage == 0.0

    def test_elapsed_time(self):
        """Test elapsed time calculation."""
        progress = TableProgress(table_name="test", total_rows=1000)

        # No start time
        assert progress.elapsed_time is None

        # With start time, no end time
        start_time = datetime.now()
        progress.start_time = start_time
        elapsed = progress.elapsed_time
        assert elapsed is not None
        assert isinstance(elapsed, timedelta)

        # With both start and end time
        progress.end_time = start_time + timedelta(seconds=30)
        assert progress.elapsed_time == timedelta(seconds=30)

    def test_estimated_remaining(self):
        """Test estimated remaining time calculation."""
        progress = TableProgress(table_name="test", total_rows=1000)

        # No start time
        assert progress.estimated_remaining is None

        # With start time but no processed rows
        progress.start_time = datetime.now() - timedelta(seconds=10)
        assert progress.estimated_remaining is None

        # With start time and processed rows
        progress.processed_rows = 250  # 25% complete
        remaining = progress.estimated_remaining
        assert remaining is not None
        assert isinstance(remaining, timedelta)
        # Should estimate ~30 seconds remaining (3x the elapsed 10 seconds)

    def test_rows_per_second(self):
        """Test rows per second calculation."""
        progress = TableProgress(table_name="test", total_rows=1000)

        # No start time
        assert progress.rows_per_second == 0.0

        # With start time but no processed rows
        progress.start_time = datetime.now() - timedelta(seconds=10)
        assert progress.rows_per_second == 0.0

        # With start time and processed rows
        progress.processed_rows = 500
        rate = progress.rows_per_second
        assert rate > 0
        assert rate == pytest.approx(50, rel=1e-1)  # ~50 rows/second


class TestMigrationProgress:
    """Test MigrationProgress class."""

    def test_initialization(self):
        """Test migration progress initialization."""
        progress = MigrationProgress()

        assert len(progress.tables) == 0
        assert progress.overall_start_time is None
        assert progress.overall_end_time is None
        assert progress.total_tables == 0
        assert progress.completed_tables == 0
        assert progress.failed_tables == 0

    def test_add_table(self):
        """Test adding table to progress tracking."""
        progress = MigrationProgress()

        with patch.object(progress._progress, 'add_task', return_value='task_id') as mock_add_task:
            progress.add_table("users", 1000, 100)

        assert "users" in progress.tables
        assert progress.tables["users"].table_name == "users"
        assert progress.tables["users"].total_rows == 1000
        assert progress.tables["users"].batch_size == 100
        assert progress.tables["users"].status == "running"
        assert progress.total_tables == 1

        mock_add_task.assert_called_once_with("Migrating users", total=1000, completed=0)

    def test_update_table(self):
        """Test updating table progress."""
        progress = MigrationProgress()

        with patch.object(progress._progress, 'add_task', return_value='task_id'):
            progress.add_table("users", 1000, 100)

        with patch.object(progress._progress, 'update') as mock_update:
            progress.update_table("users", 500, 1024)

        table_progress = progress.tables["users"]
        assert table_progress.processed_rows == 500
        assert table_progress.bytes_processed == 1024

        mock_update.assert_called_once_with('task_id', completed=500)

    def test_update_nonexistent_table(self):
        """Test updating non-existent table (should not crash)."""
        progress = MigrationProgress()

        # Should not raise exception
        progress.update_table("nonexistent", 100)

    def test_complete_table_success(self):
        """Test completing table successfully."""
        progress = MigrationProgress()

        with patch.object(progress._progress, 'add_task', return_value='task_id'):
            progress.add_table("users", 1000, 100)

        with patch.object(progress._progress, 'update') as mock_update:
            progress.complete_table("users", success=True)

        table_progress = progress.tables["users"]
        assert table_progress.status == "completed"
        assert table_progress.processed_rows == 1000  # Should be set to total
        assert table_progress.end_time is not None
        assert progress.completed_tables == 1
        assert progress.failed_tables == 0

        mock_update.assert_called_once_with('task_id', completed=1000)

    def test_complete_table_failure(self):
        """Test completing table with failure."""
        progress = MigrationProgress()

        with patch.object(progress._progress, 'add_task', return_value='task_id'):
            progress.add_table("users", 1000, 100)

        error_message = "Connection failed"
        with patch.object(progress._progress, 'update') as mock_update:
            progress.complete_table("users", success=False, error_message=error_message)

        table_progress = progress.tables["users"]
        assert table_progress.status == "failed"
        assert table_progress.error_message == error_message
        assert table_progress.end_time is not None
        assert progress.completed_tables == 0
        assert progress.failed_tables == 1

        mock_update.assert_called_once_with('task_id', description="Failed: users")

    def test_create_checkpoint(self):
        """Test creating checkpoint file."""
        progress = MigrationProgress()
        progress.overall_start_time = datetime.now()

        # Add some progress data
        with patch.object(progress._progress, 'add_task', return_value='task_id'):
            progress.add_table("users", 1000, 100)
            progress.update_table("users", 500)

        # Create temporary checkpoint file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name

        try:
            progress.create_checkpoint(temp_path)

            # Verify checkpoint file exists and has correct data
            assert os.path.exists(temp_path)

            with open(temp_path, 'r') as f:
                checkpoint_data = json.load(f)

            assert "timestamp" in checkpoint_data
            assert "overall_start_time" in checkpoint_data
            assert checkpoint_data["total_tables"] == 1
            assert "users" in checkpoint_data["tables"]
            assert checkpoint_data["tables"]["users"]["processed_rows"] == 500

        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_load_checkpoint_success(self):
        """Test loading checkpoint successfully."""
        # Create test checkpoint data
        checkpoint_data = {
            "timestamp": datetime.now().isoformat(),
            "overall_start_time": datetime.now().isoformat(),
            "total_tables": 2,
            "completed_tables": 1,
            "failed_tables": 0,
            "tables": {
                "users": {
                    "table_name": "users",
                    "total_rows": 1000,
                    "processed_rows": 1000,
                    "batch_size": 100,
                    "status": "completed",
                    "error_message": None,
                    "bytes_processed": 2048,
                    "last_checkpoint": 0,
                    "start_time": datetime.now().isoformat(),
                    "end_time": datetime.now().isoformat()
                }
            }
        }

        # Create temporary checkpoint file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(checkpoint_data, f)
            temp_path = f.name

        try:
            progress = MigrationProgress()
            success = progress.load_checkpoint(temp_path)

            assert success is True
            assert progress.total_tables == 2
            assert progress.completed_tables == 1
            assert progress.failed_tables == 0
            assert "users" in progress.tables

            table_progress = progress.tables["users"]
            assert table_progress.table_name == "users"
            assert table_progress.processed_rows == 1000
            assert table_progress.status == "completed"

        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_load_checkpoint_file_not_found(self):
        """Test loading checkpoint from non-existent file."""
        progress = MigrationProgress()
        success = progress.load_checkpoint("nonexistent_file.json")
        assert success is False

    def test_get_summary(self):
        """Test getting migration summary."""
        progress = MigrationProgress()
        progress.overall_start_time = datetime.now() - timedelta(seconds=60)

        # Add some tables
        with patch.object(progress._progress, 'add_task', return_value='task_id'):
            progress.add_table("users", 1000, 100)
            progress.add_table("orders", 2000, 200)

        progress.update_table("users", 500, 1024)
        progress.update_table("orders", 1500, 2048)
        progress.complete_table("users", success=True)

        summary = progress.get_summary()

        assert summary["total_tables"] == 2
        assert summary["completed_tables"] == 1
        assert summary["failed_tables"] == 0
        assert summary["pending_tables"] == 1
        assert summary["total_rows"] == 3000  # 1000 + 2000
        assert summary["processed_rows"] == 2000  # 500 + 1500
        assert summary["progress_percentage"] == pytest.approx(66.67, rel=1e-2)
        assert summary["total_bytes_processed"] == 3072  # 1024 + 2048
        assert summary["elapsed_time"] is not None
        assert summary["overall_rate_rows_per_second"] > 0

    def test_context_manager(self):
        """Test context manager functionality."""
        progress = MigrationProgress()

        with patch.object(progress._progress, 'start') as mock_start:
            with patch.object(progress._progress, 'stop') as mock_stop:
                with progress:
                    assert progress.overall_start_time is not None

        mock_start.assert_called_once()
        mock_stop.assert_called_once()