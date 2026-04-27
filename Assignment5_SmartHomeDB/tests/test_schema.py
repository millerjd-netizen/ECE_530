import sqlite3
from pathlib import Path


def test_schema_creates_tables():
    schema_path = Path("sql/schema.sql")
    sql = schema_path.read_text()

    conn = sqlite3.connect(":memory:")
    conn.executescript(sql)

    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    )
    tables = {row[0] for row in cursor.fetchall()}

    assert len(tables) > 0