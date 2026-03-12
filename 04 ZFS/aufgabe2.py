"""
aufgabe2.py — Demonstrates file inconsistency despite ZFS snapshots.

Why can this happen despite ZFS Copy-on-Write?
-----------------------------------------------
ZFS snapshots are crash-consistent: they atomically capture the state of all
ZFS blocks at a single point in time — no block is ever half-written.
However, crash-consistency is NOT the same as application consistency.

Our writer performs a deliberate two-phase write per record:
    Phase 1: write "count=<N>"        → flush to OS
    sleep 0.01 s                       ← snapshot may be taken HERE
    Phase 2: write "  checksum=<N>\n" → flush to OS

If the snapshot is taken in the sleep window, ZFS faithfully preserves that
exact on-disk state — a file with a truncated last line. CoW only guarantees
that each ZFS block is either fully old or fully new; it has no knowledge of
application-level record boundaries.

This is why databases use write-ahead logs, fsync, and write barriers even on
ZFS: the filesystem cannot infer what constitutes a "complete" record.
"""

import hashlib
import logging
import os
import subprocess
import sys
import threading
import time

from lib import ZFSDisk, ZFSPool

IMAGE_DIR = "/zfs-images"
DEST_DIR = "/tmp/zfs-inconsist-demo"
POOL_NAME = "inconsistpool"
RECV_POOL_NAME = "recvpool"
WRITER_DURATION = 10  # seconds the writer thread runs
SNAPSHOT_DELAY = 2    # seconds before taking the inconsistent snapshot

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Writer thread
# ---------------------------------------------------------------------------

def write_counts(filepath: str, stop_event: threading.Event) -> None:
    """Continuously appends records to *filepath* in a non-atomic two-phase way.

    Each record is written in two separate flushes with a 10 ms sleep between
    them, creating a window where the file contains only a partial record.
    """
    n = 0
    deadline = time.time() + WRITER_DURATION
    while not stop_event.is_set() and time.time() < deadline:
        checksum = hashlib.sha256(str(n).encode()).hexdigest()
        # Phase 1 — write only the counter; the record is incomplete here.
        with open(filepath, "a") as f:
            f.write(f"count={n}")
            f.flush()
        # The snapshot window: file is on disk but the line has no checksum yet.
        time.sleep(0.01)
        # Phase 2 — complete the record.
        with open(filepath, "a") as f:
            f.write(f"  checksum={checksum}\n")
            f.flush()
        n += 1
    stop_event.set()
    logger.info("Writer thread finished after %d records.", n)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def zfs_receive(stream_file: str, target_dataset: str) -> None:
    """Pipe *stream_file* into ``zfs receive <target_dataset>``."""
    logger.info("Receiving '%s' into dataset '%s' ...", stream_file, target_dataset)
    with open(stream_file, "rb") as f:
        subprocess.run(["zfs", "receive", "-F", target_dataset], stdin=f, check=True)
    logger.info("Receive complete.")


def last_line(filepath: str) -> str:
    """Return the last non-empty line of *filepath*."""
    with open(filepath, "r") as f:
        lines = [ln for ln in f.readlines() if ln.strip()]
    return lines[-1] if lines else ""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    if os.geteuid() != 0:
        print("Error: This script must be run as root (use sudo).", file=sys.stderr)
        sys.exit(1)

    os.makedirs(DEST_DIR, exist_ok=True)

    snap_inconsist_file = os.path.join(DEST_DIR, "snapshot.zfs")

    disk1 = ZFSDisk(f"{IMAGE_DIR}/disk1.img")
    disk2 = ZFSDisk(f"{IMAGE_DIR}/disk2.img")

    pool = ZFSPool(POOL_NAME, [disk1])
    recv_pool = ZFSPool(RECV_POOL_NAME, [disk2])

    try:
        # ----------------------------------------------------------------
        # 1. Setup pools and dataset
        # ----------------------------------------------------------------
        if pool.exists():
            pool.destroy()
        pool.create()

        if recv_pool.exists():
            recv_pool.destroy()
        recv_pool.create()

        ds = pool.get_dataset("data")
        ds.create()

        counter_file = os.path.join(ds.mountpoint, "counter.txt")

        # ----------------------------------------------------------------
        # 2. Start the non-atomic writer thread
        # ----------------------------------------------------------------
        stop_event = threading.Event()
        writer = threading.Thread(
            target=write_counts,
            args=(counter_file, stop_event),
            daemon=True,
        )
        writer.start()
        logger.info("Writer thread started. Running for %d seconds.", WRITER_DURATION)

        # ----------------------------------------------------------------
        # 3. Take inconsistent snapshot mid-write
        # ----------------------------------------------------------------
        time.sleep(SNAPSHOT_DELAY)
        logger.info("Taking snapshot while writer is active ...")
        snap_inconsist = ds.snapshot("snap-inconsist")
        snap_inconsist.send(snap_inconsist_file)

        # ----------------------------------------------------------------
        # 4. Wait for writer to finish
        # ----------------------------------------------------------------
        writer.join()

        # ----------------------------------------------------------------
        # 5. Receive inconsistent snapshot and inspect counter.txt
        # ----------------------------------------------------------------
        recv_dataset = f"{RECV_POOL_NAME}/inspect"
        zfs_receive(snap_inconsist_file, recv_dataset)

        recv_mountpoint = f"/{RECV_POOL_NAME}/inspect"
        recv_counter = os.path.join(recv_mountpoint, "counter.txt")
        inconsist_last = last_line(recv_counter)
        logger.info("Last line from inconsistent snapshot: %r", inconsist_last)

        has_count = "count=" in inconsist_last
        has_checksum = "checksum=" in inconsist_last
        is_consistent = has_count and has_checksum

        # ----------------------------------------------------------------
        # 6. Read clean state directly from the original dataset mountpoint
        # ----------------------------------------------------------------
        clean_last = last_line(os.path.join(ds.mountpoint, "counter.txt"))
        logger.info("Last line from clean dataset:         %r", clean_last)

        # ----------------------------------------------------------------
        # 7. Summary
        # ----------------------------------------------------------------
        print()
        print("=" * 60)
        if is_consistent:
            print("CONSISTENT: snapshot was clean")
            print(f"  Last line: {inconsist_last!r}")
        else:
            print("INCONSISTENT: last line was cut mid-write")
            print(f"  Inconsistent last line: {inconsist_last!r}")
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


if __name__ == "__main__":
    main()