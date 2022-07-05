class BaseOrderGraph:
    def __init__(self):
        self.send_update_to_frontend = True

        self.bid_active = True
        self.buy_order_id = None

        self.ask_active = True
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
        if self.has_data(is_buy=True):
            response["bid_data"] = self.get_data(is_buy=True)
        if self.has_data(is_buy=False):
            response["ask_data"] = self.get_data(is_buy=False)
        return response

    def add_order(self, order):
        self.send_update_to_frontend = True

        is_buy = order.direction == "buy"
        if is_buy:
            self.bid_active = False
            self.buy_order_id = order.order_id
        else:
            self.ask_active = False
            self.sell_order_id = order.order_id
        self.sort_points(adjust_buy=not is_buy)

    def remove_order(self, order):
        self.send_update_to_frontend = True
        is_buy = order.direction == "buy"
        if is_buy:
            self.bid_active = True
            self.buy_order_id = None
            if not self.has_data(is_buy=False):
                self.ask_active = True
        else:
            self.ask_active = True
            self.sell_order_id = None
            if not self.has_data(is_buy=True):
                self.bid_active = True

    def has_data(self, is_buy):
        pass

    def get_data(self, is_buy):
        pass

    def sort_points(self, adjust_buy):
        pass
