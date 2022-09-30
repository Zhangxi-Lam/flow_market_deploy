class MyTimer:
    def __init__(self) -> None:
        self.time = 0

    def tick(self):
        self.time += 1

    def get_time(self):
        return self.time

    def reset(self):
        self.time = 0
