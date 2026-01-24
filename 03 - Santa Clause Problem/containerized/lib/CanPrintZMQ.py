import threading
import time
from datetime import datetime
from heapq import heappush, heappop
import zmq

from .config import *

class CanPrintZMQ:
    def __init__(self, log_host=None, prefix: str="", suffix: str="", timestamp: bool=True):
        self.prefix = prefix
        self.suffix = suffix
        self.timestamp = timestamp
        self.log_host = log_host

        self.ctx = zmq.Context.instance()

        if self.__is_host():
            self.buffer: list[tuple[float, str]] = []
            self.buffer_lock = threading.Lock()

            self.pull_socket = self.ctx.socket(zmq.PULL)
            self.pull_socket.bind(f"tcp://*:{PORT_DEBUG_LOGGING}")

            threading.Thread(target=self.recv_logs_loop, daemon=True).start()
            threading.Thread(target=self.flush_loop, daemon=True).start()
        else:
            self.push_socket = self.ctx.socket(zmq.PUSH)
            self.push_socket.connect(f"tcp://{self.log_host}:{PORT_DEBUG_LOGGING}")

    def print(self, msg: str):
        ts = time.time()
        record = {
            "ts": ts,
            "msg": f"{self.prefix}{msg}{self.suffix}",
        }

        if self.__is_host():
            with self.buffer_lock:
                heappush(self.buffer, (record["ts"], record["msg"]))
        else:
            self.push_socket.send_json(record)

    def recv_logs_loop(self):
        while True:
            record = self.pull_socket.recv_json()
            with self.buffer_lock:
                heappush(self.buffer, (record["ts"], record["msg"]))

    def flush_loop(self):
        while True:
            now = time.time()
            cutoff = now - FLUSH_DELAY

            with self.buffer_lock:
                while self.buffer and self.buffer[0][0] <= cutoff:
                    ts, msg = heappop(self.buffer)
                    ts_fmt = datetime.fromtimestamp(ts).strftime("%H:%M:%S.%f")[:-3]
                    print(f"[{ts_fmt}] {msg}", flush=True)
            time.sleep(0.01)

    def __is_host(self):
        return self.log_host is None

