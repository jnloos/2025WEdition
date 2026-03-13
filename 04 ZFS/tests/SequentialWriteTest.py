import os
import time

from .BenchmarkTest import BenchmarkResult, BenchmarkTest

SIZE_MB = 256
BLOCK_SIZE = 1024 * 1024  # 1 MB

class SequentialWriteTest(BenchmarkTest):
    name = "Sequential Write"
    unit = "MB/s"

    def run(self, mountpoint: str, fs: str) -> BenchmarkResult:
        path = os.path.join(mountpoint, "seq_write.bin")
        block = os.urandom(BLOCK_SIZE)
        try:
            start = time.perf_counter()
            with open(path, "wb") as f:
                for _ in range(SIZE_MB):
                    f.write(block)
                f.flush()
                os.fsync(f.fileno())
            elapsed = time.perf_counter() - start
        finally:
            if os.path.exists(path):
                os.remove(path)

        return BenchmarkResult(self.name, fs, SIZE_MB / elapsed, self.unit)