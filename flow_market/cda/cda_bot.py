import csv
from collections import namedtuple


class CdaBot:
    def __init__(self):
        self.ActionKey = namedtuple(
            "ActionKey", ["id_in_subsession", "id_in_group", "action", "timestamp"]
        )

    def get_action(self, id_in_subsession, id_in_group, action, timestamp):
        k = self.ActionKey(id_in_subsession, id_in_group, action, timestamp)
        return self.actions.get(k, None)

    def load_actions(self, r):
        self.actions = {}

        path = "flow_market/bot/" + str(r) + "_cda.csv"
        try:
            with open(path) as f:
                rows = list(csv.DictReader(f))
        except FileNotFoundError as e:
            print(
                "Can not find bot file "
                + e.filename
                + "for this round. No bot will be added."
            )
            self.actions = {}
            return
        for r in rows:
            k = self.ActionKey(
                int(r["id_in_subsession"]),
                int(r["id_in_group"]),
                r["action"],
                int(r["timestamp"]),
            )
            v = {
                "direction": r["direction"],
                "price": float(r["price"]),
                "quantity": float(r["quantity"]),
            }
            self.actions[k] = v
