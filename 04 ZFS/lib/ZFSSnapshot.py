import logging
import subprocess
from datetime import datetime

from .ShellCommander import ShellCommander

logger = logging.getLogger(__name__)

_TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S"


class ZFSSnapshot(ShellCommander):
    """A ZFS snapshot identified by its full name (``dataset@tag``)."""

    def __init__(self, full_name: str) -> None:
        self.__full_name = full_name

    @property
    def full_name(self) -> str:
        """Full snapshot name, e.g. ``backuppool/source@2025-03-12T10:00:00``."""
        return self.__full_name

    @property
    def name(self) -> str:
        """The tag portion of the snapshot name (everything after ``@``)."""
        return self.__full_name.split("@", 1)[1]

    @property
    def timestamp(self) -> datetime | None:
        """Parse the tag as an ISO 8601 datetime."""
        try:
            return datetime.strptime(self.name, _TIMESTAMP_FORMAT)
        except ValueError:
            return None

    def create(self) -> None:
        """Create this snapshot (``zfs snapshot``)."""
        logger.info("Creating snapshot '%s' ...", self.__full_name)
        self.run(["zfs", "snapshot", self.__full_name])
        logger.info("Snapshot '%s' created.", self.__full_name)

    def destroy(self) -> None:
        """Destroy this snapshot (``zfs destroy``)."""
        logger.info("Destroying snapshot '%s' ...", self.__full_name)
        self.run(["zfs", "destroy", self.__full_name])
        logger.info("Snapshot '%s' destroyed.", self.__full_name)

    def send(self, destination: str, incremental_from: "ZFSSnapshot | None" = None) -> None:
        """Write the snapshot stream to a file via ``zfs send``."""
        cmd = ["zfs", "send"]
        if incremental_from is not None:
            msg = "Sending incremental snapshot '%s' (base: '%s') to %s"
            logger.info(msg, self.__full_name, incremental_from.full_name, destination)
            cmd += ["-i", incremental_from.full_name]
        else:
            logger.info("Sending full snapshot '%s' to %s", self.__full_name, destination)

        cmd.append(self.__full_name)

        # Run zfs send and redirect its stdout to the destination file.
        logger.debug("Writing stream to '%s'", destination)
        with open(destination, "wb") as out_file:
            result = subprocess.run(cmd, check=True, stdout=out_file, stderr=subprocess.PIPE)
            if result.stderr:
                logger.debug("stderr: %s", result.stderr.decode().rstrip())

        logger.info("Snapshot '%s' sent to '%s'.", self.__full_name, destination)