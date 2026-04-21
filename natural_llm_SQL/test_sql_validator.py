import sqlite3
import pytest

from csv_loader.sql_validator import (
    SQLValidator,
    _extract_table_names,
    _get_existing_tables,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def validator():
    return SQLValidator()


@pytest.fixture
def tmp_db(tmp_path):
    """DB with 'users' and 'orders' tables."""
    db = str(tmp_path / "test.db")
    conn = sqlite3.connect(db)
    conn.execute(
        "CREATE TABLE users "
        "(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, age INTEGER)"
    )
    conn.execute(
        "CREATE TABLE orders "
        "(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, total REAL)"
    )
    conn.execute("INSERT INTO users (name, age) VALUES ('Alice', 30)")
    conn.execute("INSERT INTO users (name, age) VALUES ('Bob', 25)")
    conn.execute("INSERT INTO orders (user_id, total) VALUES (1, 99.5)")
    conn.commit()
    conn.close()
    return db


# ---------------------------------------------------------------------------
# _extract_table_names
# ---------------------------------------------------------------------------

class TestExtractTableNames:
    def test_simple_from(self):
        assert _extract_table_names("SELECT * FROM users") == {"users"}

    def test_join(self):
        assert _extract_table_names(
            "SELECT * FROM users JOIN orders ON users.id = orders.user_id"
        ) == {"users", "orders"}

    def test_multiple_joins(self):
        sql = "SELECT * FROM a JOIN b ON a.id=b.a_id JOIN c ON b.id=c.b_id"
        assert _extract_table_names(sql) == {"a", "b", "c"}

    def test_case_insensitive(self):
        assert _extract_table_names("SELECT * FROM Users") == {"users"}

    def test_alias_ignored(self):
        # "FROM users u" — should extract "users", not "u"
        result = _extract_table_names("SELECT u.name FROM users u")
        assert "users" in result

    def test_empty_returns_empty_set(self):
        assert _extract_table_names("SELECT 1") == set()


# ---------------------------------------------------------------------------
# _get_existing_tables
# ---------------------------------------------------------------------------

class TestGetExistingTables:
    def test_returns_table_names(self, tmp_db):
        conn = sqlite3.connect(tmp_db)
        tables = _get_existing_tables(conn)
        conn.close()
        assert {"users", "orders"}.issubset(tables)

    def test_empty_db_returns_empty_set(self, tmp_path):
        conn = sqlite3.connect(str(tmp_path / "empty.db"))
        assert _get_existing_tables(conn) == set()
        conn.close()


# ---------------------------------------------------------------------------
# _check_not_empty
# ---------------------------------------------------------------------------

class TestCheckNotEmpty:
    def test_empty_string(self, validator):
        result = validator._check_not_empty("")
        assert result.is_valid is False
        assert "empty" in result.error.lower()

    def test_nonempty_string(self, validator):
        assert validator._check_not_empty("SELECT 1").is_valid is True


# ---------------------------------------------------------------------------
# _check_is_select
# ---------------------------------------------------------------------------

class TestCheckIsSelect:
    def test_select_passes(self, validator):
        assert validator._check_is_select("SELECT * FROM users").is_valid is True

    def test_select_case_insensitive(self, validator):
        assert validator._check_is_select("select * from users").is_valid is True

    def test_insert_fails(self, validator):
        result = validator._check_is_select("INSERT INTO users VALUES (1)")
        assert result.is_valid is False
        assert "INSERT" in result.error

    def test_drop_fails(self, validator):
        result = validator._check_is_select("DROP TABLE users")
        assert result.is_valid is False

    def test_update_fails(self, validator):
        assert validator._check_is_select("UPDATE users SET age=1").is_valid is False

    def test_delete_fails(self, validator):
        assert validator._check_is_select("DELETE FROM users").is_valid is False


# ---------------------------------------------------------------------------
# _check_no_dangerous_patterns
# ---------------------------------------------------------------------------

class TestCheckNoDangerousPatterns:
    def test_line_comment_rejected(self, validator):
        result = validator._check_no_dangerous_patterns("SELECT 1 -- drop table")
        assert result.is_valid is False

    def test_block_comment_rejected(self, validator):
        result = validator._check_no_dangerous_patterns("SELECT /* evil */ 1")
        assert result.is_valid is False

    def test_multiple_statements_rejected(self, validator):
        result = validator._check_no_dangerous_patterns(
            "SELECT 1; DROP TABLE users"
        )
        assert result.is_valid is False

    def test_null_byte_rejected(self, validator):
        result = validator._check_no_dangerous_patterns("SELECT \x00 FROM users")
        assert result.is_valid is False

    def test_clean_query_passes(self, validator):
        result = validator._check_no_dangerous_patterns("SELECT name FROM users")
        assert result.is_valid is True


# ---------------------------------------------------------------------------
# _check_no_disallowed_keywords
# ---------------------------------------------------------------------------

class TestCheckNoDisallowedKeywords:
    def test_drop_in_select_rejected(self, validator):
        # Sneaky: "SELECT * FROM users DROP TABLE users"
        result = validator._check_no_disallowed_keywords(
            "SELECT * FROM users DROP TABLE users"
        )
        assert result.is_valid is False
        assert "DROP" in result.error

    def test_pragma_rejected(self, validator):
        result = validator._check_no_disallowed_keywords("SELECT PRAGMA")
        assert result.is_valid is False

    def test_clean_select_passes(self, validator):
        result = validator._check_no_disallowed_keywords(
            "SELECT name, age FROM users WHERE age > 18"
        )
        assert result.is_valid is True


# ---------------------------------------------------------------------------
# _check_tables_exist  (via full validate())
# ---------------------------------------------------------------------------

class TestTableValidation:
    def test_known_table_passes(self, validator, tmp_db):
        result = validator.validate("SELECT * FROM users", tmp_db)
        assert result.is_valid is True

    def test_unknown_table_fails(self, validator, tmp_db):
        result = validator.validate("SELECT * FROM ghost", tmp_db)
        assert result.is_valid is False
        assert "ghost" in result.error

    def test_join_both_tables_must_exist(self, validator, tmp_db):
        result = validator.validate(
            "SELECT * FROM users JOIN ghost ON users.id = ghost.user_id", tmp_db
        )
        assert result.is_valid is False
        assert "ghost" in result.error

    def test_join_all_known_tables_passes(self, validator, tmp_db):
        result = validator.validate(
            "SELECT * FROM users JOIN orders ON users.id = orders.user_id", tmp_db
        )
        assert result.is_valid is True


# ---------------------------------------------------------------------------
# _check_columns_exist  (via full validate())
# ---------------------------------------------------------------------------

class TestColumnValidation:
    def test_known_column_passes(self, validator, tmp_db):
        result = validator.validate("SELECT name FROM users", tmp_db)
        assert result.is_valid is True

    def test_unknown_column_fails(self, validator, tmp_db):
        result = validator.validate("SELECT ghost_col FROM users", tmp_db)
        assert result.is_valid is False
        assert "ghost_col" in result.error

    def test_wildcard_select_passes(self, validator, tmp_db):
        result = validator.validate("SELECT * FROM users", tmp_db)
        assert result.is_valid is True

    def test_qualified_column_passes(self, validator, tmp_db):
        result = validator.validate(
            "SELECT users.name FROM users", tmp_db
        )
        assert result.is_valid is True


# ---------------------------------------------------------------------------
# Full validate() integration
# ---------------------------------------------------------------------------

class TestValidateFull:
    def test_valid_query_with_where(self, validator, tmp_db):
        result = validator.validate(
            "SELECT name FROM users WHERE age > 20", tmp_db
        )
        assert result.is_valid is True

    def test_valid_query_with_limit(self, validator, tmp_db):
        result = validator.validate(
            "SELECT * FROM users LIMIT 5", tmp_db
        )
        assert result.is_valid is True

    def test_valid_aggregate_query(self, validator, tmp_db):
        result = validator.validate(
            "SELECT COUNT(*) FROM users", tmp_db
        )
        assert result.is_valid is True

    def test_empty_query_fails(self, validator, tmp_db):
        result = validator.validate("", tmp_db)
        assert result.is_valid is False

    def test_injection_attempt_fails(self, validator, tmp_db):
        result = validator.validate(
            "SELECT * FROM users; DROP TABLE users", tmp_db
        )
        assert result.is_valid is False

    def test_comment_injection_fails(self, validator, tmp_db):
        result = validator.validate(
            "SELECT * FROM users WHERE name='Alice' -- ignore rest", tmp_db
        )
        assert result.is_valid is False


# ---------------------------------------------------------------------------
# LLM-generated code was wrong — tests caught it
#
# Story: When asked to implement _check_no_disallowed_keywords, the LLM
# initially generated a version that split on whitespace only:
#
#     tokens = set(sql.upper().split())
#     found = tokens & self._DISALLOWED_KEYWORDS
#
# This approach FAILED for cases where disallowed keywords appeared:
#   - Attached to punctuation: "DROP," or "INSERT;"
#   - As part of a longer token:  "DROPPING" matched "DROP" unexpectedly
#   - Mixed into quoted strings:  "'INSERT'" was treated as a keyword
#
# The tests below caught both directions of the bug.
# The fix: use \b word-boundary regex — re.findall(r"\b[A-Za-z_]+\b", sql.upper())
# ---------------------------------------------------------------------------

class TestLLMGeneratedCodeWasWrong:
    """
    Demonstrates a case where the LLM-generated implementation was incorrect
    and these tests caught it, forcing a refined implementation.
    """

    def test_keyword_with_punctuation_is_caught(self, validator):
        # LLM version: "DROP," not in {"DROP"} → wrongly passed
        # Fixed version: word-boundary regex strips punctuation first
        result = validator._check_no_disallowed_keywords("SELECT * FROM users,DROP")
        assert result.is_valid is False, (
            "Bug: 'DROP' attached to punctuation should still be rejected. "
            "The original LLM split() approach missed this."
        )

    def test_keyword_with_semicolon_is_caught(self, validator):
        # LLM version: "INSERT;" not in {"INSERT"} → wrongly passed
        result = validator._check_no_disallowed_keywords("SELECT 1; INSERT;")
        assert result.is_valid is False, (
            "Bug: 'INSERT;' should be detected as the INSERT keyword. "
            "The original LLM split() approach missed this."
        )

    def test_partial_word_match_does_not_false_positive(self, validator):
        # The fix must NOT flag "DROPPING" as containing "DROP"
        # because \b[A-Za-z_]+\b extracts whole words only
        result = validator._check_no_disallowed_keywords(
            "SELECT dropping_count FROM metrics"
        )
        assert result.is_valid is True, (
            "Bug: 'dropping_count' is NOT the DROP keyword. "
            "A naive substring match would produce a false positive here."
        )

    def test_disallowed_word_in_column_alias_is_caught(self, validator):
        # "SELECT age AS drop FROM users" — DROP is a keyword even as alias
        result = validator._check_no_disallowed_keywords(
            "SELECT age AS drop FROM users"
        )
        assert result.is_valid is False
