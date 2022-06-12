import uuid
from pprint import pprint
from .config import Config


class Order():
    def __init__(self, id_in_group, order: dict) -> None:
        self.id_in_group = id_in_group
        self.order_id = uuid.uuid4().hex
        self.direction = order['direction']
        self.max_price_point = Point(
            order['max_price_x'], order['max_price_y'], is_max_price=True)
        self.min_price_point = Point(
            order['min_price_x'], order['min_price_y'], is_max_price=False)
        slope = Point.get_slope(self.max_price_point, self.min_price_point)
        self.max_price_point.slope = slope
        self.min_price_point.slope = slope
        self.quantity = order['quantity']

    def __repr__(self) -> str:
        return self.__dict__.__str__()


class Point(dict):

    @staticmethod
    def get_w(buy_lo, sell_lo, buy_hi, sell_hi):
        return (buy_lo.x - sell_lo.x) / (buy_lo.x - sell_lo.x + sell_hi.x - buy_hi.x)

    @staticmethod
    def get_slope(p1, p2):
        if p1.x == p2.x:
            raise ValueError("Two Point objects have the same x")
        return (p1.y - p2.y) / (p1.x - p2.x)

    def __init__(self, x, y, is_max_price=None) -> None:
        dict.__init__(self, x=x, y=y,
                      is_max_price=is_max_price, slope=None)

    def __setattr__(self, field: str, value):
        self[field] = value

    def __getattr__(self, field: str):
        return self[field]


class OrderBook():
    def __init__(self, config: Config) -> None:
        self.config = config

        self.bids_orders = {}   # {id_in_group: {order_id: Order}}
        self.asks_orders = {}
        self.raw_bids_points = []     # [Point, ...], sorted by y desc
        self.raw_asks_points = []     # [Point, ...], sorted by y asc
        self.combined_bids_points = []     # [Point, ...], sorted by y desc
        self.combined_asks_points = []     # [Point, ...], sorted by y asc

        self.intersect_points = []  # [Point, ...]

        self.precise_price = None
        self.precise_rate = None

    def add_order(self, order: Order):
        is_buy = order.direction == 'buy'
        orders = self.bids_orders if is_buy else self.asks_orders
        points = self.raw_bids_points if is_buy else self.raw_asks_points
        player_orders = orders.get(
            order.id_in_group, {})
        player_orders[order.order_id] = order
        orders[order.id_in_group] = player_orders

        points.append(order.max_price_point)
        points.append(order.min_price_point)
        points.sort(
            reverse=is_buy, key=lambda point: point.y)

        self.update_combined_points(is_buy)
        self.update_intersect_points()

    def update_combined_points(self, is_buy):
        if is_buy and not self.raw_bids_points:
            return
        if not is_buy and not self.raw_asks_points:
            return

        points = self.raw_bids_points if is_buy else self.raw_asks_points
        point = Point(0, self.config.y_max) if is_buy else Point(0, 0)
        result = [point]

        x, y = 0, points[0].y
        inverse = 1 / points[0].slope
        result.append(Point(x, y))
        for i in range(1, len(points)):
            point = points[i]
            x += (point.y - y) * inverse
            result.append(Point(x, point.y))
            # Update
            change = (1 / point.slope) if is_buy else - 1 / point.slope
            if point.is_max_price:
                inverse += change
            else:
                inverse -= change
            y = point.y
        point = Point(x, 0) if is_buy else Point(x, self.config.y_max)
        result.append(point)

        if is_buy:
            self.combined_bids_points = result
        else:
            self.combined_asks_points = result
        return

    def update_intersect_points(self):
        best_bid_in_cents = self.get_best_bid_in_cents()
        self.update_clearing_price_and_rate(best_bid_in_cents)
        if self.precise_price and self.precise_rate:
            self.intersect_points = [
                Point(0, self.precise_price / 100),
                Point(self.precise_rate, self.precise_price / 100),
                Point(self.precise_rate, 0)]
        else:
            self.intersect_points = []

    def update_clearing_price_and_rate(self, y_lo):
        if y_lo < 0:
            self.precise_price, self.precise_rate = None, None
            return
        buy_lo = Point(self.get_x(y_lo, is_buy=True), y_lo)
        sell_lo = Point(self.get_x(y_lo, is_buy=False), y_lo)
        y_hi = y_lo + self.config.dollar_to_cent
        buy_hi = Point(self.get_x(y_hi, is_buy=True), y_hi)
        sell_hi = Point(self.get_x(y_hi, is_buy=False), y_hi)

        w = Point.get_w(buy_lo, sell_lo, buy_hi, sell_hi)

        self.precise_price = round(
            sell_lo.y + w * (sell_hi.y - sell_lo.y), self.config.precision)
        self.precise_rate = round(
            sell_lo.x + w * (sell_hi.x - sell_lo.x), self.config.precision)
        print(self.precise_price, self.precise_rate)

    # Get the best bid
    def get_best_bid_in_cents(self):
        if not self.combined_bids_points or not self.combined_asks_points:
            return -1
        lo, hi = 0, self.config.y_max * self.config.dollar_to_cent + 1
        while lo < hi - 1:
            mid = lo + (hi - lo) // 2
            buy_x = self.get_x(mid, is_buy=True)
            sell_x = self.get_x(mid, is_buy=False)
            if sell_x <= buy_x:
                lo = mid
            else:
                hi = mid
        return lo

    def get_x(self, y_cents, is_buy):
        points = self.combined_bids_points if is_buy else self.combined_asks_points
        i = self.get_y_left(points, y_cents, is_buy)
        p1, p2 = points[i], points[i + 1]
        if p1.x == p2.x:
            return p1.x
        slope = Point.get_slope(p1, p2) * self.config.dollar_to_cent
        return round(p1.x + (y_cents - p1.y * self.config.dollar_to_cent) * 1 / slope,
                     self.config.precision)

    # Get the index of the Point to the left of the y_cents
    def get_y_left(self, combined_points, y_cents, is_buy):
        lo, hi = 0, len(combined_points)
        while lo < hi - 1:
            mid = lo + (hi - lo) // 2
            if is_buy:
                if combined_points[mid].y * self.config.dollar_to_cent >= y_cents:
                    lo = mid
                else:
                    hi = mid
            else:
                if combined_points[mid].y * self.config.dollar_to_cent <= y_cents:
                    lo = mid
                else:
                    hi = mid
        return lo
