from otree.api import (
    models,
    widgets,
    BaseConstants,
    BaseSubsession,
    BaseGroup,
    BasePlayer,
    Currency as c,
    currency_range,
)


author = "Your name here"

doc = """
Your app description
"""


class Constants(BaseConstants):
    name_in_url = "flow_market"
    players_per_group = 2
    num_rounds = 10


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    _inventory = models.FloatField(initial=0)
    _cash = models.FloatField(initial=0)

    def __repr__(self) -> str:
        return (
            str(self.id_in_group) + " " + str(self._inventory) + " " + str(self._cash)
        )

    def update_inventory(self, delta):
        self._inventory += delta

    def get_inventory(self):
        return round(self._inventory, 2)

    def update_cash(self, delta):
        self._cash += delta

    def get_cash(self):
        return round(self._cash, 2)
