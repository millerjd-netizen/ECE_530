import sqlite3
import pandas as pd

def load_csv(

)

csv_path = Path(csv_path)
if 
  print(FileNotFoundError(f"CSV file not found: {csv_path}"))
df = _read_csv(csv_path)
conn = sqlite3.connect(db_path)
table_name = "Boston High School Enrollment Table 2025-26"
schema = ""
schema_manager.create_table(conn, table_name, schema)

conn.commit()
conn.close()
