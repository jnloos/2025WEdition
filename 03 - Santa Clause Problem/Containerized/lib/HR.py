import zmq
from .CanPrintZMQ import CanPrintZMQ
from .Elf import Elf
from .Santa import Santa
from .Reindeer import Reindeer
from .config import *

# Human Resources office of the North Pole
# Manages all employees and the reindeers
# Also manages ICP communication logics

class HR(CanPrintZMQ):
    # Allowed number of employees
    elf_count: int
    reindeer_count: int

    # Counters for sync logics
    elves_needing_help: int = 0
    returned_reindeers: int = 0
    prepared_reindeers: int = 0
    next_elf_id: int = 1
    next_reindeer_id: int = 1

    # ZMQ Sockets
    worker_concerns: zmq.Socket
    bcast_elves: zmq.Socket
    bcast_reindeers: zmq.Socket
    con_santa: zmq.Socket
    con_application: zmq.Socket

    def __init__(self, elf_count=3, reindeer_count=9):
        self.elf_count = elf_count
        self.reindeer_count = reindeer_count

        ctx = zmq.Context()

        # Incoming connection sockets
        self.worker_concerns = ctx.socket(zmq.PULL)
        self.worker_concerns.bind(f"tcp://*:{PORT_WORKER_EVENTS}")

        # Broadcast sockets
        self.bcast_elves = ctx.socket(zmq.PUB)
        self.bcast_elves.bind(f"tcp://*:{PORT_BCAST_ELVES}")
        self.bcast_reindeers = ctx.socket(zmq.PUB)
        self.bcast_reindeers.bind(f"tcp://*:{PORT_BCAST_REINDEERS}")

        # Two-way connection sockets
        self.con_santa = ctx.socket(zmq.REQ)
        self.con_santa.connect(f"tcp://santa:{PORT_SANTA}")
        self.con_application = ctx.socket(zmq.REP)
        self.con_application.bind(f"tcp://*:{PORT_APPLICATION}")

        super().__init__(prefix="HR: ", timestamp=True)

    def run(self):
        self.print("The factories have been built. It's time to hire employees.")

        poller = zmq.Poller()
        poller.register(self.worker_concerns, zmq.POLLIN)
        poller.register(self.con_santa, zmq.POLLIN)
        poller.register(self.con_application, zmq.POLLIN)

        # All incoming connections are handled in a single thread
        while True:
            # Block the main thread until a message is received
            events = dict(poller.poll())

            if self.con_application in events:
                self.handle_application()

            if self.worker_concerns in events:
                self.handle_workers()

            if self.con_santa in events:
                self.handle_santa()

    # Handles application requests
    def handle_application(self):
        msg = self.con_application.recv_json()
        application_type = msg["type"]

        if application_type == Elf.APPLICATION:
            reindeer_id = self.next_elf_id
            self.next_elf_id += 1
            self.print(f"Elf {reindeer_id} is hired.")
            self.con_application.send_json({"id": reindeer_id})

        elif application_type == Reindeer.OUT_APPLICATION:
            elf_id = self.next_reindeer_id
            self.next_reindeer_id += 1
            self.print(f"Reindeer {elf_id} is hired.")
            self.con_application.send_json({"id": elf_id})

    # Manages the concerns of the workers and gives orders to Santa
    def handle_workers(self):
        msg = self.worker_concerns.recv_json()
        concern = msg["type"]
        employee_id = msg["id"]

        # Prioritize Christmas preparations if all reindeers have returned
        if concern == Reindeer.OUT_RETURNED:
            self.returned_reindeers += 1
            self.print(f"Reindeer {employee_id} has reported back for duty.")
            if self.returned_reindeers == self.reindeer_count:
                self.con_santa.send_json({"cmd": Santa.IN_PREPARE_SLEIGH})

        elif concern == Reindeer.OUT_IS_PREPARED:
            self.prepared_reindeers += 1
            if self.prepared_reindeers == self.reindeer_count:
                self.print("All departments are ready for Christmas.")
                self.con_santa.send_json({"cmd": Santa.IN_SHIP_PRESENTS})

        elif concern == Elf.NEEDS_HELP:
            self.elves_needing_help += 1
            self.print(f"Assistance request has been received by {employee_id}.")
            if self.elves_needing_help == PROBLEM_TOLERANCE:
                self.con_santa.send_json({"cmd": Santa.IN_HELP_ELVES})

    # Manages the concerns of Santa and gives orders to the workers
    def handle_santa(self):
        msg = self.con_santa.recv_json()
        concern = msg["type"]

        if concern == Santa.OUT_OFFICE_OPENED:
            self.print("Santa holds office hours for the elves.")
            self.bcast_elves.send_json({"cmd": Elf.HELP_GRANTED})
            self.elves_needing_help = 0

        elif concern == Santa.OUT_HITCHES_REINDEERS:
            self.print("Christmas is coming soon. Arrange overtime work.")
            self.bcast_reindeers.send_json({"cmd": Reindeer.IN_HITCH})

        elif concern == Santa.OUT_BACK_TO_HOLIDAYS:
            self.print("Christmas is done. Send non-essential staff on holiday.")
            self.returned_reindeers = 0
            self.prepared_reindeers = 0
            self.bcast_reindeers.send_json({"cmd": Reindeer.IN_HOLIDAY_APPROVED})

        elif concern == Santa.OUT_WAIT_FOR_PREPARED_REINDEERS:
            self.print("Help request must wait because Santa waits for his reindeers.")
