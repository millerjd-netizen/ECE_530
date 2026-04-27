class QueryResult:
    def __init__(self, data):
        self.data = data


class QueryService:
    def __init__(self):
        pass

    def execute(self, query: str):
        return QueryResult(data=[])
