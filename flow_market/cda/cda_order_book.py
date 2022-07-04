from flow_market.models import Player
from .cda_order import CdaOrder


class CdaOrderBook:
    def __init__(self, config):
        self.config = config

        self.orders = {}  # {order_id: CdaOrder}
        self.bid_orders = {}  # {id_in_group: {order_id: CdaOrder}}
        self.ask_orders = {}  # {id_in_group: {order_id: CdaOrder}}
        self.raw_bid_points = []  # [CdaPoint, ...], sorted by y desc
        self.raw_ask_points = []  # [CdaPoint, ...], sorted by y asc
        self.combined_bid_points = []  # [CdaPoint, ...], sorted by y desc
        self.combined_ask_points = []  # [CdaPoint, ...], sorted by y asc

        self.precise_price_in_cents = None
        self.precise_rate = None

    def __repr__(self) -> str:
        return self.__dict__.__str__()

    def get_frontend_response(self):
        return {
            "bids_order_points": self.combined_bid_points,
            "asks_order_points": self.combined_ask_points,
        }

    def add_order(self, order: CdaOrder):
        self.orders[order.order_id] = order

        is_buy = order.direction == "buy"
        group_orders = self.bid_orders if is_buy else self.ask_orders
        player_orders = group_orders.get(order.id_in_group, {})
        player_orders[order.order_id] = order
        group_orders[order.id_in_group] = player_orders

        points = self.raw_bid_points if is_buy else self.raw_ask_points
        points.append(order.point)
        points.sort(reverse=is_buy, key=lambda point: point.y)

        self.update_combined_points(is_buy)

    def find_order(self, order_id):
        return self.orders[order_id]

    def remove_order(self, order: CdaOrder):
        if order.order_id in self.orders:
            del self.orders[order.order_id]

        is_buy = order.direction == "buy"
        group_orders = self.bid_orders if is_buy else self.ask_orders
        del group_orders[order.id_in_group][order.order_id]

        points = self.raw_bid_points if is_buy else self.raw_ask_points
        points.remove(order.point)

        self.update_combined_points(is_buy)

    def update_combined_points(self, is_buy):
        pass
