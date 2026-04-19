import io
import sqlite3
import tempfile


@pytest.fixture
def tmp_db(tmp_path):
    """Return a path to a fresh, empty SQLite database file."""
    return str(tmp_path / "test.db")
