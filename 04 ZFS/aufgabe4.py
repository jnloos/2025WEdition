import logging
import os
import subprocess
import sys

from lib import ZFSDisk, ZFSPool, Ext4Disk, Ext4Mount
from tests.BenchmarkTest import BenchmarkResult, BenchmarkTest
from tests.SequentialWriteTest import SequentialWriteTest
from tests.SequentialReadTest import SequentialReadTest
from tests.RandomWriteTest import RandomWriteTest
from tests.RandomReadTest import RandomReadTest
from tests.SmallFilesTest import SmallFilesTest

IMAGE_DIR = "/2025WEdition/disks"
EXT4_MOUNT = "/2025WEdition/aufgabe4/ext4"
ZFS_MOUNT = "/2025WEdition/aufgabe4/zfs"
EXT4_IMAGE = f"{IMAGE_DIR}/disk2.img"

TESTS: list[BenchmarkTest] = [
    SequentialWriteTest(),
    SequentialReadTest(),
    RandomWriteTest(),
    RandomReadTest(),
    SmallFilesTest(),
]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

def print_results(results: list[BenchmarkResult]) -> None:
    """Collect unique test names in order and build lookup: name -> {fs: result}"""
    seen: dict[str, dict[str, BenchmarkResult]] = {}
    for r in results:
        seen.setdefault(r.name, {})[r.fs] = r

    col_name = 24
    col_val = 13

    sep = "=" * 60
    divider = "-" * 60
    header = f"{'Test':<{col_name}} {'ZFS':>{col_val}} {'ext4':>{col_val}}"

    print()
    print(sep)
    print("  Benchmark Results: ZFS vs ext4")
    print(sep)
    print(header)
    print(divider)
    for name, fs_map in seen.items():
        zfs_r = fs_map.get("zfs")
        ext4_r = fs_map.get("ext4")
        unit = (zfs_r or ext4_r).unit
        zfs_str  = f"{zfs_r.value:.1f} {unit}"  if zfs_r  else "n/a"
        ext4_str = f"{ext4_r.value:.1f} {unit}" if ext4_r else "n/a"
        print(f"{name:<{col_name}} {zfs_str:>{col_val}} {ext4_str:>{col_val}}")
    print(sep)

def main() -> None:
    if os.geteuid() != 0:
        print("Error: This script must be run as root (use sudo).", file=sys.stderr)
        sys.exit(1)

    disk1 = ZFSDisk(f"{IMAGE_DIR}/disk1.img")
    pool = ZFSPool("benchpool", [disk1], mountpoint=ZFS_MOUNT)
    ext4_mount: Ext4Mount | None = None
    results: list[BenchmarkResult] = []

    try:
        # 1. ZFS setup
        if pool.exists():
            pool.destroy()
        pool.create()
        zfs_mountpoint = ZFS_MOUNT
        logger.info("ZFS mountpoint: %s", zfs_mountpoint)

        # 2. ext4 setup
        ext4_disk = Ext4Disk(EXT4_IMAGE)
        ext4_disk.format()
        ext4_mount = ext4_disk.attach(EXT4_MOUNT)
        ext4_mount.mount()

        # 3. Run benchmarks
        for test in TESTS:
            logger.info("Running '%s' on ZFS ...", test.name)
            results.append(test.run(zfs_mountpoint, "zfs"))

            logger.info("Running '%s' on ext4 ...", test.name)
            results.append(test.run(EXT4_MOUNT, "ext4"))

    except subprocess.CalledProcessError as exc:
        logger.error("A command failed: %s", exc)
        logger.error("stderr: %s", exc.stderr)
        sys.exit(1)
    finally:
        if ext4_mount:
            ext4_mount.umount()
            ext4_mount.detach()
        if pool.exists():
            pool.destroy()

    print_results(results)


if __name__ == "__main__":
    main()