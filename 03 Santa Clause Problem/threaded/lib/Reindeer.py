from __future__ import annotations

import random
import time

from multiprocessing import Process, Semaphore, Value

from .CanPrint import CanPrint
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .HR import HR

class Reindeer(Process, CanPrint):
    hr: HR
    reindeer_id: int

    def __init__(self, reindeer_id: int, human_res: HR) -> None:
        self.reindeer_id = reindeer_id
        self.hr = human_res

        CanPrint.__init__(self, prefix= f"[Reindeer {reindeer_id}] ", color=CanPrint.BLUE)
        Process.__init__(self)

    def enjoy_holidays(self):
        cocktails = ["Mojito", "Pina Colada", "Caipirinha", "Sex on the Beach", "Tequila Sunrise", "Whiskey Sour"]
        countries = ["Fiji", "Samoa", "Tonga", "Vanuatu", "Kiribati", "Tuvalu", "Nauru"]
        self.print(f"Drinks {random.choice(cocktails)} on {random.choice(countries)}.")

    def leave_holidays(self):
        self.print("Returns from vacation feeling deeply relaxed.")

    def get_hitched(self):
        self.print("Is getting hitched for christmas.")

    def run(self):
        while not self.hr.shutdown.is_set():
            self.hr.holiday_approval_sem.acquire()

            # Enjoy holidays
            self.enjoy_holidays()
            time.sleep(self.hr.time_until_christmas)
            self.leave_holidays()

            # Give the start signal for the preparations
            self.hr.glob_mutex.acquire()
            self.hr.returned_reindeers.value += 1
            if self.hr.returned_reindeers.value == len(self.hr.reindeers):
                self.hr.santa_sem.release()
            self.hr.glob_mutex.release()

            # Getting hitched
            self.hr.hitch_reindeer_sem.acquire()
            self.get_hitched()

            # Give the start signal for Christmas (NOT IN ORIGINAL PROBLEM)
            self.hr.glob_mutex.acquire()
            self.hr.prepared_reindeers.value += 1
            if self.hr.prepared_reindeers.value == len(self.hr.reindeers):
                self.hr.christmas_sem.release()
            self.hr.glob_mutex.release()
