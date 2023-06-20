import json
import os
from flow_market.models import Player
from flow_market.common.contract_table import ContractTable
from flow_market.common.order_table import OrderTable
from flow_market.common.player_info import PlayerInfo


class Logger:
    def __init__(self, round, id_in_subsession):
        self.market_path = (
            "flow_market/data/"
            + str(round)
            + "/"
            + str(id_in_subsession)
            + "_market.json"
        )
        self.participant_path = (
            "flow_market/data/"
            + str(round)
            + "/"
            + str(id_in_subsession)
            + "_participant.json"
        )
        self.market_data = []
        self.participant_data = []

    def update_market_data(
        self, timestamp, id_in_subsession, before_transaction, order_book
    ):
        pass

    def update_participant_data(
        self,
        timestamp,
        before_transaction,
        player: Player,
        player_info: PlayerInfo,
        order_book,
        order_table: OrderTable,
        contract_table: ContractTable,
    ):
        cur_data = {
            "timestamp": timestamp,
            "id_in_subsession": player.group.id_in_subsession,
            "id_in_group": player.id_in_group,
            "participant_id": player.participant.id,
            "before_transaction": before_transaction,
            "active_orders": self.log_active_orders(player, order_book),
            "executed_orders": self.log_executed_orders(order_table),
            "active_contracts": self.log_contracts(contract_table.active_contracts),
            "executed_contracts": self.log_contracts(contract_table.executed_contracts),
            "cash": player_info.get_cash(),
            "inventory": player_info.get_inventory(),
            "rate": player_info.get_rate(),
        }
        self.participant_data.append(cur_data)

    def log_active_orders(self, player: Player, order_book):
        pass

    def log_executed_orders(self, order_table: OrderTable):
        pass

    def log_contracts(self, contracts):
        data = []
        for c in contracts:
            data.append(
                {
                    "direction": c.direction,
                    "price": c.price,
                    "quantity": c.quantity,
                    "fill_quantity": c.fill_quantity,
                    "showtime": c.showtime,
                    "deadline": c.deadline,
                }
            )
        return data

    def write_log(self):
        self.write(self.market_path, self.market_data)
        self.write(self.participant_path, self.participant_data)

    def write(self, file_path, data):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as outfile:
            json.dump(data, outfile)
