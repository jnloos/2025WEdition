import logging
import subprocess

logger = logging.getLogger(__name__)


class ShellCommander:
    """Executes shell commands via subprocess and logs their output."""

    @staticmethod
    def run(cmd: list[str]) -> subprocess.CompletedProcess:
        """Run *cmd* and return the results."""
        logger.info("Running: %s", " ".join(cmd))
        result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.stdout:
            logger.debug("stdout: %s", result.stdout.rstrip())
        if result.stderr:
            logger.debug("stderr: %s", result.stderr.rstrip())
        return result