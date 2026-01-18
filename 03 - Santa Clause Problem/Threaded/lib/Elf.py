from __future__ import annotations

import random
import time
from multiprocessing import Process, Semaphore, Value
from .CanPrint import CanPrint
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .HR import HR

class Elf(Process, CanPrint):
    hr: HR
    elf_id: int

    # Probability of needing help from Santa Clause
    help_prob: float = 0.2

    # Max and min time to produce a toy
    max_prod_time: int = 5
    min_prod_time: int = 1

    def __init__(self, elf_id: int, human_res: HR) -> None:
        self.elf_id = elf_id
        self.hr = human_res

        CanPrint.__init__(self, prefix= f"[Elf {elf_id}] ", color=CanPrint.GREEN)
        Process.__init__(self)

    def build_toys(self) -> None:
        toys = ["wooden train", "teddy bear", "dollhouse", "race car", "action figure", "building blocks", "yo-yo"]
        names = ["James", "Peter", "George", "Ringo", "Daniel", "Paul", "John", "Anna", "Lisa", "Laura"]
        surnames = ["Smith", "McDonald", "Johnson", "Williams", "Jones", "Garcia", "Miller", "Davis", "Rodriguez"]
        self.print(f"Builds a {random.choice(toys)} for {random.choice(names)} {random.choice(surnames)}.")

    def need_help(self) -> None:
        self.print("Needs help from Santa Clause.")

    def get_help(self) -> None:
        self.print("Gets help from Santa Clause.")

    def run(self):
        while not self.hr.shutdown.is_set():
            # Build a toy, normally Santa is not required to help
            self.build_toys()
            time.sleep(random.randint(self.min_prod_time, self.max_prod_time))
            if random.random() >= self.help_prob:
                continue

            # Santa is required to help, wait for him
            self.hr.glob_mutex.acquire()
            self.hr.elves_needing_help.value += 1
            if self.hr.elves_needing_help.value == self.hr.problem_tolerance:
                self.hr.santa_sem.release()
            self.hr.glob_mutex.release()

            # Getting help by Santa
            self.need_help()
            self.hr.help_elves_sem.acquire()
            self.get_help()

            # Going back to work
            self.hr.glob_mutex.acquire()
            self.hr.elves_needing_help.value -= 1
            self.hr.glob_mutex.release()


