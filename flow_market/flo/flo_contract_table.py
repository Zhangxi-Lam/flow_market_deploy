import csv
import time
from ..models import Player


class Contract(dict):
    def __init__(self, id_in_subsession, id_in_group, direction, price,
                 quantity, showtime, deadline):
        dict.__init__(self, id_in_subsession=int(id_in_subsession),
                      id_in_group=int(id_in_group),
                      direction=direction,
                      price=float(price),
                      quantity=int(quantity),
                      showtime=int(showtime),
                      deadline=int(deadline),
                      remaining=0,
                      has_executed=False)

    def __setattr__(self, field: str, value):
        self[field] = value

    def __getattr__(self, field: str):
        return self[field]

    def update(self, t: int):
        if t < self.deadline:
            self.remaining = round(self.deadline - t, 0)


class FloContractTable():
    def __init__(self, id_in_subsession, id_in_group, start_time) -> None:
        self.id_in_subsession = id_in_subsession
        self.id_in_group = id_in_group
        self.start_time = start_time
        self.contracts = self.get_contracts()
        self.active_contracts = []
        self.executed_contracts = []

    def get_frontend_response(self):
        return {
            'active_contracts': self.active_contracts,
            'executed_contracts': self.executed_contracts
        }

    def update(self, player: Player):
        self.active_contracts = []
        t = self.get_time()
        for c in self.contracts:
            if t >= c.deadline:
                if not c.has_executed:
                    self.execute(c, player)
                    self.executed_contracts.append(c)
            elif t >= c.showtime:
                c.update(t)
                self.active_contracts.append(c)

    def execute(self, contract, player: Player):
        contract.has_executed = True
        is_buy = contract['direction']
        if is_buy:
            player.inventory -= contract['quantity']
            player.cash += contract['quantity'] * contract['price']
        else:
            player.inventory += contract['quantity']
            player.cash -= contract['quantity'] * contract['price']

    def get_contracts(self):
        contracts = []
        path = 'flow_market/config/contracts.csv'
        with open(path) as infile:
            rows = list(csv.DictReader(infile))
        for r in rows:
            contract = Contract(r['id_in_subsession'],
                                r['id_in_group'],
                                r['direction'],
                                r['price'],
                                r['quantity'],
                                r['showtime'],
                                r['deadline'])
            if self.id_in_group == contract.id_in_group:
                contracts.append(contract)
        return contracts

    def get_time(self):
        return round(time.time() - self.start_time, 0)
