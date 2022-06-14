from email import message
from django import conf
from otree.api import Currency as c, currency_range

from flow_market.config import Config
from flow_market.orders import OrderBook, Order
from ._builtin import Page, WaitPage
from .models import Constants, Player, Group


config = Config()
order_books = {}    # Each group has one order_book


class MarketPage(Page):

    @staticmethod
    def live_method(player: Player, data):
        message_type = data['message_type']

        MarketPage.init_if_not_exist(
            player.group.id_in_subsession, order_books)
        order_book = order_books[player.group.id_in_subsession]

        complete_orders = []
        inventory_data = {}
        cash_data = {}
        if message_type == 'add_order':
            MarketPage.add_order(order_book, player.id_in_group, data)
        elif message_type == 'remove_order':
            MarketPage.remove_order(order_book, data)
        elif message_type == 'update':
            if player.id_in_group != 1:
                # We only let the first player in the group do the update to
                # avoid duplicate transactions.
                return
            complete_orders = order_book.transact(player.group)
            inventory_data = player.group.get_inventory_data(
                data['time'])
            cash_data = player.group.get_cash_data(data['time'])

        response = MarketPage.create_response(player.group,
                                              message_type, MarketPage.get_order_book_data(
                                                  order_book),
                                              complete_orders, inventory_data, cash_data)
        return response

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
    def create_response(group: Group, message_type, order_book_data,
                        complete_orders=[], inventory_data={}, cash_data={}):
        group_response = {}
        for player in group.get_players():
            player_response = {
                'message_type': message_type,
                'order_book_data': order_book_data,
                'order_graph_data': complete_orders,
            }
            if player.id_in_group in inventory_data:
                player_response['inventory_data'] = inventory_data[player.id_in_group]

            if player.id_in_group in cash_data:
                player_response['cash_data'] = cash_data[player.id_in_group]

            group_response[player.id_in_group] = player_response
        return group_response

    @staticmethod
    def get_order_book_data(order_book: OrderBook):
        return {
            'bids_order_points': order_book.combined_bids_points,
            'asks_order_points': order_book.combined_asks_points,
            'transact_points': order_book.intersect_points,
        }


page_sequence = [MarketPage]
