import asyncio
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
from .orders import OrderBook, Order
from .config import Config


author = 'Your name here'

doc = """
Your app description
"""

order_book = OrderBook(Config())


class Constants(BaseConstants):
    name_in_url = 'flow_market'
    players_per_group = 2
    num_rounds = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):

    def add_order(self, player_id, order):
        order = Order(player_id, order)
        order_book.add_order(order)

    def update_order_book(self):
        return {
            'bids_order_points': order_book.get_order_points_to_show(is_buy=True),
            'asks_order_points': order_book.get_order_points_to_show(is_buy=False)
        }


class Player(BasePlayer):
    pass
