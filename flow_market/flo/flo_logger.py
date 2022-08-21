import json
import os
from flow_market.models import Player
from .flo_order_book import FloOrderBook
from flow_market.common.contract_table import ContractTable


class FloLogger:
    def __init__(self, round):
        self.market_path = "flow_market/data/" + str(round) + "/market.json"
        self.participant_path = "flow_market/data/" + str(round) + "/participant.json"
        self.market_data = []
        self.participant_data = []

    def update_market_data(
        self, timestamp, before_transaction, order_book: FloOrderBook
    ):
        cur_data = {
            "timestamp": timestamp,
            "before_transaction": before_transaction,
            "clearing_price": order_book.clearing_price,
            "clearing_rate": order_book.clearing_rate,
        }
        self.market_data.append(cur_data)
        self.write(self.market_path, self.market_data)

    def update_participant_data(
        self,
        timestamp,
        before_transaction,
        player: Player,
        order_book: FloOrderBook,
        contract_table: ContractTable,
    ):
        cur_data = {
            "timestamp": timestamp,
            "id": player.participant.id,
            "before_transaction": before_transaction,
            "orders": self.log_orders(player, order_book),
            "contracts": self.log_contracts(contract_table),
            "cash": player.get_cash(),
            "inventory": player.get_inventory(),
        }
        self.participant_data.append(cur_data)
        self.write(self.participant_path, self.participant_data)

    def log_orders(self, player: Player, order_book: FloOrderBook):
        orders = order_book.find_orders_for_player(player)
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

    def log_contracts(self, contract_table: ContractTable):
        contracts = contract_table.active_contracts
        data = []
        for c in contracts:
            data.append(
                {
                    "direction": c.direction,
                    "price": c.price,
                    "quantity": c.quantity,
                    "showtime": c.showtime,
                    "deadline": c.deadline,
                }
            )

    def write(self, file_path, data):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as outfile:
            json.dump(data, outfile)
