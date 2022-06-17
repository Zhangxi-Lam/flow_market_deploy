import time

from flow_market.common.my_timer import MyTimer


class InventoryChartPoint(dict):
    def __init__(self, time, inventory):
        dict.__init__(self, x=time, y=inventory)


class InventoryChart():
    def __init__(self, timer: MyTimer) -> None:
        self.timer = timer
        self.inventory_data = []

    def get_frontend_response(self):
        return self.inventory_data

    def update(self, inventory):
        self.inventory_data.append(InventoryChartPoint(
            self.timer.get_time(), inventory))
