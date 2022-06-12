from django import conf
from otree.api import Currency as c, currency_range

from flow_market.config import Config
from flow_market.orders import OrderBook, Order
from ._builtin import Page, WaitPage
from .models import Constants, Player


config = Config()
order_books = {}    # Each group has one order_book


class MarketPage(Page):

    @staticmethod
    def live_method(player: Player, data):
        message_type = data['message_type']
        response = {}

        MarketPage.init_if_not_exist(
            player.group.id_in_subsession, order_books)
        order_book = order_books[player.group.id_in_subsession]

        orders_to_be_removed = []
        if message_type == 'add_order':
            MarketPage.add_order(order_book, player.id_in_group, data)
        elif message_type == 'remove_order':
            MarketPage.remove_order(order_book, data)
        elif message_type == 'update':
            orders_to_be_removed = order_book.transact()

        response = {
            'message_type': message_type,
            'order_graph_data': orders_to_be_removed,
            'order_book_data': MarketPage.update_order_book(order_book),
        }
        return {0: response}

    @staticmethod
    def init_if_not_exist(id_in_subsession, order_books):
        if id_in_subsession not in order_books:
            order_books[id_in_subsession] = OrderBook(config)

    @staticmethod
    def add_order(order_book: OrderBook, id_in_group, data):
        order = Order(id_in_group, data)
        order_book.add_order(order)

    @staticmethod
    def remove_order(order_book: OrderBook, data):
        order = order_book.find_order(data['order_id'])
        order_book.remove_order(order)

    @staticmethod
    def update_order_book(order_book: OrderBook):
        return {
            'bids_order_points': order_book.combined_bids_points,
            'asks_order_points': order_book.combined_asks_points,
            'transact_points': order_book.intersect_points,
        }


page_sequence = [MarketPage]
