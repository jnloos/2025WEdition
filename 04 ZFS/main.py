import logging
import os
import subprocess
import sys
import time

from lib import BackupManager, ZFSDisk, ZFSPool

IMAGE_DIR = "/zfs-images"
BACKUP_CONFIG = os.path.join(os.path.dirname(__file__), "config", "backup.yaml")

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

def separator(title: str) -> None:
    logger.info("=" * 60)
    logger.info("  %s", title)
    logger.info("=" * 60)

# Write a text file into a ZFs dataset's mountpoint
def write_demo_file(mountpoint: str, filename: str, content: str) -> None:
    path = os.path.join(mountpoint, filename)
    with open(path, "w") as fh:
        fh.write(content)
    logger.info("Wrote demo file: %s", path)


# ---------------------------------------------------------------------------
# Demo 1 — Basic stripe pool
# ---------------------------------------------------------------------------


def demo_basic_pool() -> None:
    separator("Demo 1: Basic stripe pool")

    disks = [
        ZFSDisk(f"{IMAGE_DIR}/disk1.img"),
        ZFSDisk(f"{IMAGE_DIR}/disk2.img"),
    ]

    pool = ZFSPool("stripepool", disks)

    if pool.exists():
        logger.info("Pool already exists — destroying first.")
        pool.destroy()

    pool.create()
    logger.info("Pool status:\n%s", pool.status())

    # Create a dataset and write a file.
    ds = pool.get_dataset("data")
    ds.create()
    write_demo_file(ds.mountpoint, "hello.txt", "Hello from ZFS stripe pool!\n")

    # Take a snapshot and list it.
    snap = ds.snapshot("initial")
    logger.info("Snapshots: %s", [s.full_name for s in ds.list_snapshots()])

    snap.destroy()
    pool.destroy()
    logger.info("Demo 1 complete.")


# ---------------------------------------------------------------------------
# Demo 2 — RAID-Z failure and replace
# ---------------------------------------------------------------------------


def demo_raidz() -> None:
    separator("Demo 2: RAIDZ disk failure and replacement")

    disks = [
        ZFSDisk(f"{IMAGE_DIR}/disk1.img"),
        ZFSDisk(f"{IMAGE_DIR}/disk2.img"),
        ZFSDisk(f"{IMAGE_DIR}/disk3.img"),
    ]
    spare = ZFSDisk(f"{IMAGE_DIR}/disk4.img")

    pool = ZFSPool("raidpool", disks, mode="raidz")

    if pool.exists():
        pool.destroy()

    pool.create()
    logger.info("Pool created. Status:\n%s", pool.status())

    # Simulate disk failure.
    logger.info("Simulating failure of disk1 ...")
    disks[0].fail("raidpool")
    logger.info("Post-failure status:\n%s", pool.status())

    # Replace the faulted disk with the spare.
    logger.info("Replacing disk1 with disk4 ...")
    disks[0].replace("raidpool", spare)
    logger.info("Post-replace status:\n%s", pool.status())

    pool.destroy()
    logger.info("Demo 2 complete.")


# ---------------------------------------------------------------------------
# Demo 3 — Backup with retention
# ---------------------------------------------------------------------------


def demo_backup() -> None:
    separator("Demo 3: Snapshot backup with retention")

    disks = [
        ZFSDisk(f"{IMAGE_DIR}/disk1.img"),
        ZFSDisk(f"{IMAGE_DIR}/disk2.img"),
    ]
    pool = ZFSPool("backuppool", disks)

    if pool.exists():
        pool.destroy()

    pool.create()
    ds = pool.get_dataset("source")
    ds.create()

    # Write a small file so there is real data in the dataset.
    write_demo_file(ds.mountpoint, "data.txt", "Important data v1\n")

    manager = BackupManager(BACKUP_CONFIG)

    while True:
        manager.run_backups()
        time.sleep(manager.interval_seconds)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    if os.geteuid() != 0:
        print("Error: This script must be run as root (use sudo).", file=sys.stderr)
        sys.exit(1)

    try:
        demo_basic_pool()
        demo_raidz()
        demo_backup()
    except subprocess.CalledProcessError as exc:
        logger.error("A ZFS command failed: %s", exc)
        logger.error("stderr: %s", exc.stderr)
        sys.exit(1)

    separator("All demos completed successfully")


if __name__ == "__main__":
    main()