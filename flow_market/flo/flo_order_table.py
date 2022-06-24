from ..models import Player
from .flo_order import FloOrder


class FloOrderTable():
    def __init__(self) -> None:
        self.active_orders = set()
        self.executed_orders = set()

    def get_frontend_response(self):
        active_orders = []
        for order in self.active_orders:
            active_orders.append({
                'direction': order.direction,
                'price': str(order.min_price_point.y) + ' - ' + str(order.max_price_point.y),
                'quantity': order.quantity,
                'progress':  order.progress()
            })

        executed_orders = []
        for order in self.executed_orders:
            executed_orders.append({
                'direction': order.direction,
                'price': str(order.min_price_point.y) + ' - ' + str(order.max_price_point.y),
                'quantity': order.fill_quantity,
            })

        return {
            'active_orders': active_orders,
            'executed_orders': executed_orders
        }

    def add_order(self, order: FloOrder):
        self.active_orders.add(order)

    def remove_order(self, order: FloOrder):
        self.active_orders.remove(order)
        self.executed_orders.add(order)
