import sqlite3
class QueryService:
  def __init__(self, db_path, validator, schema_manager):
    self.db_path = db_path
    self._validator = validator
    self._schema_manager = schema_manager
  def execute(self, sql)
    validation = self._validator.validate(sql, self.db_path)
    conn = sqlite3.connect(self.db_path)
    conn.row_factory = sqlite3.Row
  if not validation.is_valid:
    return (validation.error)
    
  
