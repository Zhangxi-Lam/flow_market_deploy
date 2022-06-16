import time


class InventoryChartPoint(dict):
    def __init__(self, time, inventory):
        dict.__init__(self, x=time, y=inventory)


class InventoryChart():
    def __init__(self, start_time) -> None:
        self.start_time = start_time
        self.inventory_data = []

    def get_frontend_response(self):
        return self.inventory_data

    def update(self, inventory):
        self.inventory_data.append(InventoryChartPoint(
            self.get_time(), inventory))

    def get_time(self):
        print(round(time.time() - self.start_time, 0),
              time.time() - self.start_time)
        return round(time.time() - self.start_time, 0)
