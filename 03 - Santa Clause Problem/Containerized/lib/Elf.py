import zmq
import random
import time
from .CanPrint import CanPrint


class Elf(CanPrint):
    def __init__(self):
        ctx = zmq.Context()

        # Registration socket
        self.reg = ctx.socket(zmq.REQ)
        self.reg.connect("tcp://hr:5558")
        self.reg.send_json({"type": "APPLY_ELF"})
        reply = self.reg.recv_json()

        self.elf_id = reply["id"]
        super().__init__(f"[Elf {self.elf_id}] ")

        # Event socket
        self.push = ctx.socket(zmq.PUSH)
        self.push.connect("tcp://hr:5555")

        # Command socket
        self.sub = ctx.socket(zmq.SUB)
        self.sub.connect("tcp://hr:5556")
        self.sub.setsockopt_string(zmq.SUBSCRIBE, "")

    def run(self):
        while True:
            self.log("Building toys")
            time.sleep(random.randint(1, 5))

            if random.random() < 0.2:
                self.log("Needs help")
                self.push.send_json({"type": "ELF_NEEDS_HELP"})

                while True:
                    msg = self.sub.recv_json()
                    if msg["cmd"] == "ELF_HELP_GRANTED":
                        self.log("Got help")
                        break
