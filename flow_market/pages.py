import time
from flow_market.common.inventory_chart import InventoryChart
from flow_market.common.cash_chart import CashChart
from flow_market.common.profit_chart import ProfitChart
from flow_market.common.status_chart import StatusChart
from flow_market.common.contract_table import ContractTable
from flow_market.common.order_table import OrderTable
from flow_market.common.my_timer import MyTimer
from flow_market.common.player_info import PlayerInfo

from .cda.cda_order_book import CdaOrderBook
from .cda.cda_order import CdaOrder
from .cda.cda_order_graph import CdaOrderGraph
from .cda.cda_bot import CdaBot
from .flo.flo_order import FloOrder
from .flo.flo_order_book import FloOrderBook
from .flo.flo_order_graph import FloOrderGraph
from .flo.flo_bot import FloBot
from .config_parser import ConfigParser
from .flo.flo_logger import FloLogger
from .cda.cda_logger import CdaLogger
from ._builtin import Page, WaitPage
from .models import Player, Group, Subsession, Constants


# Global
config = ConfigParser("flow_market/config/config.csv")
# Round level
flo_bot = FloBot()
cda_bot = CdaBot()
# Group level
timers = {}
cda_order_books = {}
flo_order_books = {}
# Player level
cda_order_graphs = {}
flo_order_graphs = {}
order_tables = {}
contract_tables = {}
inventory_charts = {}
cash_charts = {}
profit_charts = {}
status_charts = {}
player_infos = {}


class BaseMarketPage(Page):
    def before_next_page(self):
        player_info = player_infos[self.round_number][self.group.id_in_subsession][
            self.player.id_in_group
        ]
        player_info.cover_position()

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
        r = player.subsession.round_number
        id_in_subsession = player.group.id_in_subsession
        id_in_group = player.id_in_group
        message_type = data["message_type"]
        if r in timers:
            timer = timers[r][id_in_subsession]
            print(
                r,
                id_in_subsession,
                id_in_group,
                timer.get_time(),
                message_type,
                time.time(),
            )
        if message_type == "update" and player.id_in_group != 1:
            # Ignore the update request from other players.
            return {player.id_in_group: {"message_type": "stop"}}
        if r not in timers:
            BaseMarketPage.init(player.group.subsession)
        timer = timers[r][id_in_subsession]
        if timer.get_time() > config.get_round_config(r)["round_length"]:
            return {0: {"message_type": "stop", "time_remaining": 0}}

        if r not in flo_order_books and r not in cda_order_books:
            BaseMarketPage.init(player.group.subsession)

        order_book = BaseMarketPage.get_order_book(r, id_in_subsession)
        order_graph = BaseMarketPage.get_order_graph(r, id_in_subsession, id_in_group)
        order_table = order_tables[r][id_in_subsession][id_in_group]

        if message_type == "order_graph_update_request":
            # Update order graph for the player
            order_graph.send_update_to_frontend = True
            return
        elif message_type == "add_order":
            # Add order for the player
            order = BaseMarketPage.create_order(r, id_in_group, data, timer.get_time())
            order_book.add_order(order)
            order_graph.add_order(order)
            order_table.add_order(order)
        elif message_type == "remove_order":
            # Remove order for the player
            order = order_book.find_order(data["order_id"])
            order_book.remove_order(order)
            order_graph.remove_order(order)
            order_table.remove_order(order)
        else:
            # Update the entire group.
            # Get actions from Bot
            if config.get_round_config(r)["treatment"] == "flo":
                func = flo_bot.pop_action
            else:
                func = cda_bot.pop_action
            for p in player.group.get_players():
                data = func(
                    id_in_subsession, p.id_in_group, "add_order", timer.get_time()
                )
                if data:
                    order = BaseMarketPage.create_order(
                        r, p.id_in_group, data, timer.get_time()
                    )
                    order_book.add_order(order)
                    BaseMarketPage.get_order_graph(
                        r, id_in_subsession, p.id_in_group
                    ).add_order(order)
                    order_tables[r][id_in_subsession][p.id_in_group].add_order(order)
            BaseMarketPage.log(timer, player.group, before_transaction=True)
            BaseMarketPage.update(player.group)
            BaseMarketPage.log(timer, player.group, before_transaction=False)
            response = BaseMarketPage.respond(timer, player.group)
            timer.tick()
            return response

    @staticmethod
    def init(subsession: Subsession):
        r = subsession.round_number
        c = config.get_round_config(r)
        timers[r] = {}
        if c["treatment"] == "flo":
            flo_order_books[r] = {}
            flo_order_graphs[r] = {}
            flo_bot.load_actions(r)
        else:
            cda_order_books[r] = {}
            cda_order_graphs[r] = {}
            cda_bot.load_actions(r)

        inventory_charts[r] = {}
        cash_charts[r] = {}
        order_tables[r] = {}
        contract_tables[r] = {}
        profit_charts[r] = {}
        status_charts[r] = {}
        player_infos[r] = {}

        for g in subsession.get_groups():
            id_in_subsession = g.id_in_subsession
            timers[r][id_in_subsession] = MyTimer()
            if c["treatment"] == "flo":
                flo_order_books[r][id_in_subsession] = FloOrderBook()
                flo_order_graphs[r][id_in_subsession] = {}
            else:
                cda_order_books[r][id_in_subsession] = CdaOrderBook()
                cda_order_graphs[r][id_in_subsession] = {}

            inventory_charts[r][id_in_subsession] = {}
            cash_charts[r][id_in_subsession] = {}
            order_tables[r][id_in_subsession] = {}
            contract_tables[r][id_in_subsession] = {}
            profit_charts[r][id_in_subsession] = {}
            status_charts[r][id_in_subsession] = {}
            player_infos[r][id_in_subsession] = {}
            for p in g.get_players():
                id_in_group = p.id_in_group
                timer = timers[r][id_in_subsession]
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
                    id_in_subsession, id_in_group, r, timer
                )
                profit_charts[r][id_in_subsession][id_in_group] = ProfitChart(timer)
                status_charts[r][id_in_subsession][id_in_group] = StatusChart()
                player_infos[r][id_in_subsession][id_in_group] = PlayerInfo()

    @staticmethod
    def update(group: Group):
        r = group.subsession.round_number
        id_in_subsession = group.id_in_subsession

        # Order transaction
        completed_orders = BaseMarketPage.get_order_book(r, id_in_subsession).transact(
            group, player_infos[r][id_in_subsession]
        )
        for order in completed_orders:
            BaseMarketPage.get_order_graph(
                r, id_in_subsession, order.id_in_group
            ).remove_order(order)
            order_tables[r][id_in_subsession][order.id_in_group].remove_order(order)

        for player in group.get_players():
            id_in_group = player.id_in_group
            player_info = player_infos[r][id_in_subsession][id_in_group]
            # Contract transaction
            contract_tables[r][id_in_subsession][id_in_group].update(player_info)
            inventory_charts[r][id_in_subsession][id_in_group].update(
                player_info.get_inventory()
            )
            cash_charts[r][id_in_subsession][id_in_group].update(player_info.get_cash())
            profit_charts[r][id_in_subsession][id_in_group].update(
                player_info,
                contract_tables[r][id_in_subsession][id_in_group].active_contracts,
            )
            status_charts[r][id_in_subsession][id_in_group].update(player_info)

    @staticmethod
    def log(timer: MyTimer, group: Group, before_transaction):
        r = group.subsession.round_number
        if config.get_round_config(r)["treatment"] == "flo":
            FloMarketPage.log(timer, group, before_transaction)
        else:
            CdaMarketPage.log(timer, group, before_transaction)

    @staticmethod
    def respond(timer: MyTimer, group: Group):
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
                "message_type": "update" if id_in_group == 1 else "stop",
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
                "time_remaining": config.get_round_config(r)["round_length"]
                - timer.get_time(),
            }
            group_response[id_in_group] = player_response
        return group_response


class FloMarketPage(BaseMarketPage):
    flo_logger = None

    def is_displayed(self):
        if config.get_round_config(self.round_number)["treatment"] == "flo":
            FloMarketPage.flo_logger = FloLogger(self.round_number)
            return True
        else:
            return False

    @staticmethod
    def log(timer: MyTimer, group: Group, before_transaction):
        r = group.subsession.round_number
        id_in_subsession = group.id_in_subsession
        order_book = BaseMarketPage.get_order_book(r, id_in_subsession)
        FloMarketPage.flo_logger.update_market_data(
            timer.get_time(), id_in_subsession, before_transaction, order_book
        )
        for player in group.get_players():
            id_in_group = player.id_in_group
            contract_table = contract_tables[r][id_in_subsession][id_in_group]
            player_info = player_infos[r][id_in_subsession][id_in_group]
            FloMarketPage.flo_logger.update_participant_data(
                timer.get_time(),
                before_transaction,
                player,
                player_info,
                order_book,
                contract_table,
            )


class CdaMarketPage(BaseMarketPage):
    cda_logger = None

    def is_displayed(self):
        if config.get_round_config(self.round_number)["treatment"] == "cda":
            CdaMarketPage.cda_logger = CdaLogger(self.round_number)
            return True
        else:
            return False

    @staticmethod
    def log(timer: MyTimer, group: Group, before_transaction):
        r = group.subsession.round_number
        id_in_subsession = group.id_in_subsession
        order_book = BaseMarketPage.get_order_book(r, id_in_subsession)
        CdaMarketPage.cda_logger.update_market_data(
            timer.get_time(), id_in_subsession, before_transaction, order_book
        )
        for player in group.get_players():
            id_in_group = player.id_in_group
            contract_table = contract_tables[r][id_in_subsession][id_in_group]
            player_info = player_infos[r][id_in_subsession][id_in_group]
            CdaMarketPage.cda_logger.update_participant_data(
                timer.get_time(),
                before_transaction,
                player,
                player_info,
                order_book,
                contract_table,
            )


class RoundResultPage(Page):
    def get_timeout_seconds(self):
        return 20

    def vars_for_template(self):
        data = []
        for r in range(1, self.round_number + 1):
            player_info = player_infos[r][self.group.id_in_subsession][
                self.player.id_in_group
            ]
            data.append(
                {
                    "round_number": r,
                    "practice": config.get_round_config(r)["practice"],
                    "profit_from_contract": round(player_info.profit_from_contract, 2),
                    "profit_from_trading": round(player_info.profit_from_trading, 2),
                    "profit": round(
                        player_info.profit_from_contract
                        + player_info.profit_from_trading,
                        2,
                    ),
                }
            )
        return {"data": data}


class FinalResultPage(Page):
    def is_displayed(self):
        return self.round_number == Constants.num_rounds

    def get_timeout_seconds(self):
        return 20

    def vars_for_template(self):
        total = 0
        data = []
        for r in range(1, self.round_number + 1):
            if config.get_round_config(r)["practice"]:
                # Practice rounds don't count
                continue
            player_info = player_infos[r][self.group.id_in_subsession][
                self.player.id_in_group
            ]
            total += round(
                player_info.profit_from_contract + player_info.profit_from_trading, 2
            )
            data.append(
                {
                    "round_number": r,
                    "profit": round(
                        player_info.profit_from_contract
                        + player_info.profit_from_trading,
                        2,
                    ),
                }
            )
        return {"total_profit": total, "data": data}


class WaitStart(WaitPage):
    body_text = "Waiting for all players to be ready"
    wait_for_all_groups = False


class IntroPage(Page):
    def is_displayed(self):
        return self.round_number == 1

    def vars_for_template(self):
        r = self.group.subsession.round_number
        treatment = config.get_round_config(r)["treatment"]
        return {"treatment": treatment}


page_sequence = [
    IntroPage,
    WaitStart,
    FloMarketPage,
    CdaMarketPage,
    RoundResultPage,
    FinalResultPage,
]
