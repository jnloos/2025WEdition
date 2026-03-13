import os
import random
import time

from .BenchmarkTest import BenchmarkResult, BenchmarkTest

FILE_SIZE = 64 * 1024 * 1024  # 64 MB
BLOCK_SIZE = 4 * 1024          # 4 KB
ITERATIONS = 500

class RandomReadTest(BenchmarkTest):
    name = "Random Read  (4K)"
    unit = "MB/s"

    def run(self, mountpoint: str, fs: str) -> BenchmarkResult:
        path = os.path.join(mountpoint, "rand_read.bin")
        max_offset = FILE_SIZE - BLOCK_SIZE
        try:
            with open(path, "wb") as f:
                f.write(os.urandom(FILE_SIZE))
                f.flush()
                os.fsync(f.fileno())

            with open("/proc/sys/vm/drop_caches", "w") as f:
                f.write("3")

            start = time.perf_counter()
            with open(path, "rb") as f:
                for _ in range(ITERATIONS):
                    offset = random.randint(0, max_offset)
                    f.seek(offset)
                    f.read(BLOCK_SIZE)
            elapsed = time.perf_counter() - start
        finally:
            if os.path.exists(path):
                os.remove(path)

        mb_read = (ITERATIONS * BLOCK_SIZE) / (1024 * 1024)
        return BenchmarkResult(self.name, fs, mb_read / elapsed, self.unit)