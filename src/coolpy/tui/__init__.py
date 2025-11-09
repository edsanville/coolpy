import time


def color_text(text: str, color: str) -> str:
    color_codes = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m',
        'reset': '\033[0m'
    }
    return f"{color_codes.get(color, '')}{text}{color_codes['reset']}"


def pretty_time_string(total_seconds: float) -> str:
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)

    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


class StatusBar:
    total_units: int
    start_time: float

    update_interval: float = 1.0
    last_update_time: float

    def __init__(self, total_units: int, update_interval: float = 1.0):
        self.total_units = total_units
        self.start_time = time.time()
        self.update_interval = update_interval
        self.last_update_time = self.start_time


    def print_status(self, current_unit: int):
        if time.time() - self.last_update_time < self.update_interval:
            return

        percentage = (current_unit / self.total_units) * 100
        elapsed_time = time.time() - self.start_time
        remaining_time = (elapsed_time / current_unit) * (self.total_units - current_unit) if current_unit > 0 else 0
        print(f"\rProgress: {percentage:3.2f}% ({current_unit}/{self.total_units})"
              f" - Elapsed Time: {pretty_time_string(elapsed_time)} - Remaining Time: {pretty_time_string(remaining_time)}", end="")
        self.last_update_time = time.time()


    def finish(self):
        total_time = time.time() - self.start_time
        print(color_text(f"\n==> Completed {self.total_units} items in {total_time:5.2f} seconds.", 'green'))
