import sqlite3
import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class QueryResult:
    """Structured result returned from every query execution."""
    sql: str
    columns: list[str]
    rows: list[tuple]
    row_count: int
    success: bool
    error: str = ""

    @property
    def as_dicts(self) -> list[dict]:
        """Return rows as a list of column→value dicts."""
        return [dict(zip(self.columns, row)) for row in self.rows]
