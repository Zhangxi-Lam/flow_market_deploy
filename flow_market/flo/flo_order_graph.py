from .flo_order import FloOrder
from .flo_point import FloPoint
from flow_market.common.constants import Y_MAX


class FloOrderGraph:
    def __init__(self) -> None:
        self.send_update_to_frontend = True

        self.bid_active = True
        self.bid_max = FloPoint(0, 1)
        self.bid_min = FloPoint(1, 0)
        self.buy_order_id = None

        self.ask_active = True
        self.ask_max = FloPoint(1, 20)
        self.ask_min = FloPoint(0, 19)
        self.sell_order_id = None

    def get_frontend_response(self):
        if not self.send_update_to_frontend:
            return
        self.send_update_to_frontend = False

        response = {
            "bid_active": self.bid_active,
            "buy_order_id": self.buy_order_id,
            "ask_active": self.ask_active,
            "sell_order_id": self.sell_order_id,
        }
        if self.bid_max:
            response["bid_data"] = [
                {"x": self.bid_max.x, "y": Y_MAX},
                {"x": self.bid_max.x, "y": self.bid_max.y},
                {"x": self.bid_min.x, "y": self.bid_min.y},
                {"x": self.bid_min.x, "y": 0},
            ]
        if self.ask_max:
            response["ask_data"] = [
                {"x": self.ask_max.x, "y": Y_MAX},
                {"x": self.ask_max.x, "y": self.ask_max.y},
                {"x": self.ask_min.x, "y": self.ask_min.y},
                {"x": self.ask_min.x, "y": 0},
            ]
        return response

    def add_order(self, order: FloOrder):
        self.send_update_to_frontend = True

        is_buy = order.direction == "buy"
        if is_buy:
            self.bid_active = False
            self.bid_max = FloPoint(order.max_price_point.x, order.max_price_point.y)
            self.bid_min = FloPoint(order.min_price_point.x, order.min_price_point.y)
            self.buy_order_id = order.order_id
        else:
            self.ask_active = False
            self.ask_max = order.max_price_point
            self.ask_min = order.min_price_point
            self.sell_order_id = order.order_id
        self.sort_points(adjust_buy=not is_buy)

    def remove_order(self, order: FloOrder):
        self.send_update_to_frontend = True

        is_buy = order.direction == "buy"
        self.reset_points(is_buy)

    def sort_points(self, adjust_buy):
        if self.ask_min.y <= self.bid_max.y:
            if adjust_buy:
                if self.ask_min.y >= 2:
                    self.bid_max.y = self.ask_min.y - 1
                    if self.bid_min.y >= self.bid_max.y:
                        self.bid_min.y = self.bid_max.y - 1
                else:
                    self.remove_points(remove_buy=True)
            else:
                if self.bid_max.y <= Y_MAX - 2:
                    self.ask_min.y = self.bid_max.y + 1
                    if self.ask_max.y <= self.ask_min.y:
                        self.ask_max.y = self.ask_min.y + 1
                else:
                    self.remove_points(remove_buy=False)

    def remove_points(self, remove_buy):
        if remove_buy:
            self.bid_active = True
            self.bid_max, self.bid_min = None, None
        else:
            self.ask_active = True
            self.ask_max, self.ask_min = None, None

    def reset_points(self, is_buy):
        if is_buy:
            self.bid_active = True
            self.bid_max = FloPoint(0, 1)
            self.bid_min = FloPoint(1, 0)
            if not self.ask_max:
                self.ask_active = True
                self.ask_max = FloPoint(1, 20)
                self.ask_min = FloPoint(0, 19)
        else:
            self.ask_active = True
            self.ask_max = FloPoint(1, 20)
            self.ask_min = FloPoint(0, 19)
            if not self.bid_max:
                self.bid_active = True
                self.bid_max = FloPoint(0, 1)
                self.bid_min = FloPoint(1, 0)
