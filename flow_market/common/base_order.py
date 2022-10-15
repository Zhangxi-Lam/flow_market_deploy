class BaseOrder:
    order_id_cnt = 0

    def __init__(self, id_in_group, order: dict, timestamp) -> None:
        self.id_in_group = id_in_group
        self.order_id = BaseOrder.order_id_cnt
        self.direction = order["direction"]  # buy, sell
        self.quantity = order["quantity"]
        self.timestamp = timestamp
        self.fill_quantity = 0
        BaseOrder.order_id_cnt += 1

    def fill(self, clearing_rate):
        self.fill_quantity = self.fill_quantity + clearing_rate
        self.fill_quantity = min(self.fill_quantity, self.quantity)

    def remaining_quantity(self):
        return self.quantity - self.fill_quantity

    def is_complete(self):
        return self.fill_quantity >= self.quantity

    def progress(self):
        return str(int(self.fill_quantity / self.quantity * 100)) + "%"
