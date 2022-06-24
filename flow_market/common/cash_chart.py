from flow_market.common.my_timer import MyTimer


class CashChartPoint(dict):
    def __init__(self, time, cash):
        dict.__init__(self, x=time, y=cash)


class CashChart():
    def __init__(self, timer: MyTimer) -> None:
        self.timer = timer
        self.cash_data = []

    def get_frontend_response(self):
        return self.cash_data

    def update(self, cash):
        self.cash_data.append(CashChartPoint(
            self.timer.get_time(), cash))
