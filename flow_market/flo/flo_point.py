class FloPoint(dict):
    @staticmethod
    def get_w(buy_lo, sell_lo, buy_hi, sell_hi):
        return (buy_lo.x - sell_lo.x) / (buy_lo.x - sell_lo.x + sell_hi.x - buy_hi.x)

    @staticmethod
    def get_slope(p1, p2):
        if p1.x == p2.x:
            raise ValueError("Two Point objects have the same x")
        return (p1.y - p2.y) / (p1.x - p2.x)

    def __init__(self, x, y, is_max_price=None) -> None:
        # x is rate, y is price
        dict.__init__(self, x=x, y=y, is_max_price=is_max_price, slope=None)

    def __setattr__(self, field: str, value):
        self[field] = value

    def __getattr__(self, field: str):
        return self[field]
