from __future__ import annotations
from multiprocessing import Process, Semaphore, Value
from .CanPrint import CanPrint
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .HR import HR

class Santa(Process, CanPrint):
    hr: HR

    def __init__(self, human_res: HR) -> None:
        self.hr = human_res

        CanPrint.__init__(self, prefix= "[Santa] ", color=CanPrint.RED)
        Process.__init__(self)

    def christmas(self) -> None:
        self.print("Christmas is here!")

    def prepare_sleigh(self) -> None:
        self.print(f"Prepares his sleigh.")

    def help_elves(self) -> None:
        self.print("Helps the elves.")

    def run(self):
        while not self.hr.shutdown.is_set():
            self.hr.santa_sem.acquire()
            self.hr.glob_mutex.acquire()

            # Prioritize Christmas preparations if all reindeers have returned
            if self.hr.returned_reindeers.value == len(self.hr.reindeers):
                # Prepare sleigh and hitch reindeers
                self.prepare_sleigh()
                for _ in range(len(self.hr.reindeers)):
                    self.hr.hitch_reindeer_sem.release()
                self.hr.glob_mutex.release()

                # Wait until all reindeers are ready for the Christmas Eve (NOT IN ORIGINAL PROBLEM)
                self.hr.christmas_sem.acquire()
                self.christmas()

                # Send all reindeers back to holidays
                self.hr.glob_mutex.acquire()
                for _ in range(len(self.hr.reindeers)):
                    self.hr.holiday_approval_sem.release()
                self.hr.prepared_reindeers.value = 0
                self.hr.returned_reindeers.value = 0

            # Help elves if they are waiting for Santa
            elif self.hr.elves_needing_help.value >= 3:
                self.help_elves()
                for _ in range(self.hr.elves_needing_help.value):
                    self.hr.help_elves_sem.release()

            self.hr.glob_mutex.release()
