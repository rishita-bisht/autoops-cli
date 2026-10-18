"""
tests/test_parser.py
Unit tests for autoops/log_parser.py
"""

import os
import tempfile

from autoops.log_parser import classify_line, parse_log


def test_classify_line_matches_error():
    line = "2026-09-28 10:17:45 ERROR Database connection failed"
    result = classify_line(line)

    assert result is not None
    assert result["level"] == "ERROR"
    assert result["timestamp"] == "2026-09-28 10:17:45"
    assert result["message"] == "Database connection failed"


def test_classify_line_returns_none_for_bad_format():
    line = "this is not a valid log line"
    result = classify_line(line)

    assert result is None


def test_parse_log_counts_correctly():
    # Create a temporary log file so this test doesn't depend
    # on logs/sample.log existing or having specific content
    content = (
        "2026-09-28 10:00:00 ERROR Something broke\n"
        "2026-09-28 10:01:00 WARNING Disk almost full\n"
        "2026-09-28 10:02:00 INFO All good\n"
        "this line does not match\n"
    )

    with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
        f.write(content)
        temp_path = f.name

    try:
        result = parse_log(temp_path)
        assert result["counts"]["ERROR"] == 1
        assert result["counts"]["WARNING"] == 1
        assert result["counts"]["INFO"] == 1
        assert result["unmatched"] == 1
        assert len(result["entries"]) == 3
    finally:
        os.remove(temp_path)
