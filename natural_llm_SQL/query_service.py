import sqlite3


class QueryResult:
    def __init__(self, success=True, rows=None, columns=None, sql="", error=None):
        self.success = success
        self.rows = rows or []
        self.columns = columns or []
        self.sql = sql
        self.error = error

    def as_dicts(self):
        return [dict(zip(self.columns, row)) for row in self.rows]


class QueryService:
    def __init__(self, db_path=None, validator=None, schema_manager=None):
        self.db_path = db_path
        self.validator = validator
        self.schema_manager = schema_manager

    def execute(self, sql: str):
        if not sql.strip():
            return QueryResult(success=False, error="Empty query")

        if self.validator and not self.validator.validate(sql, self.db_path):
            return QueryResult(success=False, error="Validation failed")

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute(sql)

            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description] if cursor.description else []

            return QueryResult(True, rows, columns, sql)

        except Exception as e:
            return QueryResult(False, error=str(e))

    def list_tables(self):
        conn = sqlite3.connect(self.db_path)
        return self.schema_manager.list_tables(conn)

    def get_schema_context(self):
        conn = sqlite3.connect(self.db_path)
        tables = self.schema_manager.list_tables(conn)

        return {
            table: self.schema_manager.get_schema(conn, table)
            for table in tables
        }
