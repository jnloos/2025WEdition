import zmq
from .CanPrintZMQ import CanPrintZMQ
from .config import *

class Santa(CanPrintZMQ):
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
        ctx = zmq.Context()

        self.con_hr = ctx.socket(zmq.REP)
        self.con_hr.bind(f"tcp://*:{PORT_SANTA}")

        super().__init__(log_host="hr", prefix="Santa: ", timestamp=True)

    def run(self):
        # Usually all messages are a hit because no other messages are sent on this channel
        while True:
            # GIL sends this thread to sleep until a message is received
            msg = self.con_hr.recv_json()
            cmd = msg["cmd"]

            if cmd == Santa.IN_HELP_ELVES:
                self.print("Wakes up and makes himself a cup of coffee.")
                self.con_hr.send_json({"type": Santa.OUT_OFFICE_OPENED})

            # Christmas is coming soon
            elif cmd == Santa.IN_PREPARE_SLEIGH:
                self.print("Wakes up excitedly and prepares the sleigh.")
                self.con_hr.send_json({"type": Santa.OUT_HITCHES_REINDEERS})

                elves_needing_help = False
                while True:
                    msg = self.con_hr.recv_json()
                    cmd = msg["cmd"]

                    # Santa waits for each reindeer to be prepared (NOT IN ORIGINAL PROBLEM)
                    if cmd == Santa.IN_SHIP_PRESENTS:
                        self.print("Christmas is here!")
                        self.con_hr.send_json({"type": Santa.OUT_BACK_TO_HOLIDAYS})
                        break
                    # Tracks if an elf needs help, but helps later
                    else:
                        elves_needing_help = True
                        self.con_hr.send_json({"type": Santa.OUT_WAIT_FOR_PREPARED_REINDEERS})
                        break

                # Helps the elves after Christmas if necessary
                if elves_needing_help:
                    self.print("Wakes up and makes himself a cup of coffee.")
                    self.con_hr.send_json({"type": Santa.OUT_OFFICE_OPENED})