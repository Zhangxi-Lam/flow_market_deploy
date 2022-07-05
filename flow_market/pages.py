from flow_market.common.inventory_chart import InventoryChart
from flow_market.common.cash_chart import CashChart
from flow_market.common.profit_chart import ProfitChart
from flow_market.common.status_chart import StatusChart
from flow_market.common.contract_table import ContractTable
from flow_market.common.order_table import OrderTable
from flow_market.common.my_timer import MyTimer

from .cda.cda_order_book import CdaOrderBook
from .cda.cda_order import CdaOrder
from .cda.cda_order_graph import CdaOrderGraph
from .flo.flo_order import FloOrder
from .flo.flo_order_book import FloOrderBook
from .flo.flo_config import FloConfig
from .flo.flo_order_graph import FloOrderGraph
from .config_parser import ConfigParser
from ._builtin import Page
from .models import Player, Group, Subsession


config = ConfigParser("flow_market/config/config.csv")
cda_order_books = {}
cda_order_graphs = {}  # {id_in_subsession: {id_in_group: CdaOrderGraph}}
cda_order_table = {}
flo_order_books = {}  # {id_in_subsession: FloOrderBook}
flo_order_graphs = {}  # {id_in_subsession: {id_in_group: FloOrderGraph}}
order_tables = {}  # {id_in_subsession: {id_in_group: OrderTable}}
contract_tables = {}  # {id_in_subsession: {id_in_group: FloContractTable}}
inventory_charts = {}  # {id_in_subsession: {id_in_group: InventoryChart}}
cash_charts = {}  # {id_in_subsession: {id_in_group: CashChart}}
profit_charts = {}  # {id_in_subsession: {id_in_group: ProfitChart}}
status_charts = {}  # {id_in_subsession: {id_in_group: StatusChart}}
timer = MyTimer()


class BaseMarketPage(Page):
    @staticmethod
    def get_order_book(r, id_in_subsession):
        if config.get_round_config(r)["treatment"] == "flo":
            return flo_order_books[r][id_in_subsession]
        return cda_order_books[r][id_in_subsession]

    @staticmethod
    def get_order_graph(r, id_in_subsession, id_in_group):
        if config.get_round_config(r)["treatment"] == "flo":
            return flo_order_graphs[r][id_in_subsession][id_in_group]
        return cda_order_graphs[r][id_in_subsession][id_in_group]

    @staticmethod
    def create_order(r, id_in_group, data, timestamp):
        if config.get_round_config(r)["treatment"] == "flo":
            return FloOrder(id_in_group, data, timestamp)
        return CdaOrder(id_in_group, data, timestamp)

    @staticmethod
    def live_method(player: Player, data):
        message_type = data["message_type"]
        r = player.subsession.round_number
        id_in_subsession = player.group.id_in_subsession
        id_in_group = player.id_in_group

        if r not in flo_order_books and r not in cda_order_books:
            BaseMarketPage.init(player.group.subsession)

        order_book = BaseMarketPage.get_order_book(r, id_in_subsession)
        order_graph = BaseMarketPage.get_order_graph(r, id_in_subsession, id_in_group)
        order_table = order_tables[r][id_in_subsession][id_in_group]

        if message_type == "order_graph_update_request":
            order_graph.send_update_to_frontend = True
            return
        elif message_type == "add_order":
            order = BaseMarketPage.create_order(r, id_in_group, data, timer.get_time())
            order_book.add_order(order)
            order_graph.add_order(order)
            order_table.add_order(order)
            return BaseMarketPage.respond(player.group)
        elif message_type == "remove_order":
            order = order_book.find_order(data["order_id"])
            order_book.remove_order(order)
            order_graph.remove_order(order)
            order_table.remove_order(order)
            return BaseMarketPage.respond(player.group)
        else:  # update
            if id_in_group != 1:
                # We only let the first player in the group do the update to
                # avoid duplicate transactions.
                return
            BaseMarketPage.update(player.group)
            return BaseMarketPage.respond(player.group)

    @staticmethod
    def init(subsession: Subsession):
        timer.reset()
        r = subsession.round_number
        c = config.get_round_config(r)
        if c["treatment"] == "flo":
            flo_order_books[r] = {}
            flo_order_graphs[r] = {}
        else:
            cda_order_books[r] = {}
            cda_order_graphs[r] = {}

        inventory_charts[r] = {}
        cash_charts[r] = {}
        order_tables[r] = {}
        contract_tables[r] = {}
        profit_charts[r] = {}
        status_charts[r] = {}

        for g in subsession.get_groups():
            id_in_subsession = g.id_in_subsession
            if c["treatment"] == "flo":
                flo_order_books[r][id_in_subsession] = FloOrderBook(c)
                flo_order_graphs[r][id_in_subsession] = {}
            else:
                cda_order_books[r][id_in_subsession] = CdaOrderBook(c)
                cda_order_graphs[r][id_in_subsession] = {}

            inventory_charts[r][id_in_subsession] = {}
            cash_charts[r][id_in_subsession] = {}
            order_tables[r][id_in_subsession] = {}
            contract_tables[r][id_in_subsession] = {}
            profit_charts[r][id_in_subsession] = {}
            status_charts[r][id_in_subsession] = {}
            for p in g.get_players():
                id_in_group = p.id_in_group
                if c["treatment"] == "flo":
                    flo_order_graphs[r][id_in_subsession][id_in_group] = FloOrderGraph()
                else:
                    cda_order_graphs[r][id_in_subsession][id_in_group] = CdaOrderGraph()
                inventory_charts[r][id_in_subsession][id_in_group] = InventoryChart(
                    timer
                )
                cash_charts[r][id_in_subsession][id_in_group] = CashChart(timer)
                order_tables[r][id_in_subsession][id_in_group] = OrderTable(
                    c["treatment"] == "flo"
                )
                contract_tables[r][id_in_subsession][id_in_group] = ContractTable(
                    id_in_subsession, id_in_group, timer
                )
                profit_charts[r][id_in_subsession][id_in_group] = ProfitChart(timer)
                status_charts[r][id_in_subsession][id_in_group] = StatusChart()

    @staticmethod
    def update(group: Group):
        timer.tick()
        r = group.subsession.round_number
        id_in_subsession = group.id_in_subsession

        # Order transaction
        completed_orders = BaseMarketPage.get_order_book(r, id_in_subsession).transact(
            group
        )
        for order in completed_orders:
            BaseMarketPage.get_order_graph(
                r, id_in_subsession, order.id_in_group
            ).remove_order(order)
            order_tables[r][id_in_subsession][order.id_in_group].remove_order(order)

        for player in group.get_players():
            id_in_group = player.id_in_group
            # Contract transaction
            contract_tables[r][id_in_subsession][id_in_group].update(player)
            inventory_charts[r][id_in_subsession][id_in_group].update(
                player.get_inventory()
            )
            cash_charts[r][id_in_subsession][id_in_group].update(player.get_cash())
            profit_charts[r][id_in_subsession][id_in_group].update(
                player,
                contract_tables[r][id_in_subsession][id_in_group].active_contracts,
            )
            status_charts[r][id_in_subsession][id_in_group].update(player)

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
        r = group.subsession.round_number
        id_in_subsession = group.id_in_subsession
        group_response = {}
        for player in group.get_players():
            id_in_group = player.id_in_group
            player_response = {
                "message_type": "update",
                "order_book_data": BaseMarketPage.get_order_book(
                    r, id_in_subsession
                ).get_frontend_response(),
                "order_graph_data": BaseMarketPage.get_order_graph(
                    r, id_in_subsession, id_in_group
                ).get_frontend_response(),
                "inventory_chart_data": inventory_charts[r][id_in_subsession][
                    id_in_group
                ].get_frontend_response(),
                "cash_chart_data": cash_charts[r][id_in_subsession][
                    id_in_group
                ].get_frontend_response(),
                "order_table_data": order_tables[r][id_in_subsession][
                    id_in_group
                ].get_frontend_response(),
                "contract_table_data": contract_tables[r][id_in_subsession][
                    id_in_group
                ].get_frontend_response(),
                "profit_chart_data": profit_charts[r][id_in_subsession][
                    id_in_group
                ].get_frontend_response(),
                "status_chart_data": status_charts[r][id_in_subsession][
                    id_in_group
                ].get_frontend_response(),
            }
            group_response[id_in_group] = player_response
        return group_response


class FloMarketPage(BaseMarketPage):
    def is_displayed(self):
        return config.get_round_config(self.round_number)["treatment"] == "flo"


class CdaMarketPage(BaseMarketPage):
    def is_displayed(self):
        return config.get_round_config(self.round_number)["treatment"] == "cda"


page_sequence = [FloMarketPage, CdaMarketPage]
