import zmq
from .CanPrint import CanPrint

class Santa(CanPrint):
    def __init__(self):
        super().__init__("[Santa] ")
        ctx = zmq.Context()

        self.sub = ctx.socket(zmq.SUB)
        self.sub.connect("tcp://hr:5556")
        self.sub.setsockopt_string(zmq.SUBSCRIBE, "")

        self.req = ctx.socket(zmq.REQ)
        self.req.connect("tcp://hr:5557")

    def run(self):
        self.log("Santa sleeping")
        while True:
            msg = self.sub.recv_json()

            if msg["cmd"] == "WAKE_SANTA_ELVES":
                self.log("Helping elves")
                self.req.send_json({"type": "HELP_ELVES"})
                self.req.recv_json()

            elif msg["cmd"] == "WAKE_SANTA_REINDEER":
                self.log("Preparing sleigh")
                self.req.send_json({"type": "PREPARE_SLEIGH"})
                self.req.recv_json()

            elif msg["cmd"] == "CHRISTMAS":
                self.log("Christmas is here!")
