import time


class StatusBar:
    total_units: int
    start_time: float

    def __init__(self, total_units: int):
        self.total_units = total_units
        self.start_time = time.time()

    def print_status(self, current_unit: int):
        percentage = (current_unit / self.total_units) * 100
        elapsed_time = time.time() - self.start_time
        remaining_time = (elapsed_time / current_unit) * (self.total_units - current_unit) if current_unit > 0 else 0
        print(f"\rProgress: {percentage:3.2f}% ({current_unit}/{self.total_units}) - Elapsed Time: {elapsed_time:5.2f} seconds - Remaining Time: {remaining_time:5.2f} seconds", end="")
