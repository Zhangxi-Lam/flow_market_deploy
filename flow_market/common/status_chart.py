from ..models import Player


class StatusChart():
    def __init__(self) -> None:
        self.inventory = None
        self.cash = None

    def get_frontend_response(self):
        return {
            'inventory': self.inventory,
            'cash': self.cash,
        }

    def update(self, player: Player):
        self.inventory = player.get_inventory()
        self.cash = player.get_cash()
