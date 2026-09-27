"""
autoops/storage.py
Handles saving parsed log entries into a SQLite database
and querying summary statistics back out.
"""

import sqlite3

DB_PATH = "storage/history.db"


def get_connection(db_path=DB_PATH):
    """Opens a connection to the SQLite database file."""
    return sqlite3.connect(db_path)


def init_db(db_path=DB_PATH):
    """
    Creates the log_entries table if it doesn't already exist.
    Safe to call every time the program starts.
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS log_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            source_file TEXT,
            level TEXT,
            message TEXT
        )
    """)
    conn.commit()
    conn.close()


def save_entries(entries, source_file, db_path=DB_PATH):
    """
    Inserts a list of parsed log entries (from log_parser.parse_log)
    into the database, tagged with which file they came from.
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()

    for entry in entries:
        cursor.execute(
            "INSERT INTO log_entries (timestamp, source_file, level, message) "
            "VALUES (?, ?, ?, ?)",
            (entry["timestamp"], source_file, entry["level"], entry["message"]),
        )

    conn.commit()
    conn.close()


def get_level_counts(db_path=DB_PATH):
    """
    Returns total counts per level across ALL saved history,
    not just the most recent parse. Useful for trend reports.
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT level, COUNT(*) FROM log_entries GROUP BY level
    """)
    rows = cursor.fetchall()
    conn.close()

    return dict(rows)
