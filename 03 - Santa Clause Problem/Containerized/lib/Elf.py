import zmq
import random
import time
from .CanPrintZMQ import CanPrintZMQ
from .config import *

class Elf(CanPrintZMQ):
    elf_id: int

    # Outgoing concerns
    APPLICATION = "ELF_APPLICATION"
    NEEDS_HELP = "ELF_NEEDS_HELP"

    # Incoming instructions
    HELP_GRANTED = "ELF_HELP_GRANTED"

    # ZMQ sockets
    con_application: zmq.Socket
    push_hr: zmq.Socket
    sub_hr: zmq.Socket

    def __init__(self):
        ctx = zmq.Context()

        # Apply to the HR department
        self.con_application = ctx.socket(zmq.REQ)
        self.con_application.connect(f"tcp://hr:{PORT_APPLICATION}")
        self.con_application.send_json({"type": Elf.APPLICATION})
        reply = self.con_application.recv_json()
        self.elf_id = reply["id"]

        # Socket for employee concerns
        self.push_hr = ctx.socket(zmq.PUSH)
        self.push_hr.connect(f"tcp://hr:{PORT_WORKER_EVENTS}")

        # Broadcast socket from the HR department
        self.sub_hr = ctx.socket(zmq.SUB)
        self.sub_hr.connect(f"tcp://hr:{PORT_BCAST_ELVES}")
        self.sub_hr.setsockopt_string(zmq.SUBSCRIBE, "")

        super().__init__(log_host="hr", prefix=f"Elf {self.elf_id}: ", timestamp=True)

    def run(self):
        while True:
            # Working phase
            toys = ["wooden train", "teddy bear", "dollhouse", "race car", "action figure", "building blocks", "yo-yo"]
            names = ["James", "Peter", "George", "Ringo", "Daniel", "Paul", "John", "Anna", "Lisa", "Laura"]
            surnames = ["Smith", "McDonald", "Johnson", "Williams", "Jones", "Garcia", "Miller", "Davis", "Rodriguez"]
            self.print(f"Builds a {random.choice(toys)} for {random.choice(names)} {random.choice(surnames)}.")
            time.sleep(random.randint(MIN_PROD_TIME, MAX_PROD_TIME))

            # Occasionally needs help
            if random.random() < NEED_HELP_PROB:
                self.print("Needs help.")
                self.push_hr.send_json({"type": Elf.NEEDS_HELP, "id": self.elf_id})

                # Usually the first message is a hit because no other messages are sent on this broadcast channel
                while True:
                    # GIL sends this thread to sleep until a message is received
                    msg = self.sub_hr.recv_json()
                    cmd = msg["cmd"]

                    if cmd == Elf.HELP_GRANTED:
                        self.print("Gets help from Santa Clause.")
                        break
