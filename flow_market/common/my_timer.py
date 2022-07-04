class MyTimer:
    def __init__(self) -> None:
        self.time = None

    def tick(self):
        if self.time is None:
            self.time = 0
        else:
            self.time += 1

    def get_time(self):
        return self.time

    def reset(self):
        self.time = None
