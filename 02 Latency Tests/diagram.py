# Python
from pylib.LatencyTest import LatencyResult

# Example summary matching class attribute names
summary = {
    "size": 6,
    "min": 9.8,
    "median": 11.1,
    "max": 13.2,
    "mean": 11.2,
    "conf": 0.95,
    "M2": 6.848,  # sum of squared deviations
}

result = LatencyResult.from_summary(summary, title="Sample Latency")
result.show()