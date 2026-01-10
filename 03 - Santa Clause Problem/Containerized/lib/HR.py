import zmq
from .CanPrint import CanPrint

class HR(CanPrint):
    def __init__(self, elf_threshold: int = 3, reindeer_count: int = 9):
        super().__init__("[HR] ")

        self.elf_threshold = elf_threshold
        self.reindeer_count = reindeer_count

        # State
        self.elves_waiting = 0
        self.reindeer_returned = 0
        self.reindeer_prepared = 0

        self.next_elf_id = 1
        self.next_reindeer_id = 1

        ctx = zmq.Context()

        # Workers → HR (events)
        self.pull = ctx.socket(zmq.PULL)
        self.pull.bind("tcp://*:5555")

        # HR → Workers (commands)
        self.pub = ctx.socket(zmq.PUB)
        self.pub.bind("tcp://*:5556")

        # Santa ↔ HR (coordination)
        self.rep = ctx.socket(zmq.REP)
        self.rep.bind("tcp://*:5557")

        # Registration (apply for ID)
        self.reg = ctx.socket(zmq.REP)
        self.reg.bind("tcp://*:5558")

    def run(self):
        self.log("HR online")

        poller = zmq.Poller()
        poller.register(self.pull, zmq.POLLIN)
        poller.register(self.rep, zmq.POLLIN)
        poller.register(self.reg, zmq.POLLIN)

        while True:
            events = dict(poller.poll())

            if self.pull in events:
                msg = self.pull.recv_json()
                self.handle_worker_event(msg)

            if self.rep in events:
                msg = self.rep.recv_json()
                self.handle_santa_request(msg)

            if self.reg in events:
                msg = self.reg.recv_json()
                self.handle_registration(msg)

    # ---------- handlers ----------

    def handle_registration(self, msg: dict):
        t = msg.get("type")

        if t == "APPLY_ELF":
            eid = self.next_elf_id
            self.next_elf_id += 1
            self.log(f"Registered Elf {eid}")
            self.reg.send_json({"id": eid})

        elif t == "APPLY_REINDEER":
            rid = self.next_reindeer_id
            self.next_reindeer_id += 1
            self.log(f"Registered Reindeer {rid}")
            self.reg.send_json({"id": rid})

        else:
            self.reg.send_json({"error": "unknown registration type"})

    def handle_worker_event(self, msg: dict):
        t = msg.get("type")

        if t == "ELF_NEEDS_HELP":
            self.elves_waiting += 1
            self.log(f"Elf needs help ({self.elves_waiting})")

            if self.elves_waiting == self.elf_threshold:
                self.pub.send_json({"cmd": "WAKE_SANTA_ELVES"})

        elif t == "REINDEER_RETURNED":
            self.reindeer_returned += 1
            self.log(f"Reindeer returned ({self.reindeer_returned})")

            if self.reindeer_returned == self.reindeer_count:
                self.pub.send_json({"cmd": "WAKE_SANTA_REINDEER"})

        elif t == "REINDEER_PREPARED":
            self.reindeer_prepared += 1

            if self.reindeer_prepared == self.reindeer_count:
                self.pub.send_json({"cmd": "CHRISTMAS"})
                # reset cycle
                self.reindeer_prepared = 0
                self.reindeer_returned = 0

    def handle_santa_request(self, msg: dict):
        t = msg.get("type")

        if t == "HELP_ELVES":
            self.log("Santa helps elves")

            for _ in range(self.elves_waiting):
                self.pub.send_json({"cmd": "ELF_HELP_GRANTED"})

            self.elves_waiting = 0
            self.rep.send_json({"ok": True})

        elif t == "PREPARE_SLEIGH":
            self.log("Santa prepares sleigh")

            for _ in range(self.reindeer_count):
                self.pub.send_json({"cmd": "HITCH"})

            self.rep.send_json({"ok": True})

        else:
            self.rep.send_json({"error": "unknown santa request"})
