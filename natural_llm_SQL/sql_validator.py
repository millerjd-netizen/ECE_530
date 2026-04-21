import re
import sqlite3
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    is_valid: bool
    error: str = ""

class SQLValidator:
    """
    Validates a SQL query string against the structure of a SQLite database.

    All validation is structural — tables, columns, query type — not
    full grammar parsing.
    """

    # Characters that suggest injection or non-query intent
    _DANGEROUS_PATTERNS = [
        r"--",           # line comment (SQL injection vector)
        r"/\*",          # block comment open
        r"\*/",          # block comment close
        r";.+",          # multiple statements (anything after first semicolon)
        r"\x00",         # null byte
    ]

    # DML/DDL keywords that are never allowed
    _DISALLOWED_KEYWORDS = {
        "INSERT", "UPDATE", "DELETE", "DROP", "CREATE", "ALTER",
        "REPLACE", "TRUNCATE", "ATTACH", "DETACH", "PRAGMA",
    }

    def validate(self, sql: str, db_path: str) -> ValidationResult:
        """
        Validate a SQL query against the database at db_path.

        Checks (in order):
          1. Not empty
          2. No dangerous patterns (injection vectors)
          3. Must be a SELECT statement
          4. No disallowed DML/DDL keywords anywhere in the query
          5. All referenced tables exist in the database
          6. All referenced columns exist in their respective tables

        Returns a ValidationResult with is_valid=True or is_valid=False + error.
        """
        sql = sql.strip()

        result = self._check_not_empty(sql)
        if not result.is_valid:
            return result

        result = self._check_no_dangerous_patterns(sql)
        if not result.is_valid:
            return result

        result = self._check_is_select(sql)
        if not result.is_valid:
            return result

        result = self._check_no_disallowed_keywords(sql)
        if not result.is_valid:
            return result

        try:
            conn = sqlite3.connect(db_path)
            try:
                result = self._check_tables_exist(sql, conn)
                if not result.is_valid:
                    return result

                result = self._check_columns_exist(sql, conn)
                if not result.is_valid:
                    return result
            finally:
                conn.close()
        except sqlite3.Error as exc:
            return ValidationResult(is_valid=False, error=f"Database error: {exc}")

        return ValidationResult(is_valid=True)

    # ------------------------------------------------------------------
    # Individual checks
    # ------------------------------------------------------------------

    def _check_not_empty(self, sql: str) -> ValidationResult:
        if not sql:
            return ValidationResult(is_valid=False, error="Query is empty.")
        return ValidationResult(is_valid=True)

    def _check_no_dangerous_patterns(self, sql: str) -> ValidationResult:
        for pattern in self._DANGEROUS_PATTERNS:
            if re.search(pattern, sql, re.IGNORECASE):
                return ValidationResult(
                    is_valid=False,
                    error=f"Query contains disallowed pattern: '{pattern}'.",
                )
        return ValidationResult(is_valid=True)

    def _check_is_select(self, sql: str) -> ValidationResult:
        first_token = sql.split()[0].upper()
        if first_token != "SELECT":
            return ValidationResult(
                is_valid=False,
                error=f"Only SELECT queries are allowed. Got: '{first_token}'.",
            )
        return ValidationResult(is_valid=True)

    def _check_no_disallowed_keywords(self, sql: str) -> ValidationResult:
        tokens = set(re.findall(r"\b[A-Za-z_]+\b", sql.upper()))
        found = tokens & self._DISALLOWED_KEYWORDS
        if found:
            return ValidationResult(
                is_valid=False,
                error=f"Query contains disallowed keyword(s): {sorted(found)}.",
            )
        return ValidationResult(is_valid=True)

    def _check_tables_exist(
        self, sql: str, conn: sqlite3.Connection
    ) -> ValidationResult:
        """
        Extract table names from FROM and JOIN clauses and verify they exist.
        """
        referenced = _extract_table_names(sql)
        if not referenced:
            return ValidationResult(is_valid=True)

        existing = _get_existing_tables(conn)
        unknown = referenced - existing
        if unknown:
            return ValidationResult(
                is_valid=False,
                error=f"Query references unknown table(s): {sorted(unknown)}.",
            )
        return ValidationResult(is_valid=True)

    def _check_columns_exist(
        self, sql: str, conn: sqlite3.Connection
    ) -> ValidationResult:
        """
        For each table referenced in the query, verify that any explicitly
        named columns (table.column or bare column names in SELECT) exist.

        Uses a lightweight approach: attempt EXPLAIN on the query and let
        SQLite's own parser catch unknown columns. This avoids re-implementing
        SQL column parsing.
        """
        try:
            conn.execute(f"EXPLAIN {sql}")
        except sqlite3.OperationalError as exc:
            error_msg = str(exc)
            # SQLite reports "no such column: X" for unknown columns
            if "no such column" in error_msg or "no such table" in error_msg:
                return ValidationResult(is_valid=False, error=error_msg)
            # Other operational errors (e.g. syntax) also fail validation
            return ValidationResult(is_valid=False, error=f"SQL error: {error_msg}")
        return ValidationResult(is_valid=True)


# ---------------------------------------------------------------------------
# Helpers (module-level, independently testable)
# ---------------------------------------------------------------------------

def _extract_table_names(sql: str) -> set[str]:
    """
    Extract table names from FROM and JOIN clauses using regex.

    Handles:
      - FROM table
      - FROM table alias
      - JOIN table
      - Multiple joins
      - Subqueries are ignored (we don't descend into parens)

    Returns a set of lowercase table name strings.
    """
    # Match FROM or JOIN followed by an identifier (not a subquery)
    pattern = r"\b(?:FROM|JOIN)\s+([A-Za-z_][A-Za-z0-9_]*)"
    matches = re.findall(pattern, sql, re.IGNORECASE)
    return {m.lower() for m in matches}


def _get_existing_tables(conn: sqlite3.Connection) -> set[str]:
    """Return the set of lowercase table names in the database."""
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    )
    return {row[0].lower() for row in cursor.fetchall()}
