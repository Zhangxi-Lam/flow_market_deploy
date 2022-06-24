from flow_market.common.my_timer import MyTimer
from flow_market.models import Player


class ProfitChartPoint(dict):
    def __init__(self, time, profit):
        dict.__init__(self, x=time, y=profit)


class ProfitChart():
    def __init__(self, timer: MyTimer) -> None:
        self.timer = timer
        self.profit_data = []

    def get_frontend_response(self):
        return self.profit_data

    def update(self, player: Player, contracts):
        projected_profit = player.get_cash()
        for c in contracts:
            if c.direction == 'buy':
                if player.get_inventory() > 0:
                    projected_profit += c.price * \
                        min(player.get_inventory(), c.quantity)
            else:
                if player.get_inventory() < 0:
                    projected_profit -= c.price * \
                        min(-player.get_inventory(), c.quantity)
        self.profit_data.append(ProfitChartPoint(
            self.timer.get_time(), projected_profit))
