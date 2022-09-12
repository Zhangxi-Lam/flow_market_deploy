from flow_market.common.my_timer import MyTimer
from flow_market.common.player_info import PlayerInfo


class ProfitChartPoint(dict):
    def __init__(self, time, profit):
        dict.__init__(self, x=time, y=profit)


class ProfitChart:
    def __init__(self, timer: MyTimer) -> None:
        self.timer = timer
        self.profit_data = []

    def get_frontend_response(self):
        return self.profit_data

    def update(self, player_info: PlayerInfo, contracts):
        projected_profit = player_info.get_cash()
        uncovered_inventory = (
            0 if player_info.get_inventory() >= 0 else -player_info.get_inventory()
        )
        for c in contracts:
            if c.direction == "buy":
                if player_info.get_inventory() > 0:
                    projected_profit += c.price * min(
                        player_info.get_inventory(), c.quantity
                    )
            else:
                if player_info.get_inventory() < 0:
                    projected_profit -= c.price * min(
                        -player_info.get_inventory(), c.quantity
                    )
                uncovered_inventory -= c.quantity
        if uncovered_inventory > 0:
            projected_profit -= uncovered_inventory * 20
        self.profit_data.append(
            ProfitChartPoint(self.timer.get_time(), projected_profit)
        )
