import csv
import os
import time
from ..models import Player
from .my_timer import MyTimer
from flow_market.common.player_info import PlayerInfo


class Contract(dict):
    def __init__(
        self,
        id_in_subsession,
        id_in_group,
        direction,
        price,
        quantity,
        showtime,
        deadline,
    ):
        dict.__init__(
            self,
            id_in_subsession=int(id_in_subsession),
            id_in_group=int(id_in_group),
            direction=direction,
            price=float(price),
            quantity=float(quantity),
            fill_quantity=0,
            showtime=int(showtime),
            deadline=int(deadline),
            time_remaining=0,
            has_executed=False,
        )

    def __setattr__(self, field: str, value):
        self[field] = value

    def __getattr__(self, field: str):
        return self[field]

    def update(self, t: int):
        if t < self.deadline:
            self.time_remaining = round(self.deadline - t, 0)

    def execute(self, fill_quantity):
        self.fill_quantity = fill_quantity


class ContractTable:
    def __init__(
        self,
        players_per_group,
        id_in_subsession,
        id_in_group,
        round_number,
        timer: MyTimer,
    ) -> None:
        self.id_in_subsession = id_in_subsession
        self.id_in_group = id_in_group
        self.timer = timer
        self.contracts = self.get_contracts(players_per_group, round_number)
        self.active_contracts = []
        self.executed_contracts = []

    def get_frontend_response(self):
        return {
            "active_contracts": self.active_contracts,
            "executed_contracts": self.executed_contracts,
        }

    def has_buy_contract(self):
        for c in self.contracts:
            if c.direction == "buy":
                return True
        return False

    def update(self, player_info: PlayerInfo):
        self.active_contracts = []
        t = self.timer.get_time()
        for c in self.contracts:
            if t >= c.deadline:
                if not c.has_executed:
                    self.execute(c, player_info)
                    self.executed_contracts.append(c)
            elif t >= c.showtime:
                c.update(t)
                self.active_contracts.append(c)

    def execute(self, contract, player_info: PlayerInfo):
        contract.has_executed = True
        if contract["direction"] == "buy":
            fill_quantity = (
                min(player_info.get_inventory(), contract.quantity)
                if player_info.get_inventory() > 0
                else 0
            )
            player_info.update("sell", fill_quantity, contract.price, is_trade=False)
            contract.execute(fill_quantity)
        else:
            fill_quantity = (
                min(-player_info.get_inventory(), contract.quantity)
                if player_info.get_inventory() < 0
                else 0
            )
            player_info.update("buy", fill_quantity, contract.price, is_trade=False)
            contract.execute(fill_quantity)

    def get_contracts(self, players_per_group, round_number):
        contracts = []
        path = (
            "flow_market/config/contracts_"
            + str(players_per_group)
            + "/"
            + str(round_number)
            + "_contracts.csv"
        )
        if not os.path.exists(path):
            return contracts
        with open(path) as infile:
            rows = list(csv.DictReader(infile))
        for r in rows:
            contract = Contract(
                r["id_in_subsession"],
                r["id_in_group"],
                r["direction"],
                r["price"],
                r["quantity"],
                r["showtime"],
                r["deadline"],
            )
            if (
                self.id_in_subsession == contract.id_in_subsession
                and self.id_in_group == contract.id_in_group
            ):
                contracts.append(contract)
        return contracts
