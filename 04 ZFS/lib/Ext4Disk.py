import logging
import os
import subprocess

from .ShellCommander import ShellCommander

logger = logging.getLogger(__name__)


class Ext4Disk(ShellCommander):
    """A virtual ext4 disk backed by an image file."""

    def __init__(self, path: str) -> None:
        self.__path = path

    @property
    def path(self) -> str:
        """Absolute path to the backing image file."""
        return self.__path

    def exists(self) -> bool:
        """Return True if the image file exists."""
        return os.path.isfile(self.__path)

    def format(self) -> None:
        """Format the image as ext4 (``mkfs.ext4 -F <path>``)."""
        logger.info("Formatting %s as ext4 ...", self.__path)
        self.run(["mkfs.ext4", "-F", self.__path])
        logger.info("Formatting complete.")

    def attach(self, mountpoint: str) -> "Ext4Mount":
        """Attach image as loop device via ``losetup --find --show``.

        Returns an Ext4Mount instance. Does NOT mount yet.
        """
        from .Ext4Mount import Ext4Mount

        logger.info("Attaching %s as loop device ...", self.__path)
        result = subprocess.run(
            ["losetup", "--find", "--show", self.__path],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        loop_device = result.stdout.strip()
        logger.info("Attached as %s", loop_device)
        return Ext4Mount(loop_device, mountpoint)