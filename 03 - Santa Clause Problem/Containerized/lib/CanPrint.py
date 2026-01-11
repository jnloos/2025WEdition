from datetime import datetime

class CanPrint:
    prefix: str = ""
    suffix: str = ""
    timestamp: bool = False

    def __init__(self, prefix: str = "", suffix: str = "", timestamp: bool = False):
        self.prefix = prefix
        self.suffix = suffix
        self.timestamp = timestamp

    def print(self, msg: str):
        ts = ""
        if self.timestamp:
            ts = f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] "
        print(f"{ts}{self.prefix}{msg}{self.suffix}", flush=True)
