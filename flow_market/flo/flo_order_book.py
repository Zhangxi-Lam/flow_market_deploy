from flow_market.models import Player
from .flo_point import FloPoint
from .flo_order import FloOrder


class FloOrderBook:
    """
    The OrderBook of the group
    """

    def __init__(self, config) -> None:
        self.config = config

        self.orders = {}  # {order_id: FloOrder}
        self.bids_orders = {}  # {id_in_group: {order_id: FloOrder}}
        self.asks_orders = {}  # {id_in_group: {order_id: FloOrder}}
        self.raw_bids_points = []  # [FloPoint, ...], sorted by y desc
        self.raw_asks_points = []  # [FloPoint, ...], sorted by y asc
        self.combined_bids_points = []  # [FloPoint, ...], sorted by y desc
        self.combined_asks_points = []  # [FloPoint, ...], sorted by y asc

        self.intersect_points = []  # [FloPoint, ...]

        self.clearing_price = None
        self.clearing_rate = None

    def __repr__(self) -> str:
        return self.__dict__.__str__()

    def get_frontend_response(self):
        return {
            "bids_order_points": self.combined_bids_points,
            "asks_order_points": self.combined_asks_points,
            "transact_points": self.intersect_points,
        }

    def add_order(self, order: FloOrder):
        self.orders[order.order_id] = order

        is_buy = order.direction == "buy"
        group_orders = self.bids_orders if is_buy else self.asks_orders
        player_orders = group_orders.get(order.id_in_group, {})
        player_orders[order.order_id] = order
        group_orders[order.id_in_group] = player_orders

        points = self.raw_bids_points if is_buy else self.raw_asks_points
        points.append(order.max_price_point)
        points.append(order.min_price_point)
        points.sort(reverse=is_buy, key=lambda point: point.y)

        self.update_combined_points(is_buy)
        self.update_intersect_points()

    def find_orders_for_player(self, player: Player):
        id_in_group = player.id_in_group
        orders = {
            **self.bids_orders.get(id_in_group, {}),
            **self.asks_orders.get(id_in_group, {}),
        }
        return orders

    def find_order(self, order_id):
        return self.orders[order_id]

    def remove_order(self, order: FloOrder):
        if order.order_id in self.orders:
            del self.orders[order.order_id]

        is_buy = order.direction == "buy"
        group_orders = self.bids_orders if is_buy else self.asks_orders
        del group_orders[order.id_in_group][order.order_id]

        points = self.raw_bids_points if is_buy else self.raw_asks_points
        points.remove(order.max_price_point)
        points.remove(order.min_price_point)

        self.update_combined_points(is_buy)
        self.update_intersect_points()

    def update_combined_points(self, is_buy):
        if is_buy and not self.raw_bids_points:
            self.combined_bids_points = []
            return
        if not is_buy and not self.raw_asks_points:
            self.combined_asks_points = []
            return

        points = self.raw_bids_points if is_buy else self.raw_asks_points
        point = FloPoint(0, 20) if is_buy else FloPoint(0, 0)
        result = [point]

        x, y = 0, points[0].y
        inverse = 1 / points[0].slope
        result.append(FloPoint(x, y))
        for i in range(1, len(points)):
            point = points[i]
            x += (point.y - y) * inverse
            result.append(FloPoint(x, point.y))
            # Update
            change = (1 / point.slope) if is_buy else -1 / point.slope
            if point.is_max_price:
                inverse += change
            else:
                inverse -= change
            y = point.y
        point = FloPoint(x, 0) if is_buy else FloPoint(x, self.config["max_price"])
        result.append(point)

        if is_buy:
            self.combined_bids_points = result
        else:
            self.combined_asks_points = result
        return

    def update_intersect_points(self):
        (
            self.clearing_price,
            self.clearing_rate,
        ) = self.get_clearing_price_and_rate()
        if self.clearing_price and self.clearing_rate:
            self.intersect_points = [
                FloPoint(0, round(self.clearing_price, 2)),
                FloPoint(round(self.clearing_rate, 2), round(self.clearing_price, 2)),
                FloPoint(round(self.clearing_rate, 2), 0),
            ]
        else:
            self.intersect_points = []

    # 1. Find the price_in_ticks s.t. sell_rate <= buy_rate
    # 2. Use price_in_ticks, price_in_ticks+1 to get 4 points (bid_lo, ask_lo, bid_hi, ask_hi)
    # 3. Use those 4 points to get the w
    # 4. Use the w to get the final price and rate
    def get_clearing_price_and_rate(self):
        if not self.combined_bids_points or not self.combined_asks_points:
            return None, None
        lo_in_ticks, hi_in_ticks = 0, 20 * 100 + 1
        while lo_in_ticks < hi_in_ticks - 1:
            mid_in_ticks = lo_in_ticks + (hi_in_ticks - lo_in_ticks) // 2
            buy_rate = self.get_rate(mid_in_ticks, is_buy=True)
            sell_rate = self.get_rate(mid_in_ticks, is_buy=False)
            if sell_rate <= buy_rate:
                lo_in_ticks = mid_in_ticks
            else:
                hi_in_ticks = mid_in_ticks

        bid_lo_in_ticks = FloPoint(self.get_rate(lo_in_ticks, is_buy=True), lo_in_ticks)
        ask_lo_in_ticks = FloPoint(
            self.get_rate(lo_in_ticks, is_buy=False), lo_in_ticks
        )
        bid_hi_in_ticks = FloPoint(
            self.get_rate(lo_in_ticks + 1, is_buy=True), lo_in_ticks + 1
        )
        ask_hi_in_ticks = FloPoint(
            self.get_rate(lo_in_ticks + 1, is_buy=False), lo_in_ticks + 1
        )

        w = FloPoint.get_w(
            bid_lo_in_ticks, ask_lo_in_ticks, bid_hi_in_ticks, ask_hi_in_ticks
        )

        final_price = (
            ask_lo_in_ticks.y + w * (ask_hi_in_ticks.y - ask_lo_in_ticks.y)
        ) / 100
        final_rate = ask_lo_in_ticks.x + w * (ask_hi_in_ticks.x - ask_lo_in_ticks.x)
        return final_price, final_rate

    def get_rate(self, price_in_ticks, is_buy):
        points = self.combined_bids_points if is_buy else self.combined_asks_points
        i = self.get_index(points, price_in_ticks, is_buy)
        p1, p2 = points[i], points[i + 1]
        if p1.x == p2.x:
            return p1.x
        slope = FloPoint.get_slope(p1, p2)
        return p1.x + (price_in_ticks - p1.y * 100) / 100 / slope

    # Get the index of the FloPoint such that:
    # For bid, find the index of the FloPoint with price >= price_in_ticks
    # For ask, find the index of the FloPoint with price <= price_in_ticks
    def get_index(self, combined_points, price_in_ticks, is_buy):
        lo, hi = 0, len(combined_points)
        while lo < hi - 1:
            mid = lo + (hi - lo) // 2
            if is_buy:
                if combined_points[mid].y * 100 >= price_in_ticks:
                    lo = mid
                else:
                    hi = mid
            else:
                if combined_points[mid].y * 100 <= price_in_ticks:
                    lo = mid
                else:
                    hi = mid
        return lo

    def transact(self, group):
        complete_orders = []
        if not self.clearing_price or not self.clearing_rate or not self.orders:
            return complete_orders

        # Temporarilty store self.clearing_price in transact_price because
        # self.claring_price will be updated in self.remove_order()
        transact_price = self.clearing_price
        transact_orders = self.get_transact_orders(self.clearing_price)

        for order in transact_orders:
            self.fill_order(
                order,
                transact_price,
                order.get_rate(transact_price),
                group.get_player_by_id(order.id_in_group),
            )
            if order.is_complete():
                complete_orders.append(order)
                self.remove_order(order)
        return complete_orders

    def get_transact_orders(self, clearing_price):
        transact_orders = []
        for order in self.orders.values():
            if order.direction == "buy":
                if order.max_price_point.y > clearing_price:
                    transact_orders.append(order)
            else:
                if order.min_price_point.y < clearing_price:
                    transact_orders.append(order)
        return transact_orders

    def fill_order(
        self,
        order: FloOrder,
        clearing_price,
        transact_rate,
        player: Player,
    ):
        final_transact_rate = min(order.remaining_quantity(), transact_rate)
        order.fill(final_transact_rate)
        if order.direction == "buy":
            player.update_inventory(final_transact_rate)
            player.update_cash(-final_transact_rate * clearing_price)
        else:
            player.update_inventory(-final_transact_rate)
            player.update_cash(final_transact_rate * clearing_price)
