from dataclasses import dataclass

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