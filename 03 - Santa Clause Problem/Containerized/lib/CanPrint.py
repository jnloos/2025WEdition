class CanPrint:
    prefix: str = ""
    suffix: str = ""

    def __init__(self, prefix: str = "", suffix: str = ""):
        self.prefix = prefix
        self.suffix = suffix

    def log(self, msg: str):
        print(f"{self.prefix}{msg}{self.suffix}", flush=True)
