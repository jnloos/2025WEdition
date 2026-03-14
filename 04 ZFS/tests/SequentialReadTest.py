import os
import time

from .BenchmarkTest import BenchmarkResult, BenchmarkTest

SIZE_MB = 256
BLOCK_SIZE = 1024 * 1024  # 1 MB

class SequentialReadTest(BenchmarkTest):
    name = "Sequential Read"
    unit = "MB/s"

    def run(self, mountpoint: str, fs: str) -> BenchmarkResult:
        path = os.path.join(mountpoint, "seq_read.bin")
        block = os.urandom(BLOCK_SIZE)
        try:
            with open(path, "wb") as f:
                for _ in range(SIZE_MB):
                    f.write(block)
                f.flush()
                os.fsync(f.fileno())

            BenchmarkTest.drop_all_caches()

            start = time.perf_counter()
            with open(path, "rb") as f:
                while f.read(BLOCK_SIZE):
                    pass
            elapsed = time.perf_counter() - start
        finally:
            if os.path.exists(path):
                os.remove(path)

        return BenchmarkResult(self.name, fs, SIZE_MB / elapsed, self.unit)