import io
import sqlite3
import tempfile
from unittest.mock import MagicMock, patch, call

@pytest.fixture
def tmp_db(tmp_path):
    """Return a path to a fresh, empty SQLite database file."""
    return str(tmp_path / "test.db")
@pytest.fixture
def mock_schema_manager():
    sm = MagicMock()
    sm.table_exists.return_value = False
    sm.schemas_compatible.return_value = True
    sm.get_schema.return_value = []

    def _create_table(conn, table_name, schema):
        cols_sql = ", ".join(f"{c['name']} {c['type']}" for c in schema)
        conn.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({cols_sql})")

    def _drop_table(conn, table_name):
        conn.execute(f"DROP TABLE IF EXISTS {table_name}")

    sm.create_table.side_effect = _create_table
    sm.drop_table.side_effect = _drop_table
    return sm
