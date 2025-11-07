from .Importer import Importer
from .LatencyResult import LatencyResult
from typing import Dict, Any, List
import math
import numpy as np
from scipy import stats

class LatencyTest:
    conf: float = 0.95
    title: str = "Latency Test"
    unit: str = "ns"

    def __init__(self, cpp_file: str) -> None:
        self.cpp_file = cpp_file

    def set_title(self, title: str) -> None:
        self.title = title

    def set_conf(self, conf: float) -> None:
        if conf <= 0.0 or conf >= 1.0:
            raise ValueError("Invalid confidence level.")
        self.conf = conf

    def set_unit(self, unit: str) -> None:
        if unit not in ["ns", "us", "ms", "s"]:
            raise ValueError("Invalid unit.")
        self.unit = unit

    def exec(self, reps: int) -> LatencyResult:
        imp = Importer()
        cpp = imp.cpp(self.cpp_file)
        probes = cpp.run(reps)
        if not probes:
            raise ValueError("No probe data.")

        values = self.__convert(probes)
        summary = self.__eval(values)
        return LatencyResult(self.title, summary)

    # Convert probes to desired unit
    def __convert(self, probes: List[Any]) -> np.ndarray:
        match self.unit:
            case "ns":
                return np.array([p.elapsed_nanoseconds() for p in probes], dtype=float)
            case "us":
                return np.array([p.elapsed_microseconds() for p in probes], dtype=float)
            case "ms":
                return np.array([p.elapsed_milliseconds() for p in probes], dtype=float)
            case _:
                return np.array([p.elapsed_seconds() for p in probes], dtype=float)

    # Evaluate dataset
    def __eval(self, values: np.ndarray) -> Dict[str, Any]:
        size = len(values)
        mean = float(np.mean(values))
        median = float(np.median(values))
        std_dev = float(np.std(values, ddof=1)) if size > 1 else 0.0
        vmin, vmax = float(np.min(values)), float(np.max(values))
        conf_low, conf_high = self.__conf_bounds(mean, std_dev, size)

        return {
            "size": size,
            "min": vmin,
            "max": vmax,
            "mean": mean,
            "median": median,
            "std_dev": std_dev,
            "conf": self.conf,
            "conf_low": conf_low,
            "conf_high": conf_high,
            "unit": self.unit
        }

    # Calculate confidence interval
    def __conf_bounds(self, mean: float, std_dev: float, size: int) -> tuple[float, float]:
        if size <= 1 or std_dev <= 0.0:
            return mean, mean
        alpha = 1.0 - self.conf
        t_val = float(stats.t.ppf(1 - alpha / 2.0, df=size - 1))
        se = std_dev / math.sqrt(size)
        return mean - t_val * se, mean + t_val * se
