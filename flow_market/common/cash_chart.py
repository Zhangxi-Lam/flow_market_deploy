class CashChartPoint(dict):
    def __init__(self, time, cash):
        dict.__init__(self, x=time, y=cash)


class CashChart():
    def __init__(self) -> None:
        self.time = None
        self.cash_data = []

    def get_sec_since_start(self):
        if self.time is None:
            self.time = 0
        else:
            self.time += 1
        return self.time

    def update(self, cash):
        self.cash_data.append(CashChartPoint(
            self.get_sec_since_start(), cash))

    def get_frontend_response(self):
        return self.cash_data
