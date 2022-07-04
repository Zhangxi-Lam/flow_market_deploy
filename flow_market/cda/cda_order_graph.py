from .cda_point import CdaPoint
from .cda_order import CdaOrder
from flow_market.common.constants import Y_MAX


class CdaOrderGraph:
    def __init__(self) -> None:
        self.send_update_to_frontend = True

        self.bid_active = True
        self.bid = CdaPoint(1, 1)
        self.buy_order_id = None

        self.ask_active = True
        self.ask = CdaPoint(2, 19)
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
        if self.bid:
            response["bid_data"] = [
                {"x": 0, "y": self.bid.y},
                {"x": self.bid.x, "y": self.bid.y},
                {"x": self.bid.x, "y": 0},
            ]
        if self.ask:
            response["ask_data"] = [
                {"x": 0, "y": self.ask.y},
                {"x": self.ask.x, "y": self.ask.y},
                {"x": self.ask.x, "y": 0},
            ]
        print(response)
        return response

    def add_order(self, order: CdaOrder):
        self.send_update_to_frontend = True

        is_buy = order.direction == "buy"
        if is_buy:
            self.bid_active = False
            self.bid = order.point
            self.buy_order_id = order.order_id
        else:
            self.ask_active = False
            self.ask = order.point
            self.sell_order_id = order.order_id
        self.sort_points(adjust_buy=not is_buy)

    def sort_points(self, adjust_buy):
        if self.ask.y <= self.bid.y:
            if adjust_buy:
                if self.ask.y >= 2:
                    self.bid.y = self.ask.y - 1
                else:
                    self.remove_points(remove_buy=True)
            else:
                if self.bid.y <= Y_MAX - 2:
                    self.ask.y = self.bid.y + 1
                else:
                    self.remove_points(remove_buy=False)

    def remove_points(self, remove_buy):
        if remove_buy:
            self.bid_active = True
            self.bid = None
        else:
            self.ask_active = True
            self.ask = None

    def remove_order(self, order: CdaOrder):
        self.send_update_to_frontend = True

        is_buy = order.direction == "buy"
        if is_buy:
            self.buy_order_id = None
        else:
            self.sell_order_id = None
        self.reset_points(is_buy)

    def reset_points(self, is_buy):
        print("reset points")
        if is_buy:
            self.bid_active = True
            self.bid = CdaPoint(1, 1)
            if not self.ask:
                self.ask = CdaPoint(2, 19)
        else:
            self.ask_active = True
            self.ask = CdaPoint(2, 19)
            if not self.bid:
                self.bid_active = True
                self.bid = CdaPoint(1, 1)
