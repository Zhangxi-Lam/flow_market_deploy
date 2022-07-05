from .cda_point import CdaPoint
from .cda_order import CdaOrder
from flow_market.common.base_order_graph import BaseOrderGraph
from flow_market.common.constants import Y_MAX


class CdaOrderGraph(BaseOrderGraph):
    def __init__(self) -> None:
        self.bid = CdaPoint(1, 1)
        self.ask = CdaPoint(2, 19)
        BaseOrderGraph.__init__(self)

    def has_data(self, is_bid):
        if is_bid:
            return self.bid is not None
        return self.ask is not None

    def get_data(self, is_bid):
        if is_bid:
            return [
                {"x": 0, "y": self.bid.y},
                {"x": self.bid.x, "y": self.bid.y},
                {"x": self.bid.x, "y": 0},
            ]
        return [
            {"x": 0, "y": self.ask.y},
            {"x": self.ask.x, "y": self.ask.y},
            {"x": self.ask.x, "y": 0},
        ]

    def add_order(self, order: CdaOrder):
        if order.direction == "buy":
            self.bid = order.point
        else:
            self.ask = order.point
        BaseOrderGraph.add_order(self, order)

    def remove_order(self, order: CdaOrder):
        if order.direction == "buy":
            self.bid = CdaPoint(1, 1)
            if not self.ask:
                self.ask = CdaPoint(2, 19)
        else:
            self.ask = CdaPoint(2, 19)
            if not self.bid:
                self.bid = CdaPoint(1, 1)
        BaseOrderGraph.remove_order(self, order)

    def sort_points(self, adjust_buy):
        if self.ask.y <= self.bid.y:
            if adjust_buy:
                if self.ask.y >= 2:
                    self.bid.y = self.ask.y - 1
                else:
                    self.bid_active = False
                    self.bid = None
            else:
                if self.bid.y <= Y_MAX - 2:
                    self.ask.y = self.bid.y + 1
                else:
                    self.ask_active = False
                    self.ask = None
