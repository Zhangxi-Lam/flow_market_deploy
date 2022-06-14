from email import message
from django import conf
from otree.api import Currency as c, currency_range

from flow_market.common.inventory_chart import InventoryChart
from flow_market.common.cash_chart import CashChart

from .flo.flo_order import FloOrder
from .flo.flo_order_book import FloOrderBook
from .flo.flo_config import FloConfig
from ._builtin import Page, WaitPage
from .models import Constants, Player, Group


config = FloConfig()
flo_order_books = {}    # {id_in_subsession: FloOrderBook}
inventory_charts = {}   # {id_in_subsession: {id_in_group: InventoryChart}}
cash_charts = {}   # {id_in_subsession: {id_in_group: CashChart}}


class FloMarketPage(Page):

    @staticmethod
    def live_method(player: Player, data):
        message_type = data['message_type']

        FloMarketPage.init(player)

        order_book = flo_order_books[player.group.id_in_subsession]

        if message_type == 'add_order':
            order_book.add_order(FloOrder(player.id_in_group, data))
        elif message_type == 'remove_order':
            order_book.remove_order(order_book.find_order(data['order_id']))
        elif message_type == 'update':
            if player.id_in_group != 1:
                # We only let the first player in the group do the update to
                # avoid duplicate transactions.
                return
            FloMarketPage.update(player.group)

        response = FloMarketPage.create_response(player.group)
        return response

    @staticmethod
    def init(player: Player):
        id_in_subsession, id_in_group = player.group.id_in_subsession, player.id_in_group
        if id_in_subsession not in flo_order_books:
            flo_order_books[id_in_subsession] = FloOrderBook(
                config)
        if id_in_subsession not in inventory_charts:
            inventory_charts[id_in_subsession] = {}
        if id_in_group not in inventory_charts[id_in_subsession]:
            inventory_charts[id_in_subsession][id_in_group] = InventoryChart()

        if id_in_subsession not in cash_charts:
            cash_charts[id_in_subsession] = {}
        if id_in_group not in cash_charts[id_in_subsession]:
            cash_charts[id_in_subsession][id_in_group] = CashChart()

    @staticmethod
    def update(group: Group):
        id_in_subsession = group.id_in_subsession
        flo_order_books[id_in_subsession].transact(group)

        for player in group.get_players():
            id_in_group = player.id_in_group
            if id_in_subsession in inventory_charts and id_in_group in inventory_charts[id_in_subsession]:
                inventory_charts[id_in_subsession][id_in_group].update(
                    player.inventory)
            if id_in_subsession in cash_charts and id_in_group in cash_charts[id_in_subsession]:
                cash_charts[id_in_subsession][id_in_group].update(
                    player.cash)

    @staticmethod
    def create_response(group: Group, complete_orders=[]):
        """
        Response: {
            id_in_group: {
                'message_type': 'update'
                'order_graph_data':
                'order_book_data':
                'inventory_chart_data':
                'cash_chart_data':
            }
        }
        """
        id_in_subsession = group.id_in_subsession
        group_response = {}
        for player in group.get_players():
            player_response = {
                'message_type': 'update',
                'order_book_data': flo_order_books[id_in_subsession].get_frontend_response(),
                'order_graph_data': complete_orders,
            }
            if id_in_subsession in inventory_charts and player.id_in_group in inventory_charts[id_in_subsession]:
                player_response['inventory_chart_data'] = inventory_charts[id_in_subsession][player.id_in_group].get_frontend_response()
            if id_in_subsession in cash_charts and player.id_in_group in cash_charts[id_in_subsession]:
                player_response['cash_chart_data'] = cash_charts[id_in_subsession][player.id_in_group].get_frontend_response(
                )
            group_response[player.id_in_group] = player_response
        return group_response


page_sequence = [FloMarketPage]
