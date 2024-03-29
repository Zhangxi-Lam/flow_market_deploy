from .cda_point import CdaPoint
from flow_market.common.base_order import BaseOrder


class CdaOrder(BaseOrder):
    def __init__(self, id_in_group, order: dict, timestamp):
        self.price = order["price"]
        self.point = CdaPoint(order["quantity"], order["price"])
        BaseOrder.__init__(self, id_in_group, order, timestamp)

    def __repr__(self) -> str:
        return (
            str(self.order_id)
            + " "
            + str(self.price)
            + " "
            + str(self.remaining_quantity())
        )
