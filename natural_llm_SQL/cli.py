import os
import sqlite3
import sys

DB_PATH = "demo.db"


def connect():
    return sqlite3.connect(DB_PATH)


def init_demo_db():
    conn = connect()
    conn.execute("DROP TABLE IF EXISTS users")
    conn.execute(
        """
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            name TEXT,
            age INTEGER,
            role TEXT
        )
        """
    )
    conn.executemany(
        "INSERT INTO users (name, age, role) VALUES (?, ?, ?)",
        [
            ("Alice", 30, "engineer"),
            ("Bob", 25, "designer"),
            ("Carol", 41, "manager"),
        ],
    )
    conn.commit()
    print("Demo database created: demo.db")


def list_tables():
    conn = connect()
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()
    for row in rows:
        print(row[0])


def schema_text():
    conn = connect()
    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()

    parts = []
    for (table,) in tables:
        cols = conn.execute(f"PRAGMA table_info({table})").fetchall()
        col_text = ", ".join([f"{c[1]} {c[2]}" for c in cols])
        parts.append(f"{table}({col_text})")
    return "\n".join(parts)


def execute_sql(sql):
    sql = sql.strip().rstrip(";")

    if not sql.lower().startswith("select"):
        print("Only SELECT queries are allowed.")
        return

    conn = connect()
    cursor = conn.execute(sql)
    columns = [d[0] for d in cursor.description]
    rows = cursor.fetchall()

    print("SQL:", sql)
    print("Columns:", columns)
    for row in rows:
        print(row)


def simulated_llm_to_sql(question):
    print("LLM simulated processing:", question)

    q = question.lower()

    if "engineer" in q:
        return "SELECT * FROM users WHERE role = 'engineer'"

    if "designer" in q:
        return "SELECT * FROM users WHERE role = 'designer'"

    if "manager" in q:
        return "SELECT * FROM users WHERE role = 'manager'"

    if "age" in q:
        return "SELECT name, age FROM users"

    if "tables" in q:
        return "SELECT name FROM sqlite_master WHERE type = 'table'"

    return "SELECT * FROM users"


def real_llm_to_sql(question):
    api_key = os.environ.get("OPENAI_API_KEY")

    if not api_key:
        return None

    try:
        from openai import OpenAI
    except ImportError:
        print("openai package missing. Run: pip install openai")
        return None

    client = OpenAI(api_key=api_key)

    prompt = f"""
You convert natural language questions into safe SQLite SELECT queries.

Rules:
- Return only one SQL SELECT statement.
- Do not include markdown.
- Do not include explanations.
- Never return INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, or PRAGMA.
- Use only the schema below.

Database schema:
{schema_text()}

Question:
{question}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        sql = response.choices[0].message.content.strip()
        print("LLM OpenAI processing:", question)
        return sql
    except Exception as exc:
        print("OpenAI request failed:", exc)
        return None


def nl_to_sql(question):
    sql = real_llm_to_sql(question)

    if sql:
        return sql

    print("Real LLM unavailable. Falling back to simulated LLM.")
    return simulated_llm_to_sql(question)


def status():
    print("Database:", DB_PATH)
    print("OpenAI key configured:", bool(os.environ.get("OPENAI_API_KEY")))


def help_text():
    print("Usage:")
    print("  python cli.py init-demo")
    print("  python cli.py status")
    print("  python cli.py tables")
    print("  python cli.py sql \"SELECT * FROM users\"")
    print("  python cli.py query \"show all users\"")
    print("")
    print("Real LLM mode:")
    print("  export OPENAI_API_KEY=your_key")


def main():
    if len(sys.argv) < 2:
        help_text()
        return

    command = sys.argv[1]

    if command == "init-demo":
        init_demo_db()
    elif command == "status":
        status()
    elif command == "tables":
        list_tables()
    elif command == "sql":
        execute_sql(" ".join(sys.argv[2:]))
    elif command == "query":
        question = " ".join(sys.argv[2:])
        sql = nl_to_sql(question)
        if sql:
            execute_sql(sql)
    else:
        help_text()


if __name__ == "__main__":
    main()