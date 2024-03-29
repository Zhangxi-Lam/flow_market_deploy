from flow_market.common.order_table import OrderTable
from flow_market.models import Player
from .flo_order_book import FloOrderBook
from flow_market.common.logger import Logger


class FloLogger(Logger):
    def update_market_data(
        self, timestamp, id_in_subsession, before_transaction, order_book: FloOrderBook
    ):
        cur_data = {
            "timestamp": timestamp,
            "id_in_subsession": id_in_subsession,
            "before_transaction": before_transaction,
            "clearing_price": order_book.clearing_price,
            "clearing_rate": order_book.clearing_rate,
        }
        self.market_data.append(cur_data)
        print(
            str(id_in_subsession)
            + " market_data "
            + str(self.market_data[-1]["timestamp"])
        )

    def log_active_orders(self, player: Player, order_book: FloOrderBook):
        orders = order_book.find_orders_by_id_in_group(player.id_in_group)
        data = []
        for order_id, order in orders.items():
            data.append(
                {
                    "order_id": order_id,
                    "direction": order.direction,
                    "quantity": order.quantity,
                    "fill_quantity": order.fill_quantity,
                    "timestamp": order.timestamp,
                    "max_price": order.max_price_point.y,
                    "min_price": order.min_price_point.y,
                    "max_rate": order.min_price_point.x
                    if order.direction == "buy"
                    else order.max_price_point.x,
                }
            )
        return data
    
    def log_executed_orders(self, order_table: OrderTable):
        orders = order_table.executed_orders
        data = []
        for order in orders:
            data.append(
                {
                    "order_id": order.order_id,
                    "direction": order.direction,
                    "quantity": order.quantity,
                    "fill_quantity": order.fill_quantity,
                    "timestamp": order.timestamp,
                    "max_price": order.max_price_point.y,
                    "min_price": order.min_price_point.y,
                    "max_rate": order.min_price_point.x
                    if order.direction == "buy"
                    else order.max_price_point.x,
                }
            )
        return data
