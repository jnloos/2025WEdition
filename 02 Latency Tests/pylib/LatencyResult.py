from typing import Dict, Any, Optional
import matplotlib.pyplot as plt
from pathlib import Path
import json


class LatencyResult:
    def __init__(self, title: str, summary: Dict[str, Any]):
        required = ("size", "min", "max", "mean", "median", "std_dev", "conf", "conf_low", "conf_high")
        missing = [k for k in required if k not in summary]
        if missing:
            raise ValueError(f"Missing required summary keys: {missing}")

        self.title = title
        self.size = int(summary["size"])
        self.min = float(summary["min"])
        self.max = float(summary["max"])
        self.mean = float(summary["mean"])
        self.median = float(summary["median"])
        self.std_dev = float(summary["std_dev"])
        self.conf = float(summary["conf"])
        self.conf_low = float(summary["conf_low"])
        self.conf_high = float(summary["conf_high"])
        self.unit = summary["unit"]

    # Load class from a JSON file
    @staticmethod
    def from_file(path: str | Path) -> "LatencyResult":
        with Path(path).open("r", encoding="utf-8") as f:
            data = json.load(f)
        return LatencyResult(data["title"], data)

    # Store class to JSON file
    def save(self, path: str | Path) -> None:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("w", encoding="utf-8") as f:
            json.dump(self.dict(), f, indent=2)

    def dict(self) -> dict:
        return {
            "title": self.title,
            "size": self.size,
            "min": self.min,
            "max": self.max,
            "mean": self.mean,
            "median": self.median,
            "std_dev": self.std_dev,
            "conf": self.conf,
            "conf_low": self.conf_low,
            "conf_high": self.conf_high,
            "unit": self.unit
        }

    # Display data in a plot
    def show(self, title: Optional[str] = None) -> None:
        fig, ax = plt.subplots(figsize=(6, 4))
        y = 1

        # Confidence interval (mean ± CI)
        ax.errorbar(
            [self.mean], [y],
            xerr=[[self.mean - self.conf_low], [self.conf_high - self.mean]],
            fmt="o", color="tab:red", ecolor="tab:red",
            elinewidth=2, capsize=6,
            label=f"Mean ± {int(self.conf * 100)}% CI (n={self.size})",
        )

        # Min, Max, Median markers
        ax.plot([self.min, self.max], [y, y],
                color="tab:gray", linewidth=3, alpha=0.5, label="Min–Max")
        ax.scatter([self.min, self.max], [y, y], color="tab:gray", s=30)
        ax.scatter([self.median], [y], color="tab:blue", s=40, zorder=3, label="Median")

        ax.set_yticks([])
        ax.set_xlabel(f"Latency in {self.unit}")
        ax.set_title(title or self.title)
        ax.grid(True, axis="x", linestyle="--", alpha=0.4)
        ax.legend(loc="best")
        fig.tight_layout()
        plt.show()
