"""
autoops/log_parser.py
Reads a log file line by line and classifies each line as
ERROR, WARNING, or INFO using regex. Counts occurrences of each.
"""

import re

# Pattern breakdown:
# (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) -> captures the timestamp
# (ERROR|WARNING|INFO)                  -> captures the log level
# (.+)                                  -> captures the rest of the message
LOG_PATTERN = re.compile(
    r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) (ERROR|WARNING|INFO) (.+)"
)


def read_lines(filepath):
    """
    Generator that yields one line at a time instead of loading
    the whole file into memory. Important for large log files.
    """
    with open(filepath, "r") as f:
        for line in f:
            yield line.strip()


def classify_line(line):
    """
    Tries to match a single line against LOG_PATTERN.
    Returns a dict with timestamp, level, message if matched,
    otherwise None (line didn't match expected format).
    """
    match = LOG_PATTERN.match(line)
    if not match:
        return None

    timestamp, level, message = match.groups()
    return {
        "timestamp": timestamp,
        "level": level,
        "message": message,
    }


def parse_log(filepath):
    """
    Reads the whole file, classifies every line, and returns:
    - a list of parsed entries (dicts)
    - a summary count per level (ERROR / WARNING / INFO)
    - a count of lines that didn't match the expected format
    """
    entries = []
    counts = {"ERROR": 0, "WARNING": 0, "INFO": 0}
    unmatched = 0

    for line in read_lines(filepath):
        if not line:
            continue  # skip empty lines

        parsed = classify_line(line)
        if parsed is None:
            unmatched += 1
            continue

        entries.append(parsed)
        counts[parsed["level"]] += 1

    return {
        "entries": entries,
        "counts": counts,
        "unmatched": unmatched,
    }
