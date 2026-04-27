class SchemaManager:
    def __init__(self):
        self.tables = {}

    def register_table(self, name, columns):
        self.tables[name] = columns

    def list_tables(self):
        return list(self.tables.keys())


def _normalize_name(name: str) -> str:
    return name.strip().lower()


def _normalize_type(t: str) -> str:
    return t.strip().lower()
