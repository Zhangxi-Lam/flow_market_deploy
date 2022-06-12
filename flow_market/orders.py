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
    def get_slope(p1, p2):
        if p1.x == p2.x:
            raise ValueError("Two Point objects have the same x")
        return (p1.y - p2.y) / (p1.x - p2.x)

    def __init__(self, x, y, is_max_price=None) -> None:
        dict.__init__(self, x=x, y=y, is_max_price=is_max_price, slope=None)

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
        y_cents = self.get_intersect_left()
        if y_cents < 0:
            return
        price, rate = self.get_clearing_price_and_rate(y_cents)
        self.intersect_points = [
            Point(0, price), Point(rate, price), Point(rate, 0)]

    def get_clearing_price_and_rate(self, y_cents_left):
        price = y_cents_left / self.config.dollar_to_cent
        i = self.get_y_left(self.combined_bids_points,
                            y_cents_left, is_buy=True)
        rate = self.get_x(
            y_cents_left, self.combined_bids_points[i], self.combined_bids_points[i + 1])
        return price, rate

    # Get the y_cents to the left of the intersect
    def get_intersect_left(self):
        if not self.combined_bids_points or not self.combined_asks_points:
            return -1
        lo, hi = 0, self.config.y_max * self.config.dollar_to_cent + 1
        while lo < hi - 1:
            mid = lo + (hi - lo) // 2
            buy_i = self.get_y_left(
                self.combined_bids_points, mid, is_buy=True)
            buy_x = self.get_x(
                mid, self.combined_bids_points[buy_i], self.combined_bids_points[buy_i + 1])
            sell_i = self.get_y_left(
                self.combined_asks_points, mid, is_buy=False)
            sell_x = self.get_x(
                mid, self.combined_asks_points[sell_i], self.combined_asks_points[sell_i + 1])
            # print(lo, hi, mid, buy_x, sell_x)
            if sell_x <= buy_x:
                lo = mid
            else:
                hi = mid
        return lo

    def get_x(self, y_cents, p1: Point, p2: Point):
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
