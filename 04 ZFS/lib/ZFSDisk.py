import logging
import os

from .ShellCommander import ShellCommander

logger = logging.getLogger(__name__)


class ZFSDisk(ShellCommander):
    """A virtual disk backed by an image file on the local filesystem."""

    def __init__(self, path: str) -> None:
        self.__path = path

    @property
    def path(self) -> str:
        """Absolute path to the backing image file."""
        return self.__path

    def exists(self) -> bool:
        """Return True if the image file exists on disk."""
        return os.path.isfile(self.__path)

    def offline(self, pool: str) -> None:
        """Take this disk offline administratively (``zpool offline``)."""
        logger.info("Taking disk %s offline in pool %s", self.__path, pool)
        self.run(["zpool", "offline", pool, self.__path])

    def fail(self, pool: str) -> None:
        """Simulate a physical disk failure by truncating the image file to zero bytes."""
        msg = "Simulating physical failure of %s in pool %s (truncating image)"
        logger.info(msg,self.__path, pool)
        with open(self.__path, "wb") as f:
            f.truncate(0)
        logger.info("Disk image %s truncated to zero bytes.", self.__path)

    def replace(self, pool: str, new_disk: "ZFSDisk") -> None:
        """Replace this disk with another one (``zpool replace``)."""
        msg = "Replacing disk %s with %s in pool %s"
        logger.info(msg, self.__path, new_disk.path, pool)
        self.run(["zpool", "replace", pool, self.__path, new_disk.path])