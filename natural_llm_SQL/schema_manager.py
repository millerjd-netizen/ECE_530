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
  
