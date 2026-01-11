import random

import zmq
import time
from .CanPrintZMQ import CanPrintZMQ
from .config import *

class Reindeer(CanPrintZMQ):
    reindeer_id: int

    # Outgoing concerns
    OUT_APPLICATION = "REINDEER_APPLICATION"
    OUT_RETURNED = "REINDEER_RETURNED"
    OUT_IS_PREPARED = "REINDEER_PREPARED"

    # Incoming instructions
    IN_HITCH = "REINDEER_HITCH"
    IN_HOLIDAY_APPROVED = "REINDEER_HOLIDAY_APPROVED"

    # ZMQ sockets
    con_application: zmq.Socket
    worker_concerns: zmq.Socket
    reindeer_bcast: zmq.Socket

    def __init__(self):
        ctx = zmq.Context()

        # Apply to the HR department
        self.con_application = ctx.socket(zmq.REQ)
        self.con_application.connect(f"tcp://hr:{PORT_APPLICATION}")
        self.con_application.send_json({"type": Reindeer.OUT_APPLICATION})
        reply = self.con_application.recv_json()
        self.reindeer_id = reply["id"]

        # Socket for employee concerns
        self.worker_concerns = ctx.socket(zmq.PUSH)
        self.worker_concerns.connect(f"tcp://hr:{PORT_WORKER_EVENTS}")

        # Broadcast socket from the HR department
        self.reindeer_bcast = ctx.socket(zmq.SUB)
        self.reindeer_bcast.connect(f"tcp://hr:{PORT_BCAST_REINDEERS}")
        self.reindeer_bcast.setsockopt_string(zmq.SUBSCRIBE, "")

        super().__init__(log_host="hr", prefix=f"Reindeer {self.reindeer_id}: ", timestamp=True)

    def run(self):
        while True:
            # Holiday phase
            cocktails = ["Mojito", "Pina Colada", "Caipirinha", "Sex on the Beach", "Tequila Sunrise", "Whiskey Sour"]
            countries = ["Fiji", "Samoa", "Tonga", "Vanuatu", "Kiribati", "Tuvalu", "Nauru"]
            self.print(f"Drinks {random.choice(cocktails)} on {random.choice(countries)}.")
            time.sleep(TIME_UNTIL_CHRISTMAS)

            # Return from holiday
            self.print("Returned from holiday.")
            self.worker_concerns.send_json({"type": Reindeer.OUT_RETURNED, "id": self.reindeer_id})

            # Usually all messages are a hit because no other messages are sent on this broadcast channel
            while True:
                # GIL sends this thread to sleep until a message is received
                msg = self.reindeer_bcast.recv_json()
                cmd = msg["cmd"]

                if cmd == Reindeer.IN_HITCH:
                    self.print("Getting hitched to the sleigh.")
                    self.worker_concerns.send_json({"type": Reindeer.OUT_IS_PREPARED, "id": self.reindeer_id})
                    break

                elif cmd == Reindeer.IN_HOLIDAY_APPROVED:
                    self.print("Collects his wages and seeks out his dream holiday.")
                    break
