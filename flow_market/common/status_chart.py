from ..models import Player
from flow_market.common.player_info import PlayerInfo


class StatusChart:
    def __init__(self) -> None:
        self.inventory = None
        self.cash = None

    def get_frontend_response(self):
        return {
            "inventory": self.inventory,
            "cash": self.cash,
        }

    def update(self, player_info: PlayerInfo):
        self.inventory = player_info.get_inventory()
        self.cash = player_info.get_cash()
