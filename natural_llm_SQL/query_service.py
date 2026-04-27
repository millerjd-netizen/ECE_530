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
        return [
            {"name": col[1], "type": _normalize_type(col[2]), "pk": col[5]}
            for col in cursor.fetchall()
        ]

    def create_table(self, conn, name, columns):
        if not columns:
            raise ValueError("empty schema")

        sql_columns = ["id INTEGER PRIMARY KEY"]
        for col in columns:
            sql_columns.append(f"{col['name']} {_normalize_type(col['type'])}")

        conn.execute(f"CREATE TABLE {name} ({', '.join(sql_columns)})")

    def drop_table(self, conn, name):
        conn.execute(f"DROP TABLE IF EXISTS {name}")

    def rename_table(self, conn, old, new):
        if not self.table_exists(conn, old):
            raise ValueError(f"{old} does not exist")
        conn.execute(f"ALTER TABLE {old} RENAME TO {new}")

    def schemas_compatible(self, existing, incoming):
        if not existing or not incoming:
            return False

        existing_map = {c["name"].lower(): _normalize_type(c["type"]) for c in existing}
        incoming_map = {c["name"].lower(): _normalize_type(c["type"]) for c in incoming}

        for name, typ in incoming_map.items():
            if name not in existing_map:
                return False
            if existing_map[name] != typ:
                return False

        return True