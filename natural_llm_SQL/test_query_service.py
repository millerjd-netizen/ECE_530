import sqlite3
import pytest
from dataclasses import dataclass
from unittest.mock import MagicMock, patch

from query_service import QueryService, QueryResult

@dataclass
class ValidationResult:
    is_valid: bool
    error: str = ""


def make_validator(is_valid=True, error=""):
    """Return a mock validator whose validate() returns the given result."""
    v = MagicMock()
    v.validate.return_value = ValidationResult(is_valid=is_valid, error=error)
    return v


def make_schema_manager(tables=None, schema=None):
    sm = MagicMock()
    sm.list_tables.return_value = tables or []
    sm.get_schema.return_value = schema or []
    return sm


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def tmp_db(tmp_path):
    """Real SQLite DB with a 'users' table pre-populated."""
    db = str(tmp_path / "test.db")
    conn = sqlite3.connect(db)
    conn.execute(
        "CREATE TABLE users "
        "(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, age INTEGER)"
    )
    conn.execute("INSERT INTO users (name, age) VALUES ('Alice', 30)")
    conn.execute("INSERT INTO users (name, age) VALUES ('Bob', 25)")
    conn.commit()
    conn.close()
    return db


@pytest.fixture
def qs(tmp_db):
    """QueryService wired to a real DB, with a permissive validator."""
    return QueryService(tmp_db, make_validator(is_valid=True), make_schema_manager())


# ---------------------------------------------------------------------------
# QueryResult
# ---------------------------------------------------------------------------

class TestQueryResult:
    def test_as_dicts(self):
        result = QueryResult(
            sql="SELECT 1",
            columns=["name", "age"],
            rows=[("Alice", 30), ("Bob", 25)],
            row_count=2,
            success=True,
        )
        assert result.as_dicts == [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25},
        ]

    def test_as_dicts_empty(self):
        result = QueryResult(sql="", columns=[], rows=[], row_count=0, success=True)
        assert result.as_dicts == []


# ---------------------------------------------------------------------------
# execute — happy path
# ---------------------------------------------------------------------------

class TestExecuteHappyPath:
    def test_returns_rows(self, qs):
        result = qs.execute("SELECT name, age FROM users")
        assert result.success is True
        assert result.row_count == 2
        assert ("Alice", 30) in result.rows
        assert ("Bob", 25) in result.rows

    def test_returns_correct_columns(self, qs):
        result = qs.execute("SELECT name, age FROM users")
        assert result.columns == ["name", "age"]

    def test_sql_preserved_in_result(self, qs):
        sql = "SELECT * FROM users"
        result = qs.execute(sql)
        assert result.sql == sql

    def test_strips_whitespace_from_sql(self, qs):
        result = qs.execute("   SELECT * FROM users   ")
        assert result.success is True

    def test_where_clause_filters_rows(self, qs):
        result = qs.execute("SELECT name FROM users WHERE age > 27")
        assert result.row_count == 1
        assert result.rows[0][0] == "Alice"

    def test_empty_result_set_is_success(self, qs):
        result = qs.execute("SELECT * FROM users WHERE age > 999")
        assert result.success is True
        assert result.row_count == 0
        assert result.rows == []


# ---------------------------------------------------------------------------
# execute — validation rejection
# ---------------------------------------------------------------------------

class TestExecuteValidationRejection:
    def test_rejected_query_returns_failure(self, tmp_db):
        validator = make_validator(is_valid=False, error="Only SELECT is allowed.")
        qs = QueryService(tmp_db, validator, make_schema_manager())
        result = qs.execute("DROP TABLE users")
        assert result.success is False
        assert "SELECT" in result.error

    def test_rejected_query_does_not_touch_db(self, tmp_db):
        validator = make_validator(is_valid=False, error="Rejected.")
        qs = QueryService(tmp_db, validator, make_schema_manager())
        qs.execute("DROP TABLE users")
        # Table should still exist
        conn = sqlite3.connect(tmp_db)
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
        )
        assert cursor.fetchone() is not None
        conn.close()

    def test_validator_called_with_sql_and_db_path(self, tmp_db):
        validator = make_validator(is_valid=True)
        qs = QueryService(tmp_db, validator, make_schema_manager())
        qs.execute("SELECT 1")
        validator.validate.assert_called_once_with("SELECT 1", tmp_db)

    def test_empty_query_returns_error(self, qs):
        result = qs.execute("   ")
        assert result.success is False
        assert result.error == "Empty query."

    def test_validator_not_called_for_empty_query(self, tmp_db):
        validator = make_validator(is_valid=True)
        qs = QueryService(tmp_db, validator, make_schema_manager())
        qs.execute("")
        validator.validate.assert_not_called()


# ---------------------------------------------------------------------------
# execute — sqlite errors
# ---------------------------------------------------------------------------

class TestExecuteSQLiteErrors:
    def test_bad_sql_syntax_returns_failure(self, tmp_db):
        # Validator passes, but SQLite rejects it
        qs = QueryService(tmp_db, make_validator(is_valid=True), make_schema_manager())
        result = qs.execute("SELECT * FORM users")   # typo: FORM not FROM
        assert result.success is False
        assert result.error != ""

    def test_unknown_table_returns_failure(self, tmp_db):
        qs = QueryService(tmp_db, make_validator(is_valid=True), make_schema_manager())
        result = qs.execute("SELECT * FROM ghost_table")
        assert result.success is False


# ---------------------------------------------------------------------------
# get_schema_context
# ---------------------------------------------------------------------------

class TestGetSchemaContext:
    def test_returns_dict_of_tables(self, tmp_db):
        sm = make_schema_manager(
            tables=["users"],
            schema=[{"name": "id", "type": "INTEGER", "pk": 1},
                    {"name": "name", "type": "TEXT", "pk": 0}],
        )
        qs = QueryService(tmp_db, make_validator(), sm)
        ctx = qs.get_schema_context()
        assert "users" in ctx
        assert isinstance(ctx["users"], list)

    def test_empty_db_returns_empty_dict(self, tmp_db):
        sm = make_schema_manager(tables=[])
        qs = QueryService(tmp_db, make_validator(), sm)
        ctx = qs.get_schema_context()
        assert ctx == {}

    def test_schema_manager_called_per_table(self, tmp_db):
        sm = make_schema_manager(tables=["a", "b"])
        qs = QueryService(tmp_db, make_validator(), sm)
        qs.get_schema_context()
        assert sm.get_schema.call_count == 2


# ---------------------------------------------------------------------------
# list_tables
# ---------------------------------------------------------------------------

class TestListTables:
    def test_delegates_to_schema_manager(self, tmp_db):
        sm = make_schema_manager(tables=["users", "orders"])
        qs = QueryService(tmp_db, make_validator(), sm)
        assert qs.list_tables() == ["users", "orders"]

    def test_empty_db(self, tmp_db):
        sm = make_schema_manager(tables=[])
        qs = QueryService(tmp_db, make_validator(), sm)
        assert qs.list_tables() == []
