from .cda_point import CdaPoint
import uuid


class CdaOrder:
    def __init__(self, id_in_group, order: dict) -> None:
        self.id_in_group = id_in_group
        self.order_id = str(uuid.uuid4())
        self.direction = order["direction"]
        self.price = order["price"]
        self.quantity = order["quantity"]
        self.point = CdaPoint(order["price"], order["quantity"])
        self.fill_quantity = 0

    def __repr__(self) -> str:
        return str(self.order_id) + " " + str(self.quantity)
        # return self.__dict__.__str__()

    def fill(self, clearing_rate):
        self.fill_quantity = round(self.fill_quantity + clearing_rate, 2)
        self.fill_quantity = min(self.fill_quantity, self.quantity)

    def remaining_quantity(self):
        return self.quantity - self.fill_quantity

    def is_complete(self):
        return self.fill_quantity >= self.quantity

    def progress(self):
        return str(int(self.fill_quantity / self.quantity * 100)) + "%"
