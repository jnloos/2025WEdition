import threading
from queue import Queue
from datetime import datetime
import zmq

from .config import *

class CanPrintZMQ:
    def __init__(self, log_host=None, prefix: str="", suffix: str="", timestamp: bool=False):
        self.prefix = prefix
        self.suffix = suffix
        self.timestamp = timestamp
        self.log_host = log_host

        self.ctx = zmq.Context.instance()

        # Server mode: receives and prints logs
        if self.log_host is None:
            self.log_queue = Queue()

            self.pull_socket = self.ctx.socket(zmq.PULL)
            self.pull_socket.bind(f"tcp://*:{PORT_DEBUG_LOGGING}")

            threading.Thread(target=self._recv_logs_loop, daemon=True).start()
            threading.Thread(target=self._print_logs_loop, daemon=True).start()

        # Client mode: sends logs
        else:
            self.push_socket = self.ctx.socket(zmq.PUSH)
            self.push_socket.connect(f"tcp://{self.log_host}:{PORT_DEBUG_LOGGING}")

    def _recv_logs_loop(self):
        while True:
            record = self.pull_socket.recv_json()
            self.log_queue.put(record["msg"])

    def _print_logs_loop(self):
        while True:
            msg = self.log_queue.get()
            print(msg, flush=True)

    def _format(self, msg: str) -> str:
        if self.timestamp:
            ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            return f"[{ts}] {self.prefix}{msg}{self.suffix}"
        return f"{self.prefix}{msg}{self.suffix}"

    def print(self, msg: str):
        formatted = self._format(msg)
        if self.log_host is None:
            self.log_queue.put(formatted)
        else:
            self.push_socket.send_json({"msg": formatted})
