import logging
import os
from datetime import datetime

import yaml

from .ZFSDataset import ZFSDataset
from .ShellCommander import ShellCommander

logger = logging.getLogger(__name__)

TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S"
REQUIRED_FIELDS = ["source_dataset", "destination_path", "max_backups", "interval_seconds"]

class BackupManager(ShellCommander):
    """Manages snapshot-based ZFS backups with retention enforcement for multiple jobs."""

    def __init__(self, config_path: str) -> None:
        self.__jobs = self.__load_config(config_path)

    @property
    def interval_seconds(self) -> int:
        """Interval from the first job's config."""
        return int(self.__jobs[0]["interval_seconds"])

    @staticmethod
    def __load_config(path: str) -> list[dict]:
        """Load and validate the YAML config file."""
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Config file not found: {path}")

        with open(path, "r") as fh:
            config = yaml.safe_load(fh)

        jobs = config.get("backups")
        if not isinstance(jobs, list) or not jobs:
            raise ValueError("Config must contain a non-empty 'backups' list.")

        for i, job in enumerate(jobs):
            for field in REQUIRED_FIELDS:
                if field not in job:
                    raise KeyError(f"Job #{i}: missing required field '{field}'")

        logger.debug("Config loaded from '%s': %d job(s)", path, len(jobs))
        return jobs

    def run_backups(self) -> None:
        """Run all backup jobs defined in the config."""
        for job in self.__jobs:
            self.__run_job(job)

    def __run_job(self, job: dict) -> None:
        """Execute a single backup job: snapshot -> send -> retention."""
        dataset = ZFSDataset(job["source_dataset"])
        destination_path: str = job["destination_path"]
        max_backups: int = int(job["max_backups"])

        if not dataset.exists():
            raise RuntimeError(f"Source dataset '{dataset.full_name}' does not exist.")

        tag = datetime.now().strftime(TIMESTAMP_FORMAT)
        logger.info("Starting backup for '%s' — tag: %s", dataset.full_name, tag)

        existing = dataset.list_snapshots()
        prev_snapshot = existing[-1] if existing else None

        new_snapshot = dataset.snapshot(tag)

        os.makedirs(destination_path, exist_ok=True)
        dest_file = os.path.join(destination_path, f"{tag}.zfs")
        new_snapshot.send(dest_file, incremental_from=prev_snapshot)
        logger.info("Backup written to '%s'.", dest_file)

        self.__apply_retention(dataset, destination_path, max_backups)

    @staticmethod
    def __apply_retention(dataset: ZFSDataset, destination_path: str, max_backups: int) -> None:
        """Delete the oldest snapshots until at most max_backups remain."""
        snapshots = dataset.list_snapshots()
        excess = len(snapshots) - max_backups

        if excess <= 0:
            logger.debug("Retention OK: %d/%d snapshots.", len(snapshots), max_backups)
            return

        logger.info("Retention: removing %d old snapshot(s) (limit=%d).", excess, max_backups)
        for snap in snapshots[:excess]:
            snap.destroy()
            backup_file = os.path.join(destination_path, f"{snap.name}.zfs")
            if os.path.isfile(backup_file):
                logger.info("Removing backup file '%s' ...", backup_file)
                os.remove(backup_file)