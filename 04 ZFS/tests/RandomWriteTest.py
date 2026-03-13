import os
import random
import time

from .BenchmarkTest import BenchmarkResult, BenchmarkTest

FILE_SIZE = 64 * 1024 * 1024  # 64 MB
BLOCK_SIZE = 4 * 1024          # 4 KB
ITERATIONS = 500

class RandomWriteTest(BenchmarkTest):
    name = "Random Write (4K)"
    unit = "MB/s"

    def run(self, mountpoint: str, fs: str) -> BenchmarkResult:
        path = os.path.join(mountpoint, "rand_write.bin")
        block = os.urandom(BLOCK_SIZE)
        max_offset = FILE_SIZE - BLOCK_SIZE
        try:
            with open(path, "wb") as f:
                f.write(b"\0" * FILE_SIZE)
                f.flush()
                os.fsync(f.fileno())

            start = time.perf_counter()
            with open(path, "r+b") as f:
                for _ in range(ITERATIONS):
                    offset = random.randint(0, max_offset)
                    f.seek(offset)
                    f.write(block)
                    f.flush()
                    os.fsync(f.fileno())
            elapsed = time.perf_counter() - start
        finally:
            if os.path.exists(path):
                os.remove(path)

        mb_written = (ITERATIONS * BLOCK_SIZE) / (1024 * 1024)
        return BenchmarkResult(self.name, fs, mb_written / elapsed, self.unit)