from pathlib import Path

from pylib.LatencyTest import LatencyTest


def main():
    test = LatencyTest(str(Path(__file__).parent / "cpp" / "SystemCall"))
    test.set_title("System Call")
    test.set_conf(0.99)
    res = test.exec(reps=200000, unit="us")
    res.show()

if __name__ == "__main__":
    main()