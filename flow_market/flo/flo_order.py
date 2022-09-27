from .flo_point import FloPoint
from flow_market.common.base_order import BaseOrder


class FloOrder(BaseOrder):
    def __init__(self, id_in_group, order: dict, timestamp) -> None:
        self.max_price_point = FloPoint(
            order["max_price_rate"], order["max_price"], is_max_price=True
        )
        self.min_price_point = FloPoint(
            order["min_price_rate"], order["min_price"], is_max_price=False
        )
        slope = FloPoint.get_slope(self.max_price_point, self.min_price_point)
        self.max_price_point.slope = slope
        self.min_price_point.slope = slope
        BaseOrder.__init__(self, id_in_group, order, timestamp)

    def get_rate(self, price):
        price_high = self.max_price_point.y
        price_low = self.min_price_point.y
        if self.direction == "buy":
            max_rate = self.min_price_point.x
            if price > price_high:
                return 0
            if price > price_low:
                return (price_high - price) / (price_high - price_low) * max_rate
            else:
                return max_rate
        else:
            max_rate = self.max_price_point.x
            if price > price_high:
                return max_rate
            if price > price_low:
                return (price - price_low) / (price_high - price_low) * max_rate
            else:
                return 0
