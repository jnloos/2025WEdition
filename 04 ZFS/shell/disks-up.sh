#!/bin/bash
# disks-up.sh - Create virtual disk images
# Creates 4 x 5GB raw image files under /2025WEdition/ to be used as virtual disks.
# The images are filesystem-agnostic and can be used with ZFS, ext4, btrfs, or any other filesystem.

set -e

# --- Root check ---
if [[ $EUID -ne 0 ]]; then
    echo "Error: This script must be run as root (use sudo)." >&2
    exit 1
fi

IMAGE_DIR="/2025WEdition"
IMAGE_COUNT=4
IMAGE_SIZE="5G"

echo "=== Virtual Disk Setup ==="
echo "Image directory : $IMAGE_DIR"
echo "Image count     : $IMAGE_COUNT"
echo "Image size each : $IMAGE_SIZE"
echo

# --- Create image directory ---
echo "[1/2] Creating image directory $IMAGE_DIR ..."
mkdir -p "$IMAGE_DIR"
echo "      Done."
echo

# --- Create image files ---
echo "[2/2] Creating $IMAGE_COUNT image files (this may take a while) ..."
for i in $(seq 1 $IMAGE_COUNT); do
    IMG="$IMAGE_DIR/disk${i}.img"
    echo "      Creating $IMG ..."
    # Use dd to allocate a zero-filled file.
    # bs=1M count=5120 gives exactly 5 GiB.
    dd if=/dev/zero of="$IMG" bs=1M count=5120 status=progress
    echo "      $IMG created."
done
echo

# --- Verify creation ---
echo "=== Verification ==="
echo "Files in $IMAGE_DIR:"
ls -lh "$IMAGE_DIR"
echo
echo "Setup complete. The images in $IMAGE_DIR can now be used as virtual disks."
echo "Examples:"
echo "  ZFS:  zpool create mypool $IMAGE_DIR/disk1.img $IMAGE_DIR/disk2.img"
echo "  ext4: mkfs.ext4 $IMAGE_DIR/disk3.img"