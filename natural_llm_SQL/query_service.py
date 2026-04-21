import sqlite3
import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class QueryResult:
    """Structured result returned from every query execution."""
    sql: str
    columns: list[str]
    rows: list[tuple]
    row_count: int
    success: bool
    error: str = ""

    @property
    def as_dicts(self) -> list[dict]:
        """Return rows as a list of column→value dicts."""
        return [dict(zip(self.columns, row)) for row in self.rows]

class QueryService:
    """
    Executes validated SQL queries against a SQLite database.

    Parameters
    ----------
    db_path        : path to the SQLite database file
    validator      : SQL/DB Validator instance (injected dependency)
    schema_manager : SchemaManager instance (injected dependency)
    """

    def __init__(self, db_path: str, validator, schema_manager):
        self.db_path = db_path
        self._validator = validator
        self._schema_manager = schema_manager
# ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def execute(self, sql: str) -> QueryResult:
        """
        Validate and execute a SQL query.

        Flow:
          1. Validate the query via the injected validator
          2. Open a connection (read-only via URI if possible)
          3. Execute the query
          4. Return a QueryResult

        The validator decides whether the query is safe to run.
        This method never executes a query the validator rejects.
        """
        sql = sql.strip()
        if not sql:
            return QueryResult(
                sql=sql, columns=[], rows=[], row_count=0,
                success=False, error="Empty query."
            )

        # Step 1: validate
        validation = self._validator.validate(sql, self.db_path)
        if not validation.is_valid:
            logger.warning("Query rejected by validator: %s", validation.error)
            return QueryResult(
                sql=sql, columns=[], rows=[], row_count=0,
                success=False, error=validation.error,
            )

        # Step 2 & 3: execute
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            try:
                cursor = conn.execute(sql)
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description] if cursor.description else []
                tupled_rows = [tuple(row) for row in rows]
                logger.info("Query returned %d rows", len(tupled_rows))
                return QueryResult(
                    sql=sql,
                    columns=columns,
                    rows=tupled_rows,
                    row_count=len(tupled_rows),
                    success=True,
                )
            finally:
                conn.close()
        except sqlite3.Error as exc:
            logger.error("SQLite error during execution: %s", exc)
            return QueryResult(
                sql=sql, columns=[], rows=[], row_count=0,
                success=False, error=str(exc),
            )
          def get_schema_context(self) -> dict:
        """
        Return a schema summary for all tables — used by the LLM Adapter
        to build prompts with the current database structure.

        Returns
        -------
        dict mapping table_name → list of {name, type} column dicts
        """
        conn = sqlite3.connect(self.db_path)
        try:
            tables = self._schema_manager.list_tables(conn)
            return {
                table: self._schema_manager.get_schema(conn, table)
                for table in tables
            }
        finally:
            conn.close()

    def list_tables(self) -> list[str]:
        """Return all table names in the database."""
        conn = sqlite3.connect(self.db_path)
        try:
            return self._schema_manager.list_tables(conn)
        finally:
            conn.close()
