import logging
import os
import subprocess
import sys
import threading
import time
from datetime import datetime

from lib import ZFSDisk, ZFSPool

IMAGE_DIR = "/2025WEdition/disks"
POOL_NAME = "raidpool"
TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

def worker(filepath: str, stop_event: threading.Event, error_event: threading.Event) -> int:
    """Continuously reads and writes the filepath until stop_event is set."""
    iteration = 0
    while not stop_event.is_set():
        try:
            # 1. Read current content.
            with open(filepath, "r") as f:
                content = f.read()

            # 2. Append a new iteration line.
            timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
            with open(filepath, "a") as f:
                f.write(f"iteration={iteration}  timestamp={timestamp}\n")
                f.flush()

            # 3. Verify the file is readable and non-empty.
            with open(filepath, "r") as f:
                data = f.read()
            if not data:
                raise OSError("workload.txt is unexpectedly empty after write")

            time.sleep(0.05)  # ~20 iterations/s, prevents unbounded file growth
            iteration += 1

            # 4. Log every 5 iterations.
            if iteration % 5 == 0:
                logger.info("Worker: iteration %d OK", iteration)

        except (IOError, OSError) as exc:
            error_event.set()
            logger.error("WORKER ERROR: %s", exc)
            break

    return iteration

def main() -> None:
    if os.geteuid() != 0:
        print("Error: This script must be run as root (use sudo).", file=sys.stderr)
        sys.exit(1)

    disks = [
        ZFSDisk(f"{IMAGE_DIR}/disk1.img"),
        ZFSDisk(f"{IMAGE_DIR}/disk2.img"),
        ZFSDisk(f"{IMAGE_DIR}/disk3.img"),
    ]
    spare_disk = ZFSDisk(f"{IMAGE_DIR}/disk4.img")
    pool = ZFSPool(POOL_NAME, disks, mode="raidz")

    try:
        # 1. Create pool and dataset
        if pool.exists():
            pool.destroy()
        pool.create()

        ds = pool.get_dataset("data")
        ds.create()

        # 2. Write an initial file
        workload_path = os.path.join(ds.mountpoint, "workload.txt")
        with open(workload_path, "w") as f:
            f.write(f"initial  timestamp={datetime.now().strftime(TIMESTAMP_FORMAT)}\n")
        logger.info("Initial workload.txt written to %s", workload_path)

        # 3. Start a worker thread
        stop_event = threading.Event()
        error_event = threading.Event()
        iteration_count = [0]  # mutable container so the thread result is accessible

        def worker_wrapper():
            iteration_count[0] = worker(workload_path, stop_event, error_event)

        worker_thread = threading.Thread(target=worker_wrapper, daemon=True)
        worker_thread.start()

        # 4. Let a worker run for 3 seconds to confirm it's working
        time.sleep(3)
        if error_event.is_set():
            logger.error("Worker reported errors before disk failure — aborting.")
            stop_event.set()
            worker_thread.join()
            sys.exit(1)
        logger.info("Worker running normally after 3 s. Proceeding to disk failure.")

        # 5. Simulate disk failure, let worker continue for 5 more seconds
        logger.info("=" * 60)
        logger.info("  Simulating failure of disk1 ...")
        logger.info("=" * 60)
        disks[0].fail(POOL_NAME)
        logger.info("Pool status after failure:\n%s", pool.status())

        time.sleep(5)

        if error_event.is_set():
            logger.warning("Worker reported I/O errors during the failure window.")
        else:
            logger.info("Worker had NO I/O errors during the 5 s failure window — RAIDZ held.")

        # 6. Replace the failed disk, let worker run for 3 more seconds
        logger.info("=" * 60)
        logger.info("  Replacing disk1 with disk4 ...")
        logger.info("=" * 60)
        disks[0].replace(POOL_NAME, spare_disk)
        logger.info("Pool status after replacement:\n%s", pool.status())

        time.sleep(3)

        # 7. Stop worker
        stop_event.set()
        worker_thread.join()

        # 8. Summary
        final_status = pool.status()
        print()
        print("=" * 60)
        print("  SUMMARY")
        print("=" * 60)
        print(f"  Total iterations completed : {iteration_count[0]}")
        if error_event.is_set():
            print("  I/O errors during failure  : YES — worker encountered errors")
        else:
            print("  I/O errors during failure  : NO  — RAIDZ kept data accessible")
        print(f"  Final pool status:\n{final_status}")
        print("=" * 60)

    except subprocess.CalledProcessError as exc:
        logger.error("A ZFS command failed: %s", exc)
        logger.error("stderr: %s", exc.stderr)
        sys.exit(1)
    finally:
        if pool.exists():
            pool.destroy()


if __name__ == "__main__":
    main()