"""
lib/__init__.py — Public API for the ZFS backup and RAID demonstration tool.

Exports all classes so callers can simply do:
    from lib import ZFSHelper, ZFSPool, ZFSDataset, ZFSSnapshot, ZFSDisk, BackupManager
"""

from .ShellCommander import ShellCommander
from .ZFSDisk import ZFSDisk
from .ZFSPool import ZFSPool
from .ZFSDataset import ZFSDataset
from .ZFSSnapshot import ZFSSnapshot
from .BackupManager import BackupManager
from .Ext4Disk import Ext4Disk
from .Ext4Mount import Ext4Mount

__all__ = [
    "ShellCommander",
    "ZFSDisk",
    "ZFSPool",
    "ZFSDataset",
    "ZFSSnapshot",
    "BackupManager",
    "Ext4Disk",
    "Ext4Mount",
]