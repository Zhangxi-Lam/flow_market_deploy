from .flo_point import FloPoint


class FloOrder():
    def __init__(self, id_in_group, order: dict) -> None:
        self.id_in_group = id_in_group
        self.order_id = order['order_id']
        self.direction = order['direction']
        self.max_price_point = FloPoint(
            order['max_price_x'], order['max_price_y'], is_max_price=True)
        self.min_price_point = FloPoint(
            order['min_price_x'], order['min_price_y'], is_max_price=False)
        slope = FloPoint.get_slope(self.max_price_point, self.min_price_point)
        self.max_price_point.slope = slope
        self.min_price_point.slope = slope
        self.quantity = order['quantity']

    def __repr__(self) -> str:
        return str(self.order_id) + ' ' + str(self.quantity)
        # return self.__dict__.__str__()

    def fill(self, clearing_rate):
        self.quantity -= clearing_rate
