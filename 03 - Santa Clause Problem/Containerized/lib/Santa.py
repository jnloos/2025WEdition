import zmq
from .CanPrint import CanPrint
from .config import *

class Santa(CanPrint):
    # Incoming instructions
    IN_PREPARE_SLEIGH = "SANTA_PREPARE_SLEIGH"
    IN_HELP_ELVES = "SANTA_HELP_ELVES"
    IN_SHIP_PRESENTS = "SANTA_SHIP_PRESENTS"
    
    # Outgoing concerns
    OUT_OFFICE_OPENED = "SANTA_OFFICE_HOURS"
    OUT_HITCHES_REINDEERS = "SANTA_HITCHES_REINDEER"
    OUT_BACK_TO_HOLIDAYS = "SANTA_CHRISTMAS_EVE"
    OUT_WAIT_FOR_PREPARED_REINDEERS = "SANTA_WAIT_FOR_PREPARED_REINDEERS"

    # ZMQ socket
    con_hr: zmq.Socket

    def __init__(self):
        super().__init__(timestamp=True)
        ctx = zmq.Context()

        self.con_hr = ctx.socket(zmq.REP)
        self.con_hr.bind(f"tcp://*:{PORT_SANTA}")

    def run(self):
        # Usually all messages are a hit because no other messages are sent on this channel
        while True:
            # GIL sends this thread to sleep until a message is received
            msg = self.con_hr.recv_json()
            cmd = msg["cmd"]

            if cmd == Santa.IN_HELP_ELVES:
                self.print("Wakes up and makes himself a cup of coffee.")
                self.con_hr.send_json({"type": Santa.OUT_OFFICE_OPENED})

            elif cmd == Santa.IN_PREPARE_SLEIGH:
                self.print("Wakes up excitedly and prepares the sleigh.")
                self.con_hr.send_json({"type": Santa.OUT_HITCHES_REINDEERS})

                elves_needing_help = False
                while True:
                    if cmd == Santa.IN_SHIP_PRESENTS:
                        self.print("Christmas is here!")
                        self.con_hr.send_json({"type": Santa.OUT_BACK_TO_HOLIDAYS})
                        break
                    elif cmd == Santa.IN_HELP_ELVES:
                        elves_needing_help = True
                        self.con_hr.send_json({"type": Santa.OUT_WAIT_FOR_PREPARED_REINDEERS})
                        break

                if elves_needing_help:
                    self.print("Wakes up and makes himself a cup of coffee.")
                    self.con_hr.send_json({"type": Santa.OUT_OFFICE_OPENED})