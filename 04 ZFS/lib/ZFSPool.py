import logging
import subprocess

from .ZFSDisk import ZFSDisk
from .ShellCommander import ShellCommander  # base class

logger = logging.getLogger(__name__)


class ZFSPool(ShellCommander):
    """A ZFS storage pool backed by one or more ZFSDisk instances."""

    def __init__(self, name: str, disks: list[ZFSDisk], mode: str | None = None, mountpoint: str | None = None) -> None:
        self.__name = name
        self.__disks = disks
        self.__mode = mode
        self.__mountpoint = mountpoint

    @property
    def name(self) -> str:
        """Pool name."""
        return self.__name

    def exists(self) -> bool:
        """Return True if the pool currently exists on the system."""
        try:
            self.run(["zpool", "list", self.__name])
            return True
        except subprocess.CalledProcessError:
            return False

    def status(self) -> str:
        """Return the raw output of ``zpool status``."""
        result = self.run(["zpool", "status", self.__name])
        return result.stdout

    def create(self) -> None:
        """Create the pool with the configured disks and topology via ``zpool create``"""
        cmd = ["zpool", "create"]
        if self.__mountpoint:
            cmd += ["-m", self.__mountpoint]
        cmd.append(self.__name)
        if self.__mode:
            cmd.append(self.__mode)
        cmd.extend(disk.path for disk in self.__disks)
        logger.info("Creating pool '%s' (mode=%s)", self.__name, self.__mode or "stripe")
        self.run(cmd)
        logger.info("Pool '%s' created.", self.__name)

    def destroy(self) -> None:
        """Forcefully destroy the pool (``zpool destroy``)."""
        logger.info("Destroying pool '%s' ...", self.__name)
        self.run(["zpool", "destroy", "-f", self.__name])
        logger.info("Pool '%s' destroyed.", self.__name)

    def get_dataset(self, name: str) -> "ZFSDataset":  # noqa: F821
        """Return an existing ZFSDataset within the pool."""
        # Import here to avoid circular imports at module load time.
        from .ZFSDataset import ZFSDataset

        full_name = f"{self.__name}/{name}"
        logger.debug("Returning dataset handle for '%s'", full_name)
        return ZFSDataset(full_name)
