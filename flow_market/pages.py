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
loggers = {}
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
    # Cover short positions before next page.
    def before_next_page(self):
        player_info = player_infos[self.round_number][self.group.id_in_subsession][
            self.player.id_in_group
        ]
        player_info.cover_position()
        if self.player.id_in_group == 1:
            # Let the first player update the log
            BaseMarketPage.write_log(self.group)

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
    def can_add_order(r, id_in_subsession, id_in_group, order):
        contract_table = contract_tables[r][id_in_subsession][id_in_group]
        active_contracts = contract_table.active_contracts
        if not active_contracts:
            return True
        if len(active_contracts) > 1:
            raise ValueError("Player has more than 1 active contracts.")
            return False
        contract_direction, contract_quantity = (
            active_contracts[0].direction,
            active_contracts[0].quantity,
        )
        order_direction, order_quantity = order.direction, order.quantity
        inventory = player_infos[r][id_in_subsession][id_in_group].get_inventory()
        if contract_direction == "buy":
            if order_direction == "buy":
                return inventory + order.quantity <= contract_quantity
            else:
                return order_quantity <= inventory
        else:
            if order_quantity == "buy":
                return order_quantity <= abs(inventory)
            else:
                return abs(inventory) + order_quantity <= contract_quantity

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
        # Print debug message
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
        timer = timers[r][id_in_subsession]
        timestamp = timer.get_time()
        if timestamp >= config.get_round_config(r)["round_length"]:
            return {0: {"message_type": "stop", "time_remaining": 0}}

        order_book = BaseMarketPage.get_order_book(r, id_in_subsession)
        order_graph = BaseMarketPage.get_order_graph(r, id_in_subsession, id_in_group)
        order_table = order_tables[r][id_in_subsession][id_in_group]

        if message_type == "order_graph_update_request":
            # Update order graph for the player
            order_graph.send_update_to_frontend = True
            return
        elif message_type == "add_order":
            # Add order for the player
            if order_book.has_order(id_in_group, data["direction"]):
                # Don't add multiple buy/sell orders.
                return
            order = BaseMarketPage.create_order(r, id_in_group, data, timestamp)
            if not config.get_round_config(r)[
                "free_trade"
            ] and not BaseMarketPage.can_add_order(
                r, id_in_subsession, id_in_group, order
            ):
                return {id_in_group: {"message_type": "invalid_order"}}
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
                data = func(id_in_subsession, p.id_in_group, "add_order", timestamp)
                if data and not order_book.has_order(p.id_in_group, data["direction"]):
                    order = BaseMarketPage.create_order(
                        r, p.id_in_group, data, timestamp
                    )
                    order_book.add_order(order)
                    BaseMarketPage.get_order_graph(
                        r, id_in_subsession, p.id_in_group
                    ).add_order(order)
                    order_tables[r][id_in_subsession][p.id_in_group].add_order(order)
            BaseMarketPage.add_log(timestamp, player.group, before_transaction=True)
            BaseMarketPage.update(player.group)
            BaseMarketPage.add_log(timestamp, player.group, before_transaction=False)
            response = BaseMarketPage.respond(timestamp, player.group)
            timer.tick()
            return response

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
    def add_log(timestamp, group: Group, before_transaction):
        r = group.subsession.round_number
        id_in_subsession = group.id_in_subsession
        order_book = BaseMarketPage.get_order_book(r, id_in_subsession)
        logger = loggers[r][id_in_subsession]
        logger.update_market_data(
            timestamp, id_in_subsession, before_transaction, order_book
        )
        for player in group.get_players():
            id_in_group = player.id_in_group
            contract_table = contract_tables[r][id_in_subsession][id_in_group]
            player_info = player_infos[r][id_in_subsession][id_in_group]
            logger.update_participant_data(
                timestamp,
                before_transaction,
                player,
                player_info,
                order_book,
                contract_table,
            )

    @staticmethod
    def write_log(group):
        r = group.subsession.round_number
        id_in_subsession = group.id_in_subsession
        logger = loggers[r][id_in_subsession]
        logger.write_log()

    @staticmethod
    def respond(timestamp, group: Group):
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
                - timestamp,
            }
            group_response[id_in_group] = player_response
        return group_response


class FloMarketPage(BaseMarketPage):
    def is_displayed(self):
        if config.get_round_config(self.round_number)["treatment"] == "flo":
            return True
        else:
            return False


class CdaMarketPage(BaseMarketPage):
    def is_displayed(self):
        if config.get_round_config(self.round_number)["treatment"] == "cda":
            return True
        else:
            return False


class RoundResultPage(Page):
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
        if self.subsession.round_number not in timers:
            self.init()
        return self.round_number == 1

    def vars_for_template(self):
        r = self.group.subsession.round_number
        treatment = config.get_round_config(r)["treatment"]
        return {"treatment": treatment}

    def init(self):
        subsession = self.subsession
        r = subsession.round_number
        c = config.get_round_config(r)
        timers[r] = {}
        loggers[r] = {}
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
                loggers[r][id_in_subsession] = FloLogger(r, id_in_subsession)
            else:
                cda_order_books[r][id_in_subsession] = CdaOrderBook()
                cda_order_graphs[r][id_in_subsession] = {}
                loggers[r][id_in_subsession] = CdaLogger(r, id_in_subsession)

            inventory_charts[r][id_in_subsession] = {}
            cash_charts[r][id_in_subsession] = {}
            order_tables[r][id_in_subsession] = {}
            contract_tables[r][id_in_subsession] = {}
            profit_charts[r][id_in_subsession] = {}
            status_charts[r][id_in_subsession] = {}
            player_infos[r][id_in_subsession] = {}

            timer = timers[r][id_in_subsession]
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
                    Constants.players_per_group, id_in_subsession, id_in_group, r, timer
                )
                profit_charts[r][id_in_subsession][id_in_group] = ProfitChart(timer)
                status_charts[r][id_in_subsession][id_in_group] = StatusChart()
                player_infos[r][id_in_subsession][id_in_group] = PlayerInfo()


class FloBuyerQuizPage(Page):
    form_model = "player"
    form_fields = [
        "flo_buyer_quiz1",
        "flo_buyer_quiz2",
        "flo_buyer_quiz3",
        "flo_buyer_quiz4",
        "flo_buyer_quiz5",
        "flo_buyer_quiz6",
        "flo_buyer_quiz7",
        "flo_buyer_quiz8",
        "flo_buyer_quiz9",
        "flo_buyer_quiz10",
        "flo_buyer_quiz11",
    ]

    def is_displayed(self):
        return (
            self.round_number == 1
            and config.get_round_config(self.round_number)["treatment"] == "flo"
            and contract_tables[self.round_number][self.group.id_in_subsession][
                self.player.id_in_group
            ].has_buy_contract()
        )

    @staticmethod
    def error_message(values):
        solutions = dict(
            flo_buyer_quiz1="Buy order",
            flo_buyer_quiz2=15,
            flo_buyer_quiz3=10,
            flo_buyer_quiz4=5,
            flo_buyer_quiz5=400,
            flo_buyer_quiz6="No",
            flo_buyer_quiz7="0 unit per second",
            flo_buyer_quiz8="5 units per second",
            flo_buyer_quiz9="(12 - 10) * 300 = 600",
            flo_buyer_quiz10="(12 - 10) * 500 = 1000",
            flo_buyer_quiz11="(12 - 10) * 500 + (0 - 10) * 100 = 0",
        )
        errors = {
            name: "Wrong" for name in solutions if values[name] != solutions[name]
        }
        return errors


class FloSellerQuizPage(Page):
    form_model = "player"
    form_fields = [
        "flo_seller_quiz1",
        "flo_seller_quiz2",
        "flo_seller_quiz3",
        "flo_seller_quiz4",
        "flo_seller_quiz5",
        "flo_seller_quiz6",
        "flo_seller_quiz7",
        "flo_seller_quiz8",
        "flo_seller_quiz9",
        "flo_seller_quiz10",
        "flo_seller_quiz11",
    ]

    def is_displayed(self):
        return (
            self.round_number == 1
            and config.get_round_config(self.round_number)["treatment"] == "flo"
            and not contract_tables[self.round_number][self.group.id_in_subsession][
                self.player.id_in_group
            ].has_buy_contract()
        )

    @staticmethod
    def error_message(values):
        solutions = dict(
            flo_seller_quiz1="Sell order",
            flo_seller_quiz2=14,
            flo_seller_quiz3=10,
            flo_seller_quiz4=6,
            flo_seller_quiz5=600,
            flo_seller_quiz6="Yes",
            flo_seller_quiz7="0 unit per second",
            flo_seller_quiz8="6 units per second",
            flo_seller_quiz9="(10 - 8) * 300 = 600",
            flo_seller_quiz10="(10 - 8) * 500 = 1000",
            flo_seller_quiz11="(10 - 8) * 500 + (10 - 20) * 100 = 0",
        )
        errors = {
            name: "Wrong" for name in solutions if values[name] != solutions[name]
        }
        return errors


class CdaBuyerQuizPage(Page):
    form_model = "player"
    form_fields = [
        "cda_buyer_quiz1",
        "cda_buyer_quiz2",
        "cda_buyer_quiz3",
        "cda_buyer_quiz4",
        "cda_buyer_quiz5",
        "cda_buyer_quiz6",
        "cda_buyer_quiz7",
    ]

    def is_displayed(self):
        return (
            self.round_number == 1
            and config.get_round_config(self.round_number)["treatment"] == "cda"
            and contract_tables[self.round_number][self.group.id_in_subsession][
                self.player.id_in_group
            ].has_buy_contract()
        )

    @staticmethod
    def error_message(values):
        solutions = dict(
            cda_buyer_quiz1="Buy order",
            cda_buyer_quiz2=18,
            cda_buyer_quiz3=14,
            cda_buyer_quiz4=20,
            cda_buyer_quiz5="(12 - 10) * 300 = 600",
            cda_buyer_quiz6="(12 - 10) * 500 = 1000",
            cda_buyer_quiz7="(12 - 10) * 500 + (0 - 10) * 100 = 0",
        )
        errors = {
            name: "Wrong" for name in solutions if values[name] != solutions[name]
        }
        return errors


class CdaSellerQuizPage(Page):
    form_model = "player"
    form_fields = [
        "cda_seller_quiz1",
        "cda_seller_quiz2",
        "cda_seller_quiz3",
        "cda_seller_quiz4",
        "cda_seller_quiz5",
        "cda_seller_quiz6",
        "cda_seller_quiz7",
    ]

    def is_displayed(self):
        return (
            self.round_number == 1
            and config.get_round_config(self.round_number)["treatment"] == "cda"
            and not contract_tables[self.round_number][self.group.id_in_subsession][
                self.player.id_in_group
            ].has_buy_contract()
        )

    @staticmethod
    def error_message(values):
        solutions = dict(
            cda_seller_quiz1="Sell order",
            cda_seller_quiz2=15,
            cda_seller_quiz3=12,
            cda_seller_quiz4=20,
            cda_seller_quiz5="(10 - 8) * 300 = 600",
            cda_seller_quiz6="(10 - 8) * 500 = 1000",
            cda_seller_quiz7="(10 - 8) * 500 + (10 - 20) * 100 = 0",
        )
        errors = {
            name: "Wrong" for name in solutions if values[name] != solutions[name]
        }
        return errors


page_sequence = [
    IntroPage,
    FloBuyerQuizPage,
    FloSellerQuizPage,
    CdaBuyerQuizPage,
    CdaSellerQuizPage,
    WaitStart,
    FloMarketPage,
    CdaMarketPage,
    RoundResultPage,
    FinalResultPage,
]
