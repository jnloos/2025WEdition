import hashlib
import logging
import os
import shutil
import subprocess
import sys
import threading
import time

from lib import ZFSDisk, ZFSPool

IMAGE_DIR = "/2025WEdition/disks"
DEST_DIR = "/2025WEdition/aufgabe2"
POOL_NAME = "inconsistpool"
RECV_POOL_NAME = "recvpool"
WRITER_DURATION = 10 # seconds the writer thread runs
SNAPSHOT_DELAY = 2 # seconds before taking the inconsistent snapshot

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

def write_counts(filepath: str, stop_event: threading.Event) -> None:
    """Continuously appends records to filepath in a non-atomic two-phase way."""
    n = 0
    deadline = time.time() + WRITER_DURATION
    while not stop_event.is_set() and time.time() < deadline:
        checksum = hashlib.sha256(str(n).encode()).hexdigest()
        # 1. Write only the counter; the record is incomplete here.
        with open(filepath, "a") as f:
            f.write(f"count={n}")
            f.flush()
        # 2. Snapshot window: The file is on the disk, but the line has no checksum yet.
        time.sleep(0.01)
        # 3. Complete the record with a checksum.
        with open(filepath, "a") as f:
            f.write(f"  checksum={checksum}\n")
            f.flush()
        n += 1
    stop_event.set()
    logger.info("Writer thread finished after %d records.", n)

def last_line(filepath: str) -> str:
    """Return the last non-empty line of *filepath*."""
    with open(filepath, "r") as f:
        lines = [ln for ln in f.readlines() if ln.strip()]
    return lines[-1] if lines else ""

def main() -> None:
    if os.geteuid() != 0:
        print("Error: This script must be run as root (use sudo).", file=sys.stderr)
        sys.exit(1)

    # Inconsistent snapshot file
    os.makedirs(DEST_DIR, exist_ok=True)
    snap_inconsistent_file = os.path.join(DEST_DIR, "snapshot.zfs")

    # Create the ZFS pools
    disk1 = ZFSDisk(f"{IMAGE_DIR}/disk1.img")
    disk2 = ZFSDisk(f"{IMAGE_DIR}/disk2.img")
    pool = ZFSPool(POOL_NAME, [disk1])
    recv_pool = ZFSPool(RECV_POOL_NAME, [disk2])

    try:
        # 1. Setup pools and dataset
        if pool.exists():
            pool.destroy()
        pool.create()

        if recv_pool.exists():
            recv_pool.destroy()
        recv_pool.create()

        ds = pool.get_dataset("data")
        ds.create()

        counter_file = os.path.join(ds.mountpoint, "counter.txt")

        # 2. Start the non-atomic writer thread
        stop_event = threading.Event()
        writer = threading.Thread(target=write_counts, args=(counter_file, stop_event), daemon=True)
        writer.start()
        logger.info("Writer thread started. Running for %d seconds.", WRITER_DURATION)

        # 3. Take inconsistent snapshot mid-write
        time.sleep(SNAPSHOT_DELAY)
        logger.info("Taking snapshot while writer is active ...")
        snap_inconsistent = ds.snapshot("snap-inconsist")
        snap_inconsistent.send(snap_inconsistent_file)

        # 4. Wait for writer to finish
        writer.join()

        # 5. Receive inconsistent snapshot and inspect counter.txt
        snap_inconsistent.pipe(recv_pool.get_dataset("inspect"))

        recv_mountpoint = f"/{RECV_POOL_NAME}/inspect"
        recv_counter = os.path.join(recv_mountpoint, "counter.txt")
        inconsistent_last = last_line(recv_counter)
        logger.info("Last line from inconsistent snapshot: %r", inconsistent_last)

        has_count = "count=" in inconsistent_last
        has_checksum = "checksum=" in inconsistent_last
        is_consistent = has_count and has_checksum

        # 6. Read clean state directly from the original dataset mountpoint
        clean_last = last_line(os.path.join(ds.mountpoint, "counter.txt"))
        logger.info("Last line from clean dataset:         %r", clean_last)

        # 7. Print Summary
        print()
        print("=" * 60)
        if is_consistent:
            print("CONSISTENT: snapshot was clean")
            print(f"  Last line: {inconsistent_last!r}")
        else:
            print("INCONSISTENT: last line was cut mid-write")
            print(f"  Inconsistent last line: {inconsistent_last!r}")
            print(f"  Clean last line:        {clean_last!r}")
        print("=" * 60)

    except subprocess.CalledProcessError as exc:
        logger.error("A ZFS command failed: %s", exc)
        logger.error("stderr: %s", exc.stderr)
        sys.exit(1)
    finally:
        if pool.exists():
            pool.destroy()
        if recv_pool.exists():
            recv_pool.destroy()
        shutil.rmtree(DEST_DIR, ignore_errors=True)


if __name__ == "__main__":
    main()