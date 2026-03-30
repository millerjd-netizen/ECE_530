import sqlite3

class SchemaManager:
  def list_tables(self, conn)
  def get_schema(self, conn, table_name)
  def create_table(self, schema)
    col_defs = ["Primary Key"]
    for col in schema:
      col_defs.append(f"{col['name'] col['type']}")
  conn.execute(f"CREATE TABLE {schema.table_name) ({', ', join(col_defs)})
  
