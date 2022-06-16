import time


class CashChartPoint(dict):
    def __init__(self, time, cash):
        dict.__init__(self, x=time, y=cash)


class CashChart():
    def __init__(self, start_time) -> None:
        self.start_time = start_time
        self.cash_data = []

    def get_frontend_response(self):
        return self.cash_data

    def update(self, cash):
        self.cash_data.append(CashChartPoint(
            self.get_time(), cash))

    def get_time(self):
        return round(time.time() - self.start_time, 0)
