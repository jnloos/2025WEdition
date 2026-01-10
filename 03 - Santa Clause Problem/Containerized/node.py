import sys
import time

from lib.HR import HR
from lib.Santa import Santa
from lib.Elf import Elf
from lib.Reindeer import Reindeer


def die(msg: str):
    print(f"[node] {msg}", flush=True)
    sys.exit(1)


def main():
    if len(sys.argv) < 2:
        die("role missing (hr | santa | elf | reindeer)")

    role = sys.argv[1]

    # Small delay so HR can bind sockets first (simple + sufficient)
    if role != "hr":
        time.sleep(1)

    if role == "hr":
        hr = HR()
        hr.run()

    elif role == "santa":
        santa = Santa()
        santa.run()

    elif role == "elf":
        elf = Elf()
        elf.run()

    elif role == "reindeer":
        reindeer = Reindeer()
        reindeer.run()

    else:
        die(f"unknown role: {role}")


if __name__ == "__main__":
    main()
