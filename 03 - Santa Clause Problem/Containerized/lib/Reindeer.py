import zmq
import time
from .CanPrint import CanPrint


class Reindeer(CanPrint):
    def __init__(self):
        ctx = zmq.Context()

        # Registration socket
        self.reg = ctx.socket(zmq.REQ)
        self.reg.connect("tcp://hr:5558")
        self.reg.send_json({"type": "APPLY_REINDEER"})
        reply = self.reg.recv_json()

        self.rid = reply["id"]
        super().__init__(f"[Reindeer {self.rid}] ")

        # Event socket
        self.push = ctx.socket(zmq.PUSH)
        self.push.connect("tcp://hr:5555")

        # Command socket
        self.sub = ctx.socket(zmq.SUB)
        self.sub.connect("tcp://hr:5556")
        self.sub.setsockopt_string(zmq.SUBSCRIBE, "")

    def run(self):
        while True:
            self.log("On holiday")
            time.sleep(10)

            self.log("Returned")
            self.push.send_json({"type": "REINDEER_RETURNED"})

            while True:
                msg = self.sub.recv_json()
                if msg["cmd"] == "HITCH":
                    self.log("Getting hitched")
                    self.push.send_json({"type": "REINDEER_PREPARED"})
                    break
