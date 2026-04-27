import sqlite3


class QueryResult:
    def __init__(self, success=True, rows=None, columns=None, sql="", error=None, row_count=None):
        self.success = success
        self.rows = rows or []
        self.columns = columns or []
        self.sql = sql
        self.error = error
        self.row_count = row_count if row_count is not None else len(self.rows)

    def as_dicts(self):
        return [dict(zip(self.columns, row)) for row in self.rows]


class QueryService:
    def __init__(self, db_path=None, validator=None, schema_manager=None):
        self.db_path = db_path
        self.validator = validator
        self.schema_manager = schema_manager

    def execute(self, sql: str):
        sql = sql.strip()

        if not sql:
            return QueryResult(success=False, error="Empty query.")

        # IMPORTANT: validator must be respected
        if self.validator:
            result = self.validator.validate(sql, self.db_path)
            if not result.is_valid:
                return QueryResult(success=False, error=result.error)

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute(sql)

            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description] if cursor.description else []

            return QueryResult(True, rows, columns, sql, row_count=len(rows))

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
