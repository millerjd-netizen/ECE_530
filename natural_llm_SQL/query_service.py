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

        if self.validator:
            validation = self.validator.validate(sql, self.db_path)
            if hasattr(validation, "is_valid"):
                if not validation.is_valid:
                    return QueryResult(success=False, error=validation.error)
            elif validation is False:
                return QueryResult(success=False, error="Validation failed.")

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.execute(sql)

            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description] if cursor.description else []

            return QueryResult(success=True, rows=rows, columns=columns, sql=sql)

        except Exception as e:
            return QueryResult(success=False, error=str(e), sql=sql)

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