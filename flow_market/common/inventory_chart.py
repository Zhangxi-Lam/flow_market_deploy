class InventoryChartPoint(dict):
    def __init__(self, time, inventory):
        dict.__init__(self, x=time, y=inventory)


class InventoryChart():
    def __init__(self) -> None:
        self.time = None
        self.inventory_data = []

    def get_sec_since_start(self):
        if self.time is None:
            self.time = 0
        else:
            self.time += 1
        return self.time

    def update(self, inventory):
        self.inventory_data.append(InventoryChartPoint(
            self.get_sec_since_start(), inventory))

    def get_frontend_response(self):
        return self.inventory_data
