from dataclasses import dataclass
import os
import time

@dataclass
class BenchmarkResult:
    name: str
    fs: str      # "zfs" or "ext4"
    value: float  # MB/s or files/s
    unit: str    # "MB/s" or "files/s"

class BenchmarkTest:
    name: str = "unnamed"
    unit: str = "MB/s"

    def run(self, mountpoint: str, fs: str) -> BenchmarkResult:
        raise NotImplementedError

    @staticmethod
    def drop_all_caches() -> None:
        """Clear Linux page cache and ZFS ARC before a read benchmark."""
        # 1. Flush Linux page cache
        with open("/proc/sys/vm/drop_caches", "w") as f:
            f.write("3")

        # 2. Force ZFS ARC to minimum size (512 KB), then restore
        arc_max_path = "/sys/module/zfs/parameters/zfs_arc_max"
        if os.path.exists(arc_max_path):
            with open(arc_max_path, "w") as f:
                f.write("524288")  # 512 KB — forces ARC eviction
            time.sleep(1)  # give ARC time to shrink
            with open(arc_max_path, "w") as f:
                f.write("0")  # restore to default (no limit)