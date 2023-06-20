from flow_market.common.order_table import OrderTable
from flow_market.models import Player
from .cda_order_book import CdaOrderBook
from flow_market.common.logger import Logger


class CdaLogger(Logger):
    def update_market_data(
        self, timestamp, id_in_subsession, before_transaction, order_book: CdaOrderBook
    ):
        cur_data = {
            "timestamp": timestamp,
            "id_in_subsession": id_in_subsession,
            "before_transaction": before_transaction,
            "clearing_price": None if before_transaction else order_book.clearing_price,
            "clearing_rate": None if before_transaction else order_book.clearing_rate,
        }
        self.market_data.append(cur_data)
        print(
            str(id_in_subsession)
            + " market_data "
            + str(self.market_data[-1]["timestamp"])
        )

    def log_active_orders(self, player: Player, order_book: CdaOrderBook):
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
                    "price": order.price,
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
                    "price": order.price,
                }
            )
        return data
