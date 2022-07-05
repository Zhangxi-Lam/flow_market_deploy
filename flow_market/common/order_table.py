class OrderTable:
    def __init__(self, is_flo):
        self.active_orders = set()
        self.executed_orders = set()
        self.is_flo = is_flo

    def get_frontend_response(self):
        active_orders = []
        for order in self.active_orders:
            active_orders.append(
                {
                    "direction": order.direction,
                    "price": str(order.min_price_point.y)
                    + " - "
                    + str(order.max_price_point.y)
                    if self.is_flo
                    else order.price,
                    "quantity": order.quantity,
                    "progress": order.progress(),
                }
            )

        executed_orders = []
        for order in self.executed_orders:
            executed_orders.append(
                {
                    "direction": order.direction,
                    "price": str(order.min_price_point.y)
                    + " - "
                    + str(order.max_price_point.y)
                    if self.is_flo
                    else order.price,
                    "quantity": order.fill_quantity,
                }
            )

        response = {"active_orders": active_orders, "executed_orders": executed_orders}
        print(response)
        return {"active_orders": active_orders, "executed_orders": executed_orders}

    def add_order(self, order):
        self.active_orders.add(order)

    def remove_order(self, order):
        self.active_orders.remove(order)
        self.executed_orders.add(order)
