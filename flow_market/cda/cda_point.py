class CdaPoint(dict):
    def __init__(self, x, y) -> None:
        dict.__init__(self, x=x, y=y)

    def __setattr__(self, field: str, value):
        self[field] = value

    def __getattr__(self, field: str):
        return self[field]
