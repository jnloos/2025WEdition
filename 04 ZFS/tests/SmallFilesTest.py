import os
import shutil
import time

from .BenchmarkTest import BenchmarkResult, BenchmarkTest

FILE_COUNT = 500
FILE_SIZE = 4 * 1024  # 4 KB

class SmallFilesTest(BenchmarkTest):
    name = "Small Files"
    unit = "files/s"

    def run(self, mountpoint: str, fs: str) -> BenchmarkResult:
        dirpath = os.path.join(mountpoint, "small_files")
        os.makedirs(dirpath, exist_ok=True)
        data = os.urandom(FILE_SIZE)
        try:
            start = time.perf_counter()
            for i in range(FILE_COUNT):
                path = os.path.join(dirpath, f"file_{i:04d}.bin")
                with open(path, "wb") as f:
                    f.write(data)
                    f.flush()
                    os.fsync(f.fileno())
            elapsed = time.perf_counter() - start
        finally:
            shutil.rmtree(dirpath, ignore_errors=True)

        return BenchmarkResult(self.name, fs, FILE_COUNT / elapsed, self.unit)