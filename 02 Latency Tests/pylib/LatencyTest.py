from .Importer import Importer
from typing import Dict, Any, Optional
import math
from scipy import stats
import matplotlib.pyplot as plt
from pathlib import Path
import json


class LatencyResult:
    title: str

    # Basic statistics
    size: int
    min: float
    max: float
    mean: float
    median: float

    # Standard deviation
    std_dev: float
    M2: float

    # Confidence interval
    conf: float
    conf_low: float
    conf_high: float

    def __init__(self, title: str, summary: Dict[str, Any]):
        required = ("size", "min", "max", "mean", "median", "conf", "std_dev")
        missing = [k for k in required if k not in summary]
        if missing:
            raise ValueError(f"Missing required summary keys: {missing}")

        self.title = title
        self.size = int(summary["size"])
        if self.size <= 0:
            raise ValueError("Sample size must be positive.")

        # Directly load from summary
        self.min = float(summary["min"])
        self.max = float(summary["max"])
        self.mean = float(summary["mean"])
        self.median = float(summary["median"])
        self.std_dev = float(summary["std_dev"])

        # Confidence level
        self.conf = float(summary["conf"])
        if not 0.0 < self.conf < 1.0:
            raise ValueError("Invalid confidence level.")

        # Calculate confidence interval
        if self.size > 1 and self.std_dev > 0.0:
            alpha = 1.0 - self.conf
            t = float(stats.t.ppf(1 - alpha / 2.0, df=self.size - 1))
            se = self.std_dev / math.sqrt(self.size)
            self.conf_low = self.mean - t * se
            self.conf_high = self.mean + t * se
        else:
            self.conf_low = self.conf_high = self.mean

    # Loads a LatencyResult from a JSON file
    @staticmethod
    def from_file(path: str | Path) -> "LatencyResult":
        with Path(path).open("r", encoding="utf-8") as f:
            data = json.load(f)
        return LatencyResult(data["title"], data)

    # Shows the results in a plot
    def show(self, title: Optional[str] = None) -> None:
        fig, ax = plt.subplots(figsize=(6, 4))
        y = 1

        # Distribution line
        ax.errorbar(
            [self.mean], [y],
            xerr=[[self.mean - self.conf_low], [self.conf_high - self.mean]],
            fmt="o", color="tab:red", ecolor="tab:red", elinewidth=2, capsize=6,
            label=f"Mean ± {int(self.conf * 100)}% CI (size={self.size})",
        )

        # Min/max and median markers
        ax.plot([self.min, self.max], [y, y], color="tab:gray", linewidth=3, alpha=0.5, label="Min–Max")
        ax.scatter([self.min, self.max], [y, y], color="tab:gray", s=30)
        ax.scatter([self.median], [y], color="tab:blue", s=40, zorder=3, label="Median")

        ax.set_yticks([])
        ax.set_xlabel("Latency")
        ax.set_title(title or self.title)
        ax.grid(True, axis="x", linestyle="--", alpha=0.4)
        ax.legend(loc="best")
        fig.tight_layout()
        plt.show()

    def save(self, path: str | Path) -> None:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)

        data: Dict[str, Any] = {
            "title": self.title,
            "size": self.size,
            "min": self.min,
            "max": self.max,
            "mean": self.mean,
            "median": self.median,
            "std_dev": self.std_dev,
            "conf": self.conf,
        }

        with target.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)


class LatencyTest:
    conf: float = 0.95
    title: str = "Latency Test"

    def __init__(self, cpp_file: str) -> None:
        self.cpp_file = cpp_file

    def set_title (self, title: str) -> None:
        self.title = title

    def set_conf(self, conf: float) -> None:
        self.conf = conf

    def exec(self, reps: int, unit: str = "ns") -> LatencyResult:
        imp = Importer()
        cpp = imp.cpp(self.cpp_file)

        # Get raw summary from C++
        raw: Dict[str, Any] = cpp.run(reps, unit)

        # Normalize keys and ensure required fields exist
        summary: Dict[str, Any] = {
            "size": int(raw.get("size") or raw.get("n")),
            "min": float(raw["min"]),
            "max": float(raw["max"]),
            "mean": float(raw["mean"]),
            "median": float(raw["median"]),
            "std_dev": float(raw["std_dev"]),
            "conf": float(raw.get("conf", 0.95)),
        }

        return LatencyResult(self.title, summary=summary)
