import uuid
from pprint import pprint
from .config import Config
import bisect


class Order():
    def __init__(self, id_in_group, order: dict) -> None:
        self.id_in_group = id_in_group
        self.order_id = uuid.uuid4().hex
        self.direction = order['direction']
        self.max_price_x = order['max_price_x']
        self.max_price_y = order['max_price_y']
        self.min_price_x = order['min_price_x']
        self.min_price_y = order['min_price_y']
        self.quantity = order['quantity']
        self.slope = self.get_order_slope()

    def __repr__(self) -> str:
        return self.__dict__.__str__()

    def get_order_slope(self):
        return (self.max_price_y - self.min_price_y) / (self.max_price_x - self.min_price_x)


class OrderPoint():
    def __init__(self, y, slope, is_max_price) -> None:
        self.y = y
        self.slope = slope
        self.is_max_price = is_max_price

    def __repr__(self) -> str:
        return self.__dict__.__str__()


class OrderBook():
    def __init__(self, config: Config) -> None:
        self.bids_orders = {}   # {id_in_group: {order_id: Order}}
        self.raw_bids_points = []     # [OrderPoint, OrderPoint], sorted by y desc
        self.combined_bids_points = []     # [OrderPoint, OrderPoint], sorted by y desc
        self.asks_orders = {}
        self.raw_asks_points = []     # [OrderPoint, OrderPoint], sorted by y asc
        self.combined_asks_points = []     # [OrderPoint, OrderPoint], sorted by y asc
        self.config = config

    def add_order(self, order: Order):
        is_buy = order.direction == 'buy'
        orders = self.bids_orders if is_buy else self.asks_orders
        order_points = self.raw_bids_points if is_buy else self.raw_asks_points
        player_orders = orders.get(
            order.id_in_group, {})
        player_orders[order.order_id] = order
        orders[order.id_in_group] = player_orders

        order_points.append(OrderPoint(
            order.max_price_y, order.slope, is_max_price=True))
        order_points.append(OrderPoint(
            order.min_price_y, order.slope, is_max_price=False))
        order_points.sort(
            reverse=is_buy, key=lambda point: point.y)

    def update_combined_points(self, is_buy):
        if is_buy and not self.raw_bids_points:
            return
        if not is_buy and not self.raw_asks_points:
            return

        order_points = self.raw_bids_points if is_buy else self.raw_asks_points

        point = {'x': 0, 'y': self.config.y_max} if is_buy else {
            'x': 0, 'y': 0}
        result = [point]

        y = order_points[0].y
        inverse = 1 / order_points[0].slope
        x = 0
        result.append({'x': 0, 'y': y})
        for i in range(1, len(order_points)):
            point = order_points[i]
            x += (point.y - y) * inverse
            result.append({'x': x, 'y': point.y})
            # Update
            change = (1 / point.slope) if is_buy else - 1 / point.slope
            if point.is_max_price:
                inverse += change
            else:
                inverse -= change
            y = point.y
        point = {'x': x, 'y': 0} if is_buy else {
            'x': x, 'y': self.config.y_max}
        result.append(point)

        if is_buy:
            self.combined_bids_points = result
        else:
            self.combined_asks_points = result
        return

    def transact(self):
        return self.get_clearing_price_and_rate()
    #     # 1. get rate and price
    #     # 2. get orders
    #     # 3. execute orders
    #     price = self.get_clearing_price()
    #     rate = self.get_rate(price)
    #     pass

    def get_clearing_price_and_rate(self):
        lo, hi = 0, self.config.y_max * 100
        while lo < hi - 1:
            mid = lo + (hi - lo) // 2
            buy_i = self.get_left(self.combined_bids_points, mid, is_buy=True)
            buy_x = self.get_rate(
                mid, self.combined_bids_points[buy_i], self.combined_bids_points[buy_i + 1])
            sell_i = self.get_left(
                self.combined_asks_points, mid, is_buy=False)
            sell_x = self.get_rate(
                mid, self.combined_asks_points[sell_i], self.combined_asks_points[sell_i + 1])
            if sell_x <= buy_x:
                lo = mid
            else:
                hi = mid
        return mid, buy_x

    def get_rate(self, y, p1, p2):
        slope = (p1['y'] - p2['y']) / (p1['x'] - p2['x'])
        return p1['x'] + (y - p1['y']) * 1 / slope

    # Get the right most index of the point that point.y>=y (<=y for asks)
    def get_left(self, combined_points, y, is_buy):
        lo, hi = 0, len(combined_points)
        while lo < hi - 1:
            mid = lo + (hi - lo) // 2
            if is_buy:
                if combined_points[mid]['y'] >= y:
                    lo = mid
                else:
                    hi = mid
            else:
                if combined_points[mid]['y'] <= y:
                    lo = mid
                else:
                    hi = mid
        return lo
