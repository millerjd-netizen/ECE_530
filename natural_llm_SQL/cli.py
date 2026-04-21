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
