import sqlite3


def _normalize_name(name: str) -> str:
    return name.strip().lower()


def _normalize_type(t: str) -> str:
    t = t.strip().upper()

    if "(" in t:
        t = t.split("(")[0]

    if t in ("TEXT", "VARCHAR", "CHAR", "CLOB"):
        return "TEXT"
    if t in ("INTEGER", "INT", "TINYINT", "SMALLINT", "BIGINT", "BOOLEAN"):
        return "INTEGER"
    if t in ("REAL", "FLOAT", "DOUBLE"):
        return "REAL"

    return "TEXT"


class SchemaManager:
    def list_tables(self, conn):
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        return sorted([row[0] for row in cursor.fetchall()])

    def table_exists(self, conn, name):
        return name in self.list_tables(conn)

    def get_schema(self, conn, table):
        if not self.table_exists(conn, table):
            raise ValueError(f"{table} does not exist")

        cursor = conn.execute(f"PRAGMA table_info({table})")
        schema = []
        for col in cursor.fetchall():
            schema.append({
                "name": col[1],
                "type": _normalize_type(col[2]),
                "pk": col[5],
            })
        return schema
