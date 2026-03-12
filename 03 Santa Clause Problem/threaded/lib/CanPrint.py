from multiprocessing import Semaphore

class CanPrint:
    prefix: str = ""
    suffix: str = ""

    BLACK: str = "\033[30m"
    RED: str = "\033[31m"
    GREEN: str = "\033[32m"
    YELLOW: str = "\033[33m"
    BLUE: str = "\033[34m"
    MAGENTA: str = "\033[35m"
    CYAN: str = "\033[36m"
    WHITE: str = "\033[37m"
    DEFAULT: str = "\033[0m"

    console_color: str = "\033[0m"

    console_mutex = Semaphore(1)

    def __init__(self, prefix: str = "", suffix: str = "", color: str = None) -> None:
        if color is not None:
            self.console_color = color
        self.prefix = prefix
        self.suffix = suffix

    def print(self, msg) -> None:
        CanPrint.console_mutex.acquire()
        try:
            print(f"{self.console_color}{self.prefix}{msg}{self.suffix}{self.DEFAULT}", flush=True)
        finally:
            CanPrint.console_mutex.release()