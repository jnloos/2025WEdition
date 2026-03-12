import logging
import os
import subprocess
import sys
import time
from datetime import datetime

from lib import BackupManager, ZFSDisk, ZFSPool

IMAGE_DIR = "/zfs-images"
BACKUP_CONFIG = os.path.join(os.path.dirname(__file__), "config", "backup.yaml")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def write_demo_file(mountpoint: str, filename: str, content: str) -> None:
    path = os.path.join(mountpoint, filename)
    with open(path, "w") as fh:
        fh.write(content)
    logger.info("Wrote demo file: %s", path)


def main() -> None:
    if os.geteuid() != 0:
        print("Error: This script must be run as root (use sudo).", file=sys.stderr)
        sys.exit(1)

    try:
        disks = [
            ZFSDisk(f"{IMAGE_DIR}/disk1.img"),
            ZFSDisk(f"{IMAGE_DIR}/disk2.img"),
        ]
        pool = ZFSPool("backuppool", disks)

        if not pool.exists():
            pool.create()

        ds = pool.get_dataset("source")
        if not ds.exists():
            ds.create()

        write_demo_file(ds.mountpoint, "data.txt", f"Version 0 — {datetime.now()}")

        manager = BackupManager(BACKUP_CONFIG)

        cycle = 0
        while True:
            cycle += 1
            write_demo_file(ds.mountpoint, "data.txt", f"Version {cycle} — {datetime.now()}")
            manager.run_backups()
            snapshots = ds.list_snapshots()
            logger.info("Snapshots after cycle %d: %s", cycle, [s.name for s in snapshots])
            time.sleep(manager.interval_seconds)

    except KeyboardInterrupt:
        logger.info("Backup loop stopped.")
        sys.exit(0)
    except subprocess.CalledProcessError as exc:
        logger.error("A ZFS command failed: %s", exc)
        logger.error("stderr: %s", exc.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()