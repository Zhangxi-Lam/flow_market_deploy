import csv
from collections import namedtuple


class FloBot:
    def __init__(self):
        self.ActionKey = namedtuple(
            "ActionKey", ["id_in_subsession", "id_in_group", "action", "timestamp"]
        )

    def get_action(self, id_in_subsession, id_in_group, action, timestamp):
        k = self.ActionKey(id_in_subsession, id_in_group, action, timestamp)
        return self.actions.get(k, None)

    def load_actions(self, r):
        self.actions = {}

        path = "flow_market/bot/" + str(r) + ".csv"
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
                "max_rate": float(r["max_rate"]),
                "min_price": float(r["min_price"]),
                "min_rate": float(r["min_rate"]),
                "quantity": float(r["quantity"]),
            }
            self.actions[k] = v
