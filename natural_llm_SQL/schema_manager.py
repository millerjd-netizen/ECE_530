import sqlite3

# Type normalization helpers

_AFFINITY_MAP = {
    # Exact SQLite affinity names
    "TEXT": "TEXT",
    "INTEGER": "INTEGER",
    "REAL": "REAL",
    "NUMERIC": "NUMERIC",
    "BLOB": "BLOB",
    # Common aliases
    "VARCHAR": "TEXT",
    "CHAR": "TEXT",
    "CLOB": "TEXT",
    "INT": "INTEGER",
    "TINYINT": "INTEGER",
    "SMALLINT": "INTEGER",
    "BIGINT": "INTEGER",
    "FLOAT": "REAL",
    "DOUBLE": "REAL",
    "BOOLEAN": "INTEGER",
}

def _normalize_type(type_str: str) -> str:
    """Map any SQL type string to a canonical SQLite affinity."""
    return _AFFINITY_MAP.get(type_str.upper().split("(")[0].strip(), "TEXT")


def _normalize_name(name: str) -> str:
    """Lowercase and strip a column name for comparison."""
    return name.strip().lower()

class SchemaManager:
  def list_tables(self, conn)
     cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
    return [row[0] for row in cursor.fetchall()]
  def get_schema(
        self, conn: sqlite3.Connection, table_name: str
    ) -> list[dict]:
    
        cursor = conn.execute(f"PRAGMA table_info({table_name})")
        rows = cursor.fetchall()
         return [
            {
                "name": row[1],
                "type": _normalize_type(row[2])",
                "pk": row[5],
            }
  def create_table(self, schema)
    col_defs = ["Primary Key"]
    for col in schema:
      col_defs.append(f"{col['name'] col['type']}")
    conn.execute(f"CREATE TABLE {table_name} ({', '.join(col_defs)})")
  def drop_table(self, conn, table_name)
    conn.execute(f"DROP TABLE {table_name}")
  def rename_table(self, conn, table_name)
    conn.execute(f"ALTER TABLE {old_name} RENAME TO {new_name}")

    def schemas_compatible(
            self,
            existing: list[dict],
            incoming: list[dict],
        ) -> bool:
   for col in incoming:
            name = _normalize_name(col["name"])
            expected_type = _normalize_type(col["type"])
            if existing_lookup[name] != expected_type:
                    print("Incompatible: column '%s' type mismatch (%s vs %s)",
                    name, existing_lookup[name], expected_type)
                )
                return False

        return True

 def drop_table(self, conn: sqlite3.Connection, table_name: str) -> None:
     conn.execute(f"DROP TABLE IF EXISTS {table_name}")

"""
schema_manager.py

Responsible for understanding the STRUCTURE of the database — not its data.

Responsibilities:
  - Discover existing tables
  - Return table schemas as structured objects (list of {name, type} dicts)
  - Compare schemas to determine compatibility (append vs create)
  - Create and drop tables
  - Add an auto-increment primary key to every new table

Does NOT:
  - Execute SELECT/INSERT/UPDATE queries
  - Call the LLM
  - Handle user input
"""

import sqlite3
import logging

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Type normalization helpers
# ---------------------------------------------------------------------------

_AFFINITY_MAP = {
    # Exact SQLite affinity names
    "TEXT": "TEXT",
    "INTEGER": "INTEGER",
    "REAL": "REAL",
    "NUMERIC": "NUMERIC",
    "BLOB": "BLOB",
    # Common aliases
    "VARCHAR": "TEXT",
    "CHAR": "TEXT",
    "CLOB": "TEXT",
    "INT": "INTEGER",
    "TINYINT": "INTEGER",
    "SMALLINT": "INTEGER",
    "BIGINT": "INTEGER",
    "FLOAT": "REAL",
    "DOUBLE": "REAL",
    "BOOLEAN": "INTEGER",
}


def _normalize_type(type_str: str) -> str:
    """Map any SQL type string to a canonical SQLite affinity."""
    return _AFFINITY_MAP.get(type_str.upper().split("(")[0].strip(), "TEXT")


def _normalize_name(name: str) -> str:
    """Lowercase and strip a column name for comparison."""
    return name.strip().lower()


# ---------------------------------------------------------------------------
# SchemaManager
# ---------------------------------------------------------------------------

class SchemaManager:
    """
    All schema-level operations on a SQLite database.

    Every method accepts an open sqlite3.Connection so the caller
    controls transactions and connection lifecycle.
    """

    # ------------------------------------------------------------------
    # Discovery
    # ------------------------------------------------------------------

    def list_tables(self, conn: sqlite3.Connection) -> list[str]:
        """Return names of all user-created tables in the database."""
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        return [row[0] for row in cursor.fetchall()]

    def table_exists(self, conn: sqlite3.Connection, table_name: str) -> bool:
        """Return True if the named table exists."""
        cursor = conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,),
        )
        return cursor.fetchone() is not None

    def get_schema(
        self, conn: sqlite3.Connection, table_name: str
    ) -> list[dict]:
        """
        Return the schema of an existing table as a list of column dicts.

        Each dict has keys:
            name  (str)  — column name
            type  (str)  — SQLite type affinity (normalised)
            pk    (int)  — 1 if part of primary key, else 0
        """
        if not self.table_exists(conn, table_name):
            raise ValueError(f"Table '{table_name}' does not exist.")

        cursor = conn.execute(f"PRAGMA table_info({table_name})")
        rows = cursor.fetchall()
        # PRAGMA columns: cid, name, type, notnull, dflt_value, pk
        return [
            {
                "name": row[1],
                "type": _normalize_type(row[2]) if row[2] else "TEXT",
                "pk": row[5],
            }
            for row in rows
        ]

    # ------------------------------------------------------------------
    # Schema comparison
    # ------------------------------------------------------------------

    def schemas_compatible(
        self,
        existing: list[dict],
        incoming: list[dict],
    ) -> bool:
        """
        Return True if the incoming schema can be appended to the existing table.

        Compatibility rules:
          - Column names match (after normalization, order-independent)
          - Column types match (after normalization)
          - The existing table may have extra columns (e.g. the auto-added `id`)
            as long as all incoming columns are present and type-compatible.
        """
        if not incoming:
            return False

        existing_lookup = {
            _normalize_name(col["name"]): _normalize_type(col["type"])
            for col in existing
        }

        for col in incoming:
            name = _normalize_name(col["name"])
            expected_type = _normalize_type(col["type"])
            if name not in existing_lookup:
                logger.debug("Incompatible: column '%s' not in existing table", name)
                return False
            if existing_lookup[name] != expected_type:
                logger.debug(
                    "Incompatible: column '%s' type mismatch (%s vs %s)",
                    name, existing_lookup[name], expected_type,
                )
                return False

        return True

    # ------------------------------------------------------------------
    # DDL operations
    # ------------------------------------------------------------------

    def create_table(
        self,
        conn: sqlite3.Connection,
        table_name: str,
        schema: list[dict],
    ) -> None:
        """
        Create a new table with an auto-increment primary key prepended.

        The `id` column is always added as:
            id INTEGER PRIMARY KEY AUTOINCREMENT
        """
        if not schema:
            raise ValueError("Cannot create a table with an empty schema.")

        col_defs = ["id INTEGER PRIMARY KEY AUTOINCREMENT"]
        for col in schema:
            col_defs.append(f"{col['name']} {_normalize_type(col['type'])}")

        ddl = f"CREATE TABLE {table_name} ({', '.join(col_defs)})"
        logger.debug("DDL: %s", ddl)
        conn.execute(ddl)
        logger.info("Created table '%s' with %d columns", table_name, len(schema))

    def drop_table(self, conn: sqlite3.Connection, table_name: str) -> None:
        """Drop a table if it exists."""
        conn.execute(f"DROP TABLE IF EXISTS {table_name}")
        logger.info("Dropped table '%s'", table_name)

    def rename_table(
        self, conn: sqlite3.Connection, old_name: str, new_name: str
    ) -> None:
       
        conn.execute(f"ALTER TABLE {old_name} RENAME TO {new_name}")
       
