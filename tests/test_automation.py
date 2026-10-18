"""
tests/test_automation.py
Unit tests for the cleanup automation task in automation_runner.py.
run_cleanup() deletes files in `task["path"]` that are older than
`task["older_than_days"]`, based on file modification time.
"""

import os
import time
import tempfile

from autoops.automation_runner import run_cleanup


def _make_old_file(folder, name, days_old):
    """Creates a file and backdates its modification time."""
    filepath = os.path.join(folder, name)
    with open(filepath, "w") as f:
        f.write("some data")

    old_time = time.time() - (days_old * 86400)
    os.utime(filepath, (old_time, old_time))
    return filepath


def test_cleanup_dry_run_does_not_delete():
    """In dry-run mode, old files must NOT be deleted."""
    with tempfile.TemporaryDirectory() as temp_dir:
        old_file = _make_old_file(temp_dir, "old.txt", days_old=10)

        task = {"path": temp_dir, "older_than_days": 7}
        run_cleanup(task, dry_run=True)

        assert os.path.exists(old_file), "dry-run should not delete files"


def test_cleanup_real_run_deletes_old_files_only():
    """
    With dry_run=False:
    - files older than older_than_days should be deleted
    - files newer than older_than_days should be kept
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        old_file = _make_old_file(temp_dir, "old.txt", days_old=10)
        new_file = _make_old_file(temp_dir, "new.txt", days_old=1)

        task = {"path": temp_dir, "older_than_days": 7}
        run_cleanup(task, dry_run=False)

        assert not os.path.exists(old_file), "old file should be deleted"
        assert os.path.exists(new_file), "recent file should NOT be deleted"
