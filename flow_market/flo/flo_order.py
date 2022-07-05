from .flo_point import FloPoint
from flow_market.common.base_order import BaseOrder


class FloOrder(BaseOrder):
    def __init__(self, id_in_group, order: dict, timestamp) -> None:
        self.max_price_point = FloPoint(
            order["max_price_x"], order["max_price_y"], is_max_price=True
        )
        self.min_price_point = FloPoint(
            order["min_price_x"], order["min_price_y"], is_max_price=False
        )
        slope = FloPoint.get_slope(self.max_price_point, self.min_price_point)
        self.max_price_point.slope = slope
        self.min_price_point.slope = slope
        BaseOrder.__init__(self, id_in_group, order, timestamp)
