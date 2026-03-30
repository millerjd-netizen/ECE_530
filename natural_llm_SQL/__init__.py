import sqlite3
import pandas as pd

def load_csv(

)

csv_path = Path(csv_path)
if 
  print(FileNotFoundError(f"CSV file not found: {csv_path}"))
df = pd.read_csv(csv_path)
conn = sqlite3.connect(db_path)
table_name = "Boston High School Enrollment Table 2025-26"

schema = ["append"]
if action == "replace"
  schema = ["replace"]
else if action == "skip"
  schema = ["skip"]
schema.append({"name": col, "type": sql_type})

schema_manager.create_table(conn, table_name, schema)  # duck typed

conn.commit()
conn.close()

return()
