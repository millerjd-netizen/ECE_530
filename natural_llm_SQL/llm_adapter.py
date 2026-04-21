"""
llm_adapter.py

Translates natural language queries into SQL using an LLM, then passes
the generated SQL to the Query Service for validation and execution.

Responsibilities:
  - Build a prompt using the DB schema and user's natural language query
  - Call the configured LLM (OpenAI or Anthropic Claude)
  - Extract the SQL from the LLM's response
  - Pass the SQL to the Query Service (never execute it directly)
  - Treat all LLM output as untrusted input

Does NOT:
  - Execute SQL
  - Connect to the database directly
  - Define what is or isn't valid SQL (that's the validator's job)
"""

import re
import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------

@dataclass
class AdapterResult:
    natural_language_query: str
    generated_sql: str
    query_result: object          # QueryResult from QueryService, or None
    success: bool
    error: str = ""
    raw_llm_response: str = ""


# ---------------------------------------------------------------------------
# Prompt builder (independently testable)
# ---------------------------------------------------------------------------

def build_prompt(natural_language_query: str, schema_context: dict) -> str:
    """
    Build the LLM prompt from the user's query and the current DB schema.

    The schema_context is a dict of {table_name: [{"name": col, "type": type, ...}]}.
    """
    schema_lines = []
    for table, columns in schema_context.items():
        col_defs = ", ".join(
            f"{c['name']} ({c['type']})" for c in columns
        )
        schema_lines.append(f"  - {table}: {col_defs}")

    schema_block = "\n".join(schema_lines) if schema_lines else "  (no tables)"

    return f"""You are an AI assistant that converts natural language questions into SQL queries.
The database uses SQLite and contains the following tables:

{schema_block}

User question: "{natural_language_query}"

Rules:
1. Return ONLY a SELECT query — no INSERT, UPDATE, DELETE, or DROP.
2. Use only the tables and columns listed above.
3. Output the SQL query inside a ```sql ... ``` code block.
4. After the code block, write one sentence explaining what the query does.

SQL query:"""


def extract_sql(llm_response: str) -> str:
    """
    Extract a SQL query from an LLM response.

    Looks for a ```sql ... ``` code block first.
    Falls back to the first SELECT statement found in the text.
    Returns an empty string if nothing is found.
    """
    # Primary: fenced code block
    fenced = re.search(r"```sql\s*(.*?)```", llm_response, re.IGNORECASE | re.DOTALL)
    if fenced:
        return fenced.group(1).strip()

    # Fallback: bare SELECT statement
    bare = re.search(r"(SELECT\b.*?)(;|$)", llm_response, re.IGNORECASE | re.DOTALL)
    if bare:
        return bare.group(1).strip()

    return ""


# ---------------------------------------------------------------------------
# LLM client abstractions
# ---------------------------------------------------------------------------

class OpenAIClient:
    """Thin wrapper around the OpenAI chat completions API."""

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        try:
            from openai import OpenAI
            self._client = OpenAI(api_key=api_key)
        except ImportError:
            raise ImportError("openai package is required: pip install openai")
        self._model = model

    def complete(self, prompt: str) -> str:
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0,
        )
        return response.choices[0].message.content or ""


class AnthropicClient:
    """Thin wrapper around the Anthropic messages API."""

    def __init__(self, api_key: str, model: str = "claude-haiku-4-5-20251001"):
        try:
            import anthropic
            self._client = anthropic.Anthropic(api_key=api_key)
        except ImportError:
            raise ImportError("anthropic package is required: pip install anthropic")
        self._model = model

    def complete(self, prompt: str) -> str:
        message = self._client.messages.create(
            model=self._model,
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text if message.content else ""


# ---------------------------------------------------------------------------
# LLMAdapter
# ---------------------------------------------------------------------------

class LLMAdapter:
    """
    Translates natural language → SQL → validated QueryResult.

    Parameters
    ----------
    query_service : QueryService instance (injected)
    llm_client    : any object with a .complete(prompt: str) -> str method
    """

    def __init__(self, query_service, llm_client):
        self._query_service = query_service
        self._llm_client = llm_client

    def query(self, natural_language: str) -> AdapterResult:
        """
        Full pipeline: NL → prompt → LLM → extract SQL → validate + execute.

        The LLM's output is treated as untrusted — it goes through the
        Query Service (and therefore the validator) before any execution.
        """
        natural_language = natural_language.strip()
        if not natural_language:
            return AdapterResult(
                natural_language_query=natural_language,
                generated_sql="",
                query_result=None,
                success=False,
                error="Empty query.",
            )

        # Step 1: get schema context from Query Service
        schema_context = self._query_service.get_schema_context()

        # Step 2: build prompt
        prompt = build_prompt(natural_language, schema_context)

        # Step 3: call LLM
        try:
            raw_response = self._llm_client.complete(prompt)
        except Exception as exc:
            logger.error("LLM call failed: %s", exc)
            return AdapterResult(
                natural_language_query=natural_language,
                generated_sql="",
                query_result=None,
                success=False,
                error=f"LLM call failed: {exc}",
            )

        logger.debug("Raw LLM response: %s", raw_response)

        # Step 4: extract SQL — treat output as untrusted
        sql = extract_sql(raw_response)
        if not sql:
            return AdapterResult(
                natural_language_query=natural_language,
                generated_sql="",
                query_result=None,
                success=False,
                error="LLM did not return a recognisable SQL query.",
                raw_llm_response=raw_response,
            )

        # Step 5: pass to Query Service (validation + execution happen there)
        query_result = self._query_service.execute(sql)

        return AdapterResult(
            natural_language_query=natural_language,
            generated_sql=sql,
            query_result=query_result,
            success=query_result.success,
            error=query_result.error if not query_result.success else "",
            raw_llm_response=raw_response,
        )
