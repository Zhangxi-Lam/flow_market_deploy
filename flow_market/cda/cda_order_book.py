from flow_market.models import Group, Player
from .cda_point import CdaPoint
from .cda_order import CdaOrder


class CdaOrderBook:
    def __init__(self, config):
        self.config = config

        self.orders = {}  # {order_id: CdaOrder}
        self.bid_orders = {}  # {id_in_group: {order_id: CdaOrder}}
        self.ask_orders = {}  # {id_in_group: {order_id: CdaOrder}}
        self.combined_bid_points = []  # [CdaPoint, ...], sorted by y desc
        self.combined_ask_points = []  # [CdaPoint, ...], sorted by y asc

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

        self.update_combined_points(is_buy)

    def find_order(self, order_id):
        return self.orders[order_id]

    def remove_order(self, order: CdaOrder):
        if order.order_id in self.orders:
            del self.orders[order.order_id]

        is_buy = order.direction == "buy"
        group_orders = self.bid_orders if is_buy else self.ask_orders
        del group_orders[order.id_in_group][order.order_id]

        self.update_combined_points(is_buy)

    def update_combined_points(self, is_buy):
        raw_bid_points = []
        raw_ask_points = []
        for d in self.bid_orders.values():
            for _, order in d.items():
                raw_bid_points.append(CdaPoint(order.remaining_quantity(), order.price))
        for d in self.ask_orders.values():
            for _, order in d.items():
                raw_ask_points.append(CdaPoint(order.remaining_quantity(), order.price))

        if is_buy and not raw_bid_points:
            self.combined_bid_points = []
            return
        if not is_buy and not raw_ask_points:
            self.combined_ask_points = []
            return

        points = raw_bid_points if is_buy else raw_ask_points
        result = [CdaPoint(0, 20)] if is_buy else [CdaPoint(0, 0)]
        result.append(CdaPoint(0, points[0].y))

        x, y = points[0].x, points[0].y
        i = 1
        while i < len(points):
            if points[i].y != y:
                result.append(CdaPoint(x, y))
                result.append(CdaPoint(x, points[i].y))
                y = points[i].y
            x += points[i].x
            i += 1
        result.append(CdaPoint(x, y))
        point = CdaPoint(x, 0) if is_buy else CdaPoint(x, 20)
        result.append(point)

        if is_buy:
            self.combined_bid_points = result
        else:
            self.combined_ask_points = result
        return

    def transact(self, group: Group):
        complete_orders = []
        sorted_bid_orders = []
        sorted_ask_orders = []
        for d in self.bid_orders.values():
            for _, order in d.items():
                sorted_bid_orders.append(order)
        for d in self.ask_orders.values():
            for _, order in d.items():
                sorted_ask_orders.append(order)
        sorted_bid_orders.sort(
            reverse=True, key=lambda order: (order.price, order.timestamp)
        )
        sorted_ask_orders.sort(
            reverse=False, key=lambda order: (order.price, order.timestamp)
        )
        while (
            sorted_bid_orders
            and sorted_ask_orders
            and sorted_bid_orders[0].price >= sorted_ask_orders[0].price
        ):
            bid, ask = sorted_bid_orders[0], sorted_ask_orders[0]
            price = bid.price if bid.timestamp < ask.timestamp else ask.price
            quantity = min(bid.remaining_quantity(), ask.remaining_quantity())
            self.fill_order(
                bid, price * 100, quantity, group.get_player_by_id(bid.id_in_group)
            )
            self.fill_order(
                ask, price * 100, quantity, group.get_player_by_id(ask.id_in_group)
            )
            if bid.is_complete():
                complete_orders.append(bid)
                sorted_bid_orders.pop(0)
                self.remove_order(bid)
            if ask.is_complete():
                complete_orders.append(ask)
                sorted_ask_orders.pop(0)
                self.remove_order(ask)
        self.update_combined_points(is_buy=True)
        self.update_combined_points(is_buy=False)
        return complete_orders

    def fill_order(self, order: CdaOrder, price_in_cents, quantity, player: Player):
        order.fill(quantity)
        if order.direction == "buy":
            player.update_inventory(quantity)
            player.update_cash(-quantity * price_in_cents / 100)
            print(player)
        else:
            player.update_inventory(-quantity)
            player.update_cash(quantity * price_in_cents / 100)
