from multiprocessing import *
from .Reindeer import Reindeer
from .Santa import Santa
from .Elf import Elf
from .CanPrint import CanPrint

import signal

# Human Resources office of the North Pole
# Manages all employees and the reindeers

class HR(CanPrint):
    # Shutdown flag
    shutdown = Event()

    # Global semaphore
    glob_mutex = Semaphore(1)

    # Elf department
    elves: list[Elf]
    help_elves_sem = Semaphore(0)

    # Reindeer department
    reindeers: list[Reindeer]
    hitch_reindeer_sem = Semaphore(0)
    holiday_approval_sem = Semaphore(0)
    
    # Santa Clause
    santa: Santa
    santa_sem = Semaphore(0)
    christmas_sem = Semaphore(0)

    # Time until Christmas in seconds
    time_until_christmas: int = 20

    # Tolerance until wake up Santa
    problem_tolerance: int = 3

    # Elves waiting for Santa
    elves_needing_help = Value('i', 0)

    # Returned and prepared reindeers
    returned_reindeers = Value('i', 0)
    prepared_reindeers = Value('i', 0)

    def __init__(self, num_elves: int = 24, num_reindeers: int = 9)  -> None:
        CanPrint.__init__(self, prefix="[HR] ")
        self.holiday_approval_sem = Semaphore(num_reindeers)
        self.santa = Santa(human_res=self)

        # Initialize employees
        self.elves = [Elf(i+1, human_res=self) for i in range(num_elves)]
        self.reindeers = [Reindeer(i+1, human_res=self) for i in range(num_reindeers)]
        self.print(f"{len(self.elves)} elves and {len(self.reindeers)} reindeers have been hired.")

    def __start_threads(self) -> None:
        self.santa.start()
        for reindeer in self.reindeers:
            reindeer.start()
        for elf in self.elves:
            elf.start()

    def __terminate_threads(self) -> None:
        self.shutdown.set()

        self.santa.join()
        for elf in self.elves:
            elf.join()
        for reindeer in self.reindeers:
            reindeer.join()

    def reset(self) -> None:
        self.prepared_reindeers = 0
        self.returned_reindeers = 0

    def simulate(self) -> None:
        self.print("The employees at the North Pole begin to make and ship the gifts.")
        self.__start_threads()

        # Block the main thread until keyboard interruption
        try:
            signal.pause()
        except KeyboardInterrupt:
            self.print("The North Pole is bankrupt. All work will be suspended. ")

        self.__terminate_threads()
        self.print("All employees were dismissed without pay. ")
