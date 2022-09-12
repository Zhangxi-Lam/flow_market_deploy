import json
import os
from flow_market.models import Player
from flow_market.common.contract_table import ContractTable
from flow_market.common.player_info import PlayerInfo


class Logger:
    def __init__(self, round):
        self.market_path = "flow_market/data/" + str(round) + "/market.json"
        self.participant_path = "flow_market/data/" + str(round) + "/participant.json"
        self.market_data = []
        self.participant_data = []

    def update_market_data(self, timestamp, before_transaction, order_book):
        pass

    def update_participant_data(
        self,
        timestamp,
        before_transaction,
        player: Player,
        player_info: PlayerInfo,
        order_book,
        contract_table: ContractTable,
    ):
        cur_data = {
            "timestamp": timestamp,
            "id": player.participant.id,
            "before_transaction": before_transaction,
            "orders": self.log_orders(player, order_book),
            "contracts": self.log_contracts(contract_table),
            "cash": player_info.get_cash(),
            "inventory": player_info.get_inventory(),
        }
        self.participant_data.append(cur_data)
        self.write(self.participant_path, self.participant_data)

    def log_orders(self, player: Player, order_book):
        pass

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
