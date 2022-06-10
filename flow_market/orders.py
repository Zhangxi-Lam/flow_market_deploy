import uuid
from pprint import pprint
from .config import Config


class Order():
    def __init__(self, player_id, order: dict) -> None:
        self.player_id = player_id
        self.order_id = uuid.uuid4().hex
        self.direction = order['direction']
        self.max_price_x = order['max_price_x']
        self.max_price_y = order['max_price_y']
        self.min_price_x = order['min_price_x']
        self.min_price_y = order['min_price_y']
        self.quantity = order['quantity']
        self.slope = self.get_order_slope()

    def get_order_slope(self):
        return (self.max_price_y - self.min_price_y) / (self.max_price_x - self.min_price_x)


class OrderPoint():
    def __init__(self, y, slope, is_max_price) -> None:
        self.y = y
        self.slope = slope
        self.is_max_price = is_max_price

    def __repr__(self) -> str:
        d = {'y': self.y, 'slope': self.slope,
             'is_max_price': self.is_max_price}
        return d.__str__()


class OrderBook():
    def __init__(self, config: Config) -> None:
        self.bids_orders = {}
        self.bids_order_points = []
        self.asks_orders = {}
        self.asks_order_points = []
        self.config = config

    def add_order(self, order: Order):
        is_buy = order.direction == 'buy'
        orders = self.bids_orders if is_buy else self.asks_orders
        order_points = self.bids_order_points if is_buy else self.asks_order_points
        player_orders = orders.get(
            order.player_id, {})
        player_orders[order.order_id] = order
        orders[order.player_id] = player_orders

        order_points.append(OrderPoint(
            order.max_price_y, order.slope, is_max_price=True))
        order_points.append(OrderPoint(
            order.min_price_y, order.slope, is_max_price=False))
        order_points.sort(
            reverse=is_buy, key=lambda point: point.y)

    def get_order_points_to_show(self, is_buy):
        if is_buy and not self.bids_order_points:
            return []
        if not is_buy and not self.asks_order_points:
            return []

        order_points = self.bids_order_points if is_buy else self.asks_order_points

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
        return result
