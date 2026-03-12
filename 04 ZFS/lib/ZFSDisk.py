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

    def fail(self, pool: str) -> None:
        """Mark this disk as faulted (``zpool offline``)."""
        logger.info("Failing disk %s in pool %s", self.__path, pool)
        self.run(["zpool", "offline", pool, self.__path])

    def replace(self, pool: str, new_disk: "ZFSDisk") -> None:
        """Replace this disk with another one (``zpool replace``)."""
        msg = "Replacing disk %s with %s in pool %s"
        logger.info(msg, self.__path, new_disk.path, pool)
        self.run(["zpool", "replace", pool, self.__path, new_disk.path])