import logging
import os
import subprocess

from .ShellCommander import ShellCommander

logger = logging.getLogger(__name__)


class Ext4Mount(ShellCommander):
    """A loop-device-backed ext4 filesystem."""

    def __init__(self, loop_device: str, mountpoint: str) -> None:
        self.__loop_device = loop_device
        self.__mountpoint = mountpoint

    @property
    def loop_device(self) -> str:
        """Path to the loop device, e.g. ``/dev/loop0``."""
        return self.__loop_device

    @property
    def mountpoint(self) -> str:
        """Path where the filesystem is (or will be) mounted."""
        return self.__mountpoint

    def exists(self) -> bool:
        """Return True if the loop device is currently active."""
        try:
            self.run(["losetup", self.__loop_device])
            return True
        except subprocess.CalledProcessError:
            return False

    def mount(self) -> None:
        """Create mountpoint directory if needed, then mount the loop device."""
        os.makedirs(self.__mountpoint, exist_ok=True)
        logger.info("Mounting %s at %s ...", self.__loop_device, self.__mountpoint)
        self.run(["mount", self.__loop_device, self.__mountpoint])
        logger.info("Mounted at %s.", self.__mountpoint)

    def umount(self) -> None:
        """Unmount the filesystem. Best-effort — logs warning on failure, does not raise."""
        try:
            self.run(["umount", self.__mountpoint])
            logger.info("Unmounted %s.", self.__mountpoint)
        except subprocess.CalledProcessError as exc:
            logger.warning("umount %s failed: %s", self.__mountpoint, exc)

    def detach(self) -> None:
        """Detach the loop device. Best-effort — logs warning on failure, does not raise."""
        try:
            self.run(["losetup", "-d", self.__loop_device])
            logger.info("Loop device %s detached.", self.__loop_device)
        except subprocess.CalledProcessError as exc:
            logger.warning("losetup -d %s failed: %s", self.__loop_device, exc)