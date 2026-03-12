import logging
import subprocess

from .ShellCommander import ShellCommander

logger = logging.getLogger(__name__)

# Manages a
class ZFSDataset(ShellCommander):
    """A ZFS dataset (filesystem) identified by its full hierarchical name."""

    def __init__(self, full_name: str) -> None:
        self.__full_name = full_name

    @property
    def full_name(self) -> str:
        """Full dataset name."""
        return self.__full_name

    @property
    def mountpoint(self) -> str:
        """Return the dataset's current mountpoint."""
        try:
            result = self.run(
                ["zfs", "get", "-H", "mountpoint", self.__full_name]
            )
            # Output columns: name  property  value  source
            value = result.stdout.split("\t")[2]
            return value.strip()
        except subprocess.CalledProcessError:
            return ""

    def exists(self) -> bool:
        """Return True if the dataset exists."""
        try:
            self.run(["zfs", "list", self.__full_name])
            return True
        except subprocess.CalledProcessError:
            return False

    def create(self) -> None:
        """Create the dataset (``zfs create``)."""
        logger.info("Creating dataset '%s' ...", self.__full_name)
        self.run(["zfs", "create", self.__full_name])
        logger.info("Dataset '%s' created.", self.__full_name)

    def destroy(self) -> None:
        """Recursively destroy the dataset and all its snapshots (``zfs destroy -r``)."""
        logger.info("Destroying dataset '%s' (recursive) ...", self.__full_name)
        self.run(["zfs", "destroy", "-r", self.__full_name])
        logger.info("Dataset '%s' destroyed.", self.__full_name)

    def snapshot(self, tag: str) -> "ZFSSnapshot":  # noqa: F821
        """Create a snapshot via ``zfs snapshot`` and return its handle."""
        from .ZFSSnapshot import ZFSSnapshot

        snap = ZFSSnapshot(f"{self.__full_name}@{tag}")
        snap.create()
        return snap

    def list_snapshots(self) -> list:  # noqa: F821
        """Return a chronologically sorted list of existing snapshots."""
        from .ZFSSnapshot import ZFSSnapshot

        try:
            result = self.run(["zfs", "list", "-H", "-t", "snapshot", "-o", "name", "-r", self.__full_name])
        except subprocess.CalledProcessError:
            return []

        # Extract snapshot names and timestamps
        snapshots: list[ZFSSnapshot] = []
        for line in result.stdout.splitlines():
            line = line.strip()
            if line.startswith(f"{self.__full_name}@"):
                snapshots.append(ZFSSnapshot(line))

        # Sort by timestamp property, fall back to name for unparseable tags.
        def sort_key(s: ZFSSnapshot):
            ts = s.timestamp
            if ts is not None:
                return 0, ts
            return 1, s.name

        snapshots.sort(key=sort_key)
        return snapshots