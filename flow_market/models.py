import asyncio
from email.policy import default
import uuid
from jsonfield import JSONField
from otree import live
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


author = 'Your name here'

doc = """
Your app description
"""


class Constants(BaseConstants):
    name_in_url = 'flow_market'
    players_per_group = 2
    num_rounds = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    def get_inventory_data(self, time):
        """
        Return {id_in_group: {'time': time, 'inventory': player.inventory}}
        """
        result = {}
        for player in self.get_players():
            result[player.id_in_group] = {
                'time': time,
                'inventory': player.inventory
            }
        return result

    def get_cash_data(self, time):
        """
        Return {id_in_group: {'time': time, 'cash': player.cash}}
        """
        result = {}
        for player in self.get_players():
            result[player.id_in_group] = {
                'time': time,
                'cash': player.cash
            }
        return result


class Player(BasePlayer):
    inventory = models.FloatField(initial=0)
    cash = models.FloatField(initial=0)
