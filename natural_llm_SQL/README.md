

## How to Run

## #1. Install dependencies

```bash
pip install -r requirements.txt
```

To use the LLM `query` command, also install your provider:

```bash
pip install anthropic   # for Claude
pip install openai      # for GPT
```

### 2. Set your API key (optional — only needed for `query` command)

```bash
export ANTHROPIC_API_KEY=your_key_here
# or
export OPENAI_API_KEY=your_key_here
```

> **Never commit API keys to your repository.** Use environment variables only.

### 3. Start the CLI

```bash
python -m csv_loader.cli              # uses data.db by default
python -m csv_loader.cli mydata.db    # custom database path
```

### 4. Example session

```
> load data/sales.csv
  ✓ Inserted 120 rows into 'sales'.

> tables
  Tables (1):
    • sales

> schema sales
  Table: sales
  Column               Type         PK
  -------------------- ------------ --
  id                   INTEGER      ✓
  product              TEXT
  revenue              REAL
  sale_date            TEXT

> sql SELECT product, SUM(revenue) FROM sales GROUP BY product LIMIT 5
  product     SUM(revenue)
  ----------  ------------
  Widget A    4200.0
  ...

> query What were the top 3 products by total revenue?
  Generated SQL: SELECT product, SUM(revenue) AS total FROM sales GROUP BY product ORDER BY total DESC LIMIT 3
  product     total
  ----------  -----
  Widget A    4200.0
  ...

> exit
```

---

## How to Run Tests

```bash
pytest tests/ -v
```

All 150 tests use mocks or in-memory SQLite — no API keys needed.

```
tests/test_csv_loader.py       24 tests
tests/test_schema_manager.py   35 tests
tests/test_query_service.py    20 tests
tests/test_sql_validator.py    42 tests
tests/test_llm_adapter.py      29 tests
─────────────────────────────────────
Total                         150 tests
```

---

## CI

GitHub Actions runs the full test suite on every push. See `.github/workflows/ci.yml`.

---

## Design Justification

### Why inject dependencies?
Every module accepts its collaborators (validator, schema manager, LLM client) as constructor arguments. This means tests never need real API keys, real files, or a real database — the entire suite runs in ~2 seconds with mocks. It also means swapping OpenAI for Anthropic is a one-line change at the call site.

### Why is the CLI last?
The CLI depends on everything else but nothing depends on it. Building it last meant all the contracts between components were already tested and stable before the interface layer was written.

### Why does the validator use `EXPLAIN`?
Column validation delegates to SQLite's own `EXPLAIN` command rather than reimplementing SQL parsing. This is accurate, cheap, and catches edge cases (qualified columns, aliases, functions) that regex would miss.

### Known limitation
The LLM adapter's `extract_sql` uses regex to find SQL in the LLM response. Deeply nested subqueries or CTEs (WITH clauses) may not be extracted perfectly. A more robust approach would be to prompt the LLM to return *only* the SQL with no surrounding text — a prompt engineering improvement left for future work.

---

## LLM Usage Documentation

Per assignment requirements, the following uses of LLM assistance are documented:

| Where | How LLM was used |
|---|---|
| `sql_validator.py` — `_check_no_disallowed_keywords` | LLM suggested using `sql.split()` to tokenize. Tests caught that this missed keywords attached to punctuation (e.g. `"INSERT;"`). Refined to use `re.findall(r"\b[A-Za-z_]+\b", ...)`. |
| `llm_adapter.py` — `extract_sql` | LLM suggested regex patterns for extracting fenced code blocks. Reviewed and adapted. |
| General | LLM used for code review and explaining SQLite PRAGMA behaviour. |

All submitted code was reviewed and is understood by the author.
