import pytest
from unittest.mock import MagicMock

from csv_loader.llm_adapter import (
    LLMAdapter,
    AdapterResult,
    build_prompt,
    extract_sql,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_query_service(
    schema_context=None,
    execute_success=True,
    execute_rows=None,
    execute_columns=None,
    execute_error="",
):
    """Return a mock QueryService."""
    qs = MagicMock()
    qs.get_schema_context.return_value = schema_context or {}

    result = MagicMock()
    result.success = execute_success
    result.rows = execute_rows or []
    result.columns = execute_columns or []
    result.error = execute_error
    qs.execute.return_value = result
    return qs


def make_llm_client(response: str):
    """Return a mock LLM client that returns a fixed response."""
    client = MagicMock()
    client.complete.return_value = response
    return client


SAMPLE_SCHEMA = {
    "users": [
        {"name": "id", "type": "INTEGER", "pk": 1},
        {"name": "name", "type": "TEXT", "pk": 0},
        {"name": "age", "type": "INTEGER", "pk": 0},
    ]
}

VALID_LLM_RESPONSE = """
Here is the SQL query:

```sql
SELECT name, age FROM users WHERE age > 20
```

This query returns all users older than 20.
"""

BARE_SQL_RESPONSE = "SELECT name FROM users LIMIT 5"

NO_SQL_RESPONSE = "I'm sorry, I don't understand the question."


# ---------------------------------------------------------------------------
# build_prompt
# ---------------------------------------------------------------------------

class TestBuildPrompt:
    def test_contains_user_question(self):
        prompt = build_prompt("show all users", SAMPLE_SCHEMA)
        assert "show all users" in prompt

    def test_contains_table_name(self):
        prompt = build_prompt("anything", SAMPLE_SCHEMA)
        assert "users" in prompt

    def test_contains_column_names(self):
        prompt = build_prompt("anything", SAMPLE_SCHEMA)
        assert "name" in prompt
        assert "age" in prompt

    def test_empty_schema_handled(self):
        prompt = build_prompt("anything", {})
        assert "(no tables)" in prompt

    def test_select_only_rule_present(self):
        prompt = build_prompt("anything", SAMPLE_SCHEMA)
        assert "SELECT" in prompt

    def test_multiple_tables_all_present(self):
        schema = {
            "users": [{"name": "id", "type": "INTEGER", "pk": 1}],
            "orders": [{"name": "total", "type": "REAL", "pk": 0}],
        }
        prompt = build_prompt("anything", schema)
        assert "users" in prompt
        assert "orders" in prompt


# ---------------------------------------------------------------------------
# extract_sql
# ---------------------------------------------------------------------------

class TestExtractSQL:
    def test_fenced_code_block(self):
        response = "Here it is:\n```sql\nSELECT * FROM users\n```\nDone."
        assert extract_sql(response) == "SELECT * FROM users"

    def test_fenced_block_case_insensitive(self):
        response = "```SQL\nSELECT 1\n```"
        assert extract_sql(response) == "SELECT 1"

    def test_strips_whitespace_inside_block(self):
        response = "```sql\n  SELECT * FROM t  \n```"
        assert extract_sql(response) == "SELECT * FROM t"

    def test_fallback_bare_select(self):
        assert extract_sql(BARE_SQL_RESPONSE) == "SELECT name FROM users LIMIT 5"

    def test_no_sql_returns_empty_string(self):
        assert extract_sql(NO_SQL_RESPONSE) == ""

    def test_prefers_fenced_block_over_bare(self):
        response = "SELECT wrong FROM t\n```sql\nSELECT right FROM t\n```"
        assert extract_sql(response) == "SELECT right FROM t"

    def test_multiline_sql_in_block(self):
        response = "```sql\nSELECT name\nFROM users\nWHERE age > 20\n```"
        sql = extract_sql(response)
        assert "SELECT name" in sql
        assert "FROM users" in sql


# ---------------------------------------------------------------------------
# LLMAdapter.query — happy path
# ---------------------------------------------------------------------------

class TestAdapterHappyPath:
    def test_success_returns_true(self):
        qs = make_query_service(schema_context=SAMPLE_SCHEMA, execute_success=True)
        adapter = LLMAdapter(qs, make_llm_client(VALID_LLM_RESPONSE))
        result = adapter.query("show users older than 20")
        assert result.success is True

    def test_generated_sql_extracted_correctly(self):
        qs = make_query_service(schema_context=SAMPLE_SCHEMA)
        adapter = LLMAdapter(qs, make_llm_client(VALID_LLM_RESPONSE))
        result = adapter.query("show users older than 20")
        assert "SELECT" in result.generated_sql.upper()

    def test_query_service_execute_called_with_extracted_sql(self):
        qs = make_query_service(schema_context=SAMPLE_SCHEMA)
        adapter = LLMAdapter(qs, make_llm_client(VALID_LLM_RESPONSE))
        adapter.query("show users older than 20")
        qs.execute.assert_called_once()
        called_sql = qs.execute.call_args[0][0]
        assert "SELECT" in called_sql.upper()

    def test_natural_language_query_preserved_in_result(self):
        qs = make_query_service(schema_context=SAMPLE_SCHEMA)
        adapter = LLMAdapter(qs, make_llm_client(VALID_LLM_RESPONSE))
        result = adapter.query("show all users")
        assert result.natural_language_query == "show all users"

    def test_raw_llm_response_stored(self):
        qs = make_query_service(schema_context=SAMPLE_SCHEMA)
        adapter = LLMAdapter(qs, make_llm_client(VALID_LLM_RESPONSE))
        result = adapter.query("anything")
        assert result.raw_llm_response == VALID_LLM_RESPONSE

    def test_query_result_attached(self):
        qs = make_query_service(schema_context=SAMPLE_SCHEMA, execute_success=True)
        adapter = LLMAdapter(qs, make_llm_client(VALID_LLM_RESPONSE))
        result = adapter.query("anything")
        assert result.query_result is not None


# ---------------------------------------------------------------------------
# LLMAdapter.query — failure cases
# ---------------------------------------------------------------------------

class TestAdapterFailureCases:
    def test_empty_query_returns_failure(self):
        qs = make_query_service()
        adapter = LLMAdapter(qs, make_llm_client(""))
        result = adapter.query("   ")
        assert result.success is False
        assert "Empty" in result.error

    def test_empty_query_does_not_call_llm(self):
        client = make_llm_client("")
        adapter = LLMAdapter(make_query_service(), client)
        adapter.query("")
        client.complete.assert_not_called()

    def test_llm_returns_no_sql_returns_failure(self):
        qs = make_query_service(schema_context=SAMPLE_SCHEMA)
        adapter = LLMAdapter(qs, make_llm_client(NO_SQL_RESPONSE))
        result = adapter.query("show me everything")
        assert result.success is False
        assert "SQL" in result.error

    def test_llm_returns_no_sql_does_not_call_execute(self):
        qs = make_query_service(schema_context=SAMPLE_SCHEMA)
        adapter = LLMAdapter(qs, make_llm_client(NO_SQL_RESPONSE))
        adapter.query("something")
        qs.execute.assert_not_called()

    def test_llm_exception_returns_failure(self):
        qs = make_query_service(schema_context=SAMPLE_SCHEMA)
        client = MagicMock()
        client.complete.side_effect = Exception("API rate limit")
        adapter = LLMAdapter(qs, client)
        result = adapter.query("show users")
        assert result.success is False
        assert "LLM call failed" in result.error

    def test_validator_rejects_llm_sql_returns_failure(self):
        # LLM returned something that looks like SQL but the validator rejects it
        bad_llm_response = "```sql\nDROP TABLE users\n```"
        qs = make_query_service(
            schema_context=SAMPLE_SCHEMA,
            execute_success=False,
            execute_error="Only SELECT queries are allowed.",
        )
        adapter = LLMAdapter(qs, make_llm_client(bad_llm_response))
        result = adapter.query("delete all users")
        assert result.success is False
        assert result.error != ""

    def test_validator_rejects_llm_sql_preserves_generated_sql(self):
        # Even when rejected, we should know what SQL the LLM tried to generate
        bad_llm_response = "```sql\nDROP TABLE users\n```"
        qs = make_query_service(
            schema_context=SAMPLE_SCHEMA,
            execute_success=False,
            execute_error="Rejected.",
        )
        adapter = LLMAdapter(qs, make_llm_client(bad_llm_response))
        result = adapter.query("delete all users")
        assert "DROP TABLE users" in result.generated_sql


# ---------------------------------------------------------------------------
# LLM output is always treated as untrusted
# ---------------------------------------------------------------------------

class TestLLMOutputUntrusted:
    def test_adapter_never_executes_sql_directly(self):
        """
        The adapter must ALWAYS go through query_service.execute().
        It must never call sqlite3 or any DB connection itself.
        """
        import csv_loader.llm_adapter as adapter_module
        # sqlite3 should not be imported by the adapter at all
        assert "sqlite3" not in dir(adapter_module), (
            "LLMAdapter must not import sqlite3 — SQL execution belongs to QueryService."
        )

    def test_execute_called_even_for_bare_sql_response(self):
        """Even when LLM returns bare SQL (no code block), it still goes through QS."""
        qs = make_query_service(schema_context=SAMPLE_SCHEMA)
        adapter = LLMAdapter(qs, make_llm_client(BARE_SQL_RESPONSE))
        adapter.query("show 5 users")
        qs.execute.assert_called_once()

    def test_schema_context_fetched_before_llm_call(self):
        """Prompt must be built with live schema, not hardcoded."""
        qs = make_query_service(schema_context=SAMPLE_SCHEMA)
        client = make_llm_client(VALID_LLM_RESPONSE)
        adapter = LLMAdapter(qs, client)
        adapter.query("anything")
        qs.get_schema_context.assert_called_once()
        # Schema context fetch happens before LLM call
        schema_call_order = qs.get_schema_context.call_args_list
        llm_call_order = client.complete.call_args_list
        assert len(schema_call_order) == 1
        assert len(llm_call_order) == 1
