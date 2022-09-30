import csv
from collections import namedtuple
import os


class FloBot:
    def __init__(self):
        self.ActionKey = namedtuple(
            "ActionKey", ["id_in_subsession", "id_in_group", "action", "timestamp"]
        )
        self.actions = {}

    def get_action(self, id_in_subsession, id_in_group, action, timestamp):
        k = self.ActionKey(id_in_subsession, id_in_group, action, timestamp)
        return self.actions.get(k, None)

    def load_actions(self, round_number):
        self.actions = {}
        path = "flow_market/bot/" + str(round_number) + "_flo.csv"
        if not os.path.exists(path):
            return
        with open(path) as f:
            rows = list(csv.DictReader(f))
        for r in rows:
            k = self.ActionKey(
                int(r["id_in_subsession"]),
                int(r["id_in_group"]),
                r["action"],
                int(r["timestamp"]),
            )
            v = {
                "direction": r["direction"],
                "max_price": float(r["max_price"]),
                "max_price_rate": float(r["max_price_rate"]),
                "min_price": float(r["min_price"]),
                "min_price_rate": float(r["min_price_rate"]),
                "quantity": float(r["quantity"]),
            }
            self.actions[k] = v
