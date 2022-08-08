from .flo_order import FloOrder
from .flo_point import FloPoint
from flow_market.common.base_order_graph import BaseOrderGraph


class FloOrderGraph(BaseOrderGraph):
    def __init__(self):
        self.bid_max = FloPoint(0, 1)
        self.bid_min = FloPoint(1, 0)
        self.ask_max = FloPoint(1, 20)
        self.ask_min = FloPoint(0, 19)
        BaseOrderGraph.__init__(self)

    def has_data(self, is_buy):
        if is_buy:
            return self.bid_max is not None
        return self.ask_max is not None

    def get_data(self, is_buy):
        if is_buy:
            return [
                {"x": self.bid_max.x, "y": 20},
                {"x": self.bid_max.x, "y": self.bid_max.y},
                {"x": self.bid_min.x, "y": self.bid_min.y},
                {"x": self.bid_min.x, "y": 0},
            ]
        return [
            {"x": self.ask_max.x, "y": 20},
            {"x": self.ask_max.x, "y": self.ask_max.y},
            {"x": self.ask_min.x, "y": self.ask_min.y},
            {"x": self.ask_min.x, "y": 0},
        ]

    def add_order(self, order: FloOrder):
        if order.direction == "buy":
            self.bid_max = order.max_price_point
            self.bid_min = order.min_price_point
        else:
            self.ask_max = order.max_price_point
            self.ask_min = order.min_price_point
        BaseOrderGraph.add_order(self, order)

    def remove_order(self, order: FloOrder):
        if order.direction == "buy":
            self.bid_max = FloPoint(0, 1)
            self.bid_min = FloPoint(1, 0)
            if not self.ask_max:
                self.ask_max = FloPoint(1, 20)
                self.ask_min = FloPoint(0, 19)
                self.ask_active = True
        else:
            self.ask_max = FloPoint(1, 20)
            self.ask_min = FloPoint(0, 19)
            if not self.bid_max:
                self.bid_max = FloPoint(0, 1)
                self.bid_min = FloPoint(1, 0)
                self.bid_active = True
        BaseOrderGraph.remove_order(self, order)

    def sort_points(self, adjust_buy):
        if self.ask_min.y <= self.bid_max.y:
            if adjust_buy:
                if self.ask_min.y >= 2:
                    self.bid_max.y = self.ask_min.y - 1
                    if self.bid_min.y >= self.bid_max.y:
                        self.bid_min.y = self.bid_max.y - 1
                else:
                    self.bid_active = False
                    self.bid_max, self.bid_min = None, None
            else:
                if self.bid_max.y <= 18:
                    self.ask_min.y = self.bid_max.y + 1
                    if self.ask_max.y <= self.ask_min.y:
                        self.ask_max.y = self.ask_min.y + 1
                else:
                    self.ask_active = False
                    self.ask_max, self.ask_min = None, None
