from email import message
from django import conf
from otree.api import Currency as c, currency_range

from flow_market.common.inventory_chart import InventoryChart
from flow_market.common.cash_chart import CashChart
from flow_market.common.status_chart import StatusChart

from .flo.flo_order import FloOrder
from .flo.flo_order_book import FloOrderBook
from .flo.flo_config import FloConfig
from .flo.flo_order_graph import FloOrderGraph
from .flo.flo_order_table import FloOrderTable
from .flo.flo_contract_table import FloContractTable
from ._builtin import Page, WaitPage
from .models import Constants, Player, Group, Subsession
import time


config = FloConfig()
flo_order_books = {}    # {id_in_subsession: FloOrderBook}
flo_order_graphs = {}   # {id_in_subsession: {id_in_group: FloOrderGraph}}
flo_order_tables = {}    # {id_in_subsession: {id_in_group: FloOrderTable}}
flo_contract_tables = {}    # {id_in_subsession: {id_in_group: FloContractTable}}
inventory_charts = {}   # {id_in_subsession: {id_in_group: InventoryChart}}
cash_charts = {}        # {id_in_subsession: {id_in_group: CashChart}}
status_charts = {}        # {id_in_subsession: {id_in_group: StatusChart}}


class FloMarketPage(Page):

    @staticmethod
    def live_method(player: Player, data):
        message_type = data['message_type']

        if not flo_order_books:
            FloMarketPage.init(player.group.subsession)

        order_book = flo_order_books[player.group.id_in_subsession]
        order_graph = flo_order_graphs[player.group.id_in_subsession][player.id_in_group]
        order_table = flo_order_tables[player.group.id_in_subsession][player.id_in_group]

        if message_type == 'order_graph_update_request':
            order_graph.send_update_to_frontend = True
            return
        elif message_type == 'add_order':
            order = FloOrder(player.id_in_group, data)
            order_book.add_order(order)
            order_graph.add_order(order)
            order_table.add_order(order)
            return FloMarketPage.respond(player.group)
        elif message_type == 'remove_order':
            order = order_book.find_order(data['order_id'])
            order_book.remove_order(order)
            order_graph.remove_order(order)
            order_table.remove_order(order)
            return FloMarketPage.respond(player.group)
        else:   # update
            if player.id_in_group != 1:
                # We only let the first player in the group do the update to
                # avoid duplicate transactions.
                return
            FloMarketPage.update(player.group)
            return FloMarketPage.respond(player.group)

    @staticmethod
    def init(subsession: Subsession):
        start_time = time.time()
        for g in subsession.get_groups():
            id_in_subsession = g.id_in_subsession
            flo_order_books[id_in_subsession] = FloOrderBook(config)
            flo_order_graphs[id_in_subsession] = {}
            flo_order_tables[id_in_subsession] = {}
            flo_contract_tables[id_in_subsession] = {}
            inventory_charts[id_in_subsession] = {}
            cash_charts[id_in_subsession] = {}
            status_charts[id_in_subsession] = {}
            for p in g.get_players():
                id_in_group = p.id_in_group
                flo_order_graphs[id_in_subsession][id_in_group] = FloOrderGraph()
                flo_order_tables[id_in_subsession][id_in_group] = FloOrderTable()
                flo_contract_tables[id_in_subsession][id_in_group] = FloContractTable(
                    id_in_subsession, id_in_group, start_time)
                inventory_charts[id_in_subsession][id_in_group] = InventoryChart(
                    start_time)
                cash_charts[id_in_subsession][id_in_group] = CashChart(
                    start_time)
                status_charts[id_in_subsession][id_in_group] = StatusChart()

    @staticmethod
    def update(group: Group):
        id_in_subsession = group.id_in_subsession

        # Order transaction
        completed_orders = flo_order_books[id_in_subsession].transact(group)
        for order in completed_orders:
            flo_order_graphs[id_in_subsession][order.id_in_group].remove_order(
                order)
            flo_order_tables[id_in_subsession][order.id_in_group].remove_order(
                order)

        for player in group.get_players():
            id_in_group = player.id_in_group
            # Contract transaction
            flo_contract_tables[id_in_subsession][id_in_group].update(player)
            inventory_charts[id_in_subsession][id_in_group].update(
                player.inventory)
            cash_charts[id_in_subsession][id_in_group].update(
                player.cash)
            status_charts[id_in_subsession][id_in_group].update(player)

    @staticmethod
    def respond(group: Group):
        """
        Response: {
            id_in_group: {
                'message_type': 'update'
                'order_graph_data':
                'order_book_data':
                'inventory_chart_data':
                'cash_chart_data':
                'order_table_data':
                'contract_table_data':
            }
        }
        """
        id_in_subsession = group.id_in_subsession
        group_response = {}
        for player in group.get_players():
            id_in_group = player.id_in_group
            player_response = {
                'message_type': 'update',
                'order_book_data': flo_order_books[id_in_subsession].get_frontend_response(),
                'order_graph_data': flo_order_graphs[id_in_subsession][id_in_group].get_frontend_response(
                ),
                'inventory_chart_data': inventory_charts[id_in_subsession][id_in_group].get_frontend_response(
                ),
                'cash_chart_data': cash_charts[id_in_subsession][id_in_group].get_frontend_response(
                ),
                'status_chart_data': status_charts[id_in_subsession][id_in_group].get_frontend_response(
                ),
                'order_table_data': flo_order_tables[id_in_subsession][id_in_group].get_frontend_response(
                ),
                'contract_table_data': flo_contract_tables[id_in_subsession][id_in_group].get_frontend_response(),
            }
            group_response[id_in_group] = player_response
        return group_response


page_sequence = [FloMarketPage]
