class CdaPoint(dict):
    def __init__(self, quantity, price) -> None:
        dict.__init__(self, x=quantity, y=price)

    def __setattr__(self, field: str, value):
        self[field] = value

    def __getattr__(self, field: str):
        return self[field]
