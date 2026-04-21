Commands:
  load <path/to/file.csv> [table_name]  — load a CSV into the database
  query <natural language question>      — query via LLM (if configured)
  sql <raw SQL>                          — query with raw SQL (bypasses LLM)
  tables                                 — list all tables
  schema [table_name]                    — show schema for one or all tables
  help                                   — show this help
  exit / quit                            — exit the program
"""

import os
import sys
import logging
from pathlib import Path

from csv_loader.csv_loader import load_csv
from csv_loader.schema_manager import SchemaManager
from csv_loader.query_service import QueryService
from csv_loader.sql_validator import SQLValidator
from csv_loader.llm_adapter import LLMAdapter, AnthropicClient, OpenAIClient

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

BANNER = """
╔══════════════════════════════════════════╗
║     Natural Language SQL Assistant       ║
║     EC530 — Boston University            ║
╚══════════════════════════════════════════╝
Type 'help' for available commands.
"""

HELP_TEXT = """
Commands:
  load <file.csv> [table]   Load a CSV file into the database
  query <question>          Ask a question in plain English (requires LLM key)
  sql <SELECT ...>          Run a raw SQL SELECT query
  tables                    List all tables in the database
  schema                    Show schema for all tables
  schema <table>            Show schema for a specific table
  help                      Show this help message
  exit / quit               Exit the program
"""


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def _print_table(columns: list[str], rows: list[tuple]) -> None:
    """Print query results as a plain-text table."""
    if not rows:
        print("  (no results)")
        return

    # Calculate column widths
    widths = [len(c) for c in columns]
    for row in rows:
        for i, val in enumerate(row):
            widths[i] = max(widths[i], len(str(val) if val is not None else "NULL"))

    fmt = "  " + "  ".join(f"{{:<{w}}}" for w in widths)
    sep = "  " + "  ".join("-" * w for w in widths)

    print(fmt.format(*columns))
    print(sep)
    for row in rows:
        display = [str(v) if v is not None else "NULL" for v in row]
        print(fmt.format(*display))
    print(f"\n  {len(rows)} row(s) returned.")


def _print_schema(table: str, schema: list[dict]) -> None:
    print(f"\n  Table: {table}")
    print(f"  {'Column':<20} {'Type':<12} {'PK'}")
    print(f"  {'-'*20} {'-'*12} {'--'}")
    for col in schema:
        pk = "✓" if col.get("pk") else ""
        print(f"  {col['name']:<20} {col['type']:<12} {pk}")


# ---------------------------------------------------------------------------
# Command handlers
# ---------------------------------------------------------------------------

def cmd_load(args: list[str], db_path: str, schema_manager: SchemaManager) -> None:
    if not args:
        print("  Usage: load <file.csv> [table_name]")
        return

    csv_path = args[0]
    table_name = args[1] if len(args) > 1 else Path(csv_path).stem.lower()

    print(f"  Loading '{csv_path}' → table '{table_name}' ...")
    try:
        result = load_csv(
            csv_path=csv_path,
            db_path=db_path,
            table_name=table_name,
            schema_manager=schema_manager,
            if_exists="append",
        )
        if result["status"] == "skipped":
            print("  Skipped — schema mismatch or empty file.")
        else:
            print(f"  ✓ Inserted {result['rows_inserted']} rows into '{table_name}'.")
            print(f"  Columns: {', '.join(result['columns'])}")
    except FileNotFoundError:
        print(f"  Error: file not found — '{csv_path}'")
    except Exception as exc:
        print(f"  Error: {exc}")


def cmd_sql(args: list[str], query_service: QueryService) -> None:
    if not args:
        print("  Usage: sql <SELECT statement>")
        return
    sql = " ".join(args)
    result = query_service.execute(sql)
    if result.success:
        _print_table(result.columns, result.rows)
    else:
        print(f"  Error: {result.error}")


def cmd_query(args: list[str], adapter: LLMAdapter | None) -> None:
    if adapter is None:
        print("  LLM not configured. Set OPENAI_API_KEY or ANTHROPIC_API_KEY.")
        return
    if not args:
        print("  Usage: query <natural language question>")
        return

    question = " ".join(args)
    print(f"  Thinking ...")
    result = adapter.query(question)

    if result.generated_sql:
        print(f"  Generated SQL: {result.generated_sql}")

    if result.success:
        _print_table(result.query_result.columns, result.query_result.rows)
    else:
        print(f"  Error: {result.error}")


def cmd_tables(query_service: QueryService) -> None:
    tables = query_service.list_tables()
    if not tables:
        print("  No tables found. Use 'load' to add data.")
    else:
        print(f"  Tables ({len(tables)}):")
        for t in tables:
            print(f"    • {t}")


def cmd_schema(args: list[str], query_service: QueryService) -> None:
    context = query_service.get_schema_context()
    if not context:
        print("  No tables found.")
        return
    targets = [args[0]] if args and args[0] in context else list(context.keys())
    if args and args[0] not in context:
        print(f"  Unknown table '{args[0]}'. Available: {', '.join(context.keys())}")
        return
    for table in targets:
        _print_schema(table, context[table])


# ---------------------------------------------------------------------------
# LLM setup
# ---------------------------------------------------------------------------

def _build_llm_adapter(query_service: QueryService) -> LLMAdapter | None:
    """Try to build an LLM adapter from environment variables."""
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")

    if anthropic_key:
        print("  LLM: using Anthropic Claude (claude-haiku-4-5-20251001)")
        return LLMAdapter(query_service, AnthropicClient(anthropic_key))
    if openai_key:
        print("  LLM: using OpenAI (gpt-4o-mini)")
        return LLMAdapter(query_service, OpenAIClient(openai_key))

    print("  LLM: not configured (set ANTHROPIC_API_KEY or OPENAI_API_KEY)")
    return None


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def run(db_path: str = "data.db") -> None:
    schema_manager = SchemaManager()
    validator = SQLValidator()
    query_service = QueryService(db_path, validator, schema_manager)
    adapter = _build_llm_adapter(query_service)

    print(BANNER)
    print(f"  Database: {db_path}")

    while True:
        try:
            raw = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  Goodbye.")
            break

        if not raw:
            continue

        parts = raw.split()
        command = parts[0].lower()
        args = parts[1:]

        if command in ("exit", "quit"):
            print("  Goodbye.")
            break
        elif command == "help":
            print(HELP_TEXT)
        elif command == "load":
            cmd_load(args, db_path, schema_manager)
        elif command == "sql":
            cmd_sql(args, query_service)
        elif command == "query":
            cmd_query(args, adapter)
        elif command == "tables":
            cmd_tables(query_service)
        elif command == "schema":
            cmd_schema(args, query_service)
        else:
            print(f"  Unknown command '{command}'. Type 'help' for options.")


if __name__ == "__main__":
    db = sys.argv[1] if len(sys.argv) > 1 else "data.db"
    run(db)
