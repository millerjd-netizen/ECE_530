import sqlite3
import pytest

from csv_loader.schema_manager import SchemaManager, _normalize_name, _normalize_type

@pytest.fixture
def sm():
    return SchemaManager()


@pytest.fixture
def conn():
    """Fresh in-memory SQLite connection for each test."""
    c = sqlite3.connect(":memory:")
    yield c
    c.close()


@pytest.fixture
def conn_with_people(conn):
    """Connection with a pre-populated 'people' table."""
    conn.execute(
        "CREATE TABLE people ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "name TEXT, "
        "age INTEGER, "
        "score REAL"
        ")"
    )
    conn.commit()
    return conn

class TestNormalizeType:
    def test_text_variants(self):
        for t in ("TEXT", "text", "VARCHAR", "varchar", "CHAR", "CLOB"):
            assert _normalize_type(t) == "TEXT"

    def test_integer_variants(self):
        for t in ("INTEGER", "INT", "TINYINT", "SMALLINT", "BIGINT", "BOOLEAN"):
            assert _normalize_type(t) == "INTEGER"

    def test_real_variants(self):
        for t in ("REAL", "FLOAT", "DOUBLE"):
            assert _normalize_type(t) == "REAL"

    def test_unknown_defaults_to_text(self):
        assert _normalize_type("JSONB") == "TEXT"

    def test_strips_length_specifier(self):
        # e.g. VARCHAR(255) → TEXT
        assert _normalize_type("VARCHAR(255)") == "TEXT"

class TestNormalizeName:
    def test_lowercases(self):
        assert _normalize_name("Name") == "name"

    def test_strips_whitespace(self):
        assert _normalize_name("  age  ") == "age"

class TestListTables:
    def test_empty_db_returns_empty(self, sm, conn):
        assert sm.list_tables(conn) == []

    def test_returns_created_tables(self, sm, conn):
        conn.execute("CREATE TABLE a (x TEXT)")
        conn.execute("CREATE TABLE b (y INTEGER)")
        assert set(sm.list_tables(conn)) == {"a", "b"}

    def test_returns_alphabetical_order(self, sm, conn):
        conn.execute("CREATE TABLE zebra (x TEXT)")
        conn.execute("CREATE TABLE apple (x TEXT)")
        tables = sm.list_tables(conn)
        assert tables == sorted(tables)

class TestTableExists:
    def test_returns_false_for_missing_table(self, sm, conn):
        assert sm.table_exists(conn, "nope") is False

    def test_returns_true_for_existing_table(self, sm, conn_with_people):
        assert sm.table_exists(conn_with_people, "people") is True

    def test_case_sensitive(self, sm, conn_with_people):
        # SQLite table names are case-sensitive in sqlite_master
        assert sm.table_exists(conn_with_people, "People") is False
class TestGetSchema:
    def test_returns_correct_columns(self, sm, conn_with_people):
        schema = sm.get_schema(conn_with_people, "people")
        names = [c["name"] for c in schema]
        assert "id" in names
        assert "name" in names
        assert "age" in names
        assert "score" in names

    def test_returns_correct_types(self, sm, conn_with_people):
        schema = sm.get_schema(conn_with_people, "people")
        lookup = {c["name"]: c["type"] for c in schema}
        assert lookup["name"] == "TEXT"
        assert lookup["age"] == "INTEGER"
        assert lookup["score"] == "REAL"

    def test_id_marked_as_primary_key(self, sm, conn_with_people):
        schema = sm.get_schema(conn_with_people, "people")
        pk_cols = [c["name"] for c in schema if c["pk"] == 1]
        assert "id" in pk_cols

    def test_raises_for_missing_table(self, sm, conn):
        with pytest.raises(ValueError, match="does not exist"):
            sm.get_schema(conn, "ghost")

class TestCreateTable:
    def test_creates_table(self, sm, conn):
        sm.create_table(conn, "products", [{"name": "title", "type": "TEXT"}])
        assert sm.table_exists(conn, "products")

    def test_auto_id_column_added(self, sm, conn):
        sm.create_table(conn, "t", [{"name": "x", "type": "TEXT"}])
        schema = sm.get_schema(conn, "t")
        names = [c["name"] for c in schema]
        assert "id" in names

    def test_id_is_primary_key(self, sm, conn):
        sm.create_table(conn, "t", [{"name": "x", "type": "TEXT"}])
        schema = sm.get_schema(conn, "t")
        pk = [c for c in schema if c["pk"] == 1]
        assert len(pk) == 1
        assert pk[0]["name"] == "id"

    def test_all_columns_present(self, sm, conn):
        cols = [
            {"name": "name", "type": "TEXT"},
            {"name": "age", "type": "INTEGER"},
            {"name": "score", "type": "REAL"},
        ]
        sm.create_table(conn, "people", cols)
        schema = sm.get_schema(conn, "people")
        names = [c["name"] for c in schema]
        assert "name" in names
        assert "age" in names
        assert "score" in names

    def test_raises_on_empty_schema(self, sm, conn):
        with pytest.raises(ValueError, match="empty schema"):
            sm.create_table(conn, "t", [])

    def test_normalizes_types_on_creation(self, sm, conn):
        sm.create_table(conn, "t", [{"name": "val", "type": "FLOAT"}])
        schema = sm.get_schema(conn, "t")
        lookup = {c["name"]: c["type"] for c in schema}
        assert lookup["val"] == "REAL"

class TestDropTable:
    def test_drops_existing_table(self, sm, conn_with_people):
        sm.drop_table(conn_with_people, "people")
        assert sm.table_exists(conn_with_people, "people") is False

    def test_drop_nonexistent_table_does_not_raise(self, sm, conn):
        # IF EXISTS means this should be a no-op
        sm.drop_table(conn, "ghost")  # should not raise



