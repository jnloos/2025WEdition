#!/bin/bash
# disks-down.sh - Remove virtual disk images
# Destroys any ZFS pools backed by images in /2025WEdition/, unmounts any ext4 loop devices,
# removes the image files, and removes the /2025WEdition/ directory.
# Intentionally does NOT use set -e so cleanup continues even if individual steps fail.

# --- Root check ---
if [[ $EUID -ne 0 ]]; then
    echo "Error: This script must be run as root (use sudo)." >&2
    exit 1
fi

IMAGE_DIR="/2025WEdition"

echo "=== Virtual Disk Teardown ==="
echo

# --- Destroy ZFS pools that use images from IMAGE_DIR ---
echo "[1/3] Checking for ZFS pools backed by images in $IMAGE_DIR ..."

if ! command -v zpool &>/dev/null; then
    echo "      zpool not found, skipping pool destruction."
else
    # List all pool names, then check each pool's config for paths under IMAGE_DIR.
    POOLS=$(zpool list -H -o name 2>/dev/null || true)

    if [[ -z "$POOLS" ]]; then
        echo "      No ZFS pools found."
    else
        for POOL in $POOLS; do
            # zpool status shows the vdev paths; grep for our image directory.
            if zpool status "$POOL" 2>/dev/null | grep -q "$IMAGE_DIR"; then
                echo "      Destroying pool '$POOL' (uses images from $IMAGE_DIR) ..."
                zpool destroy -f "$POOL" && echo "      Pool '$POOL' destroyed." \
                    || echo "      Warning: Failed to destroy pool '$POOL'."
            else
                echo "      Pool '$POOL' does not use $IMAGE_DIR, skipping."
            fi
        done
    fi
fi
echo

# --- Remove image files ---
echo "[2/3] Removing image files from $IMAGE_DIR ..."
if [[ -d "$IMAGE_DIR" ]]; then
    # Remove all files inside the directory; continue on individual failures.
    for IMG in "$IMAGE_DIR"/*.img; do
        # Guard against the glob matching nothing.
        [[ -e "$IMG" ]] || continue
        echo "      Removing $IMG ..."
        rm -f "$IMG" && echo "      Removed $IMG." \
            || echo "      Warning: Could not remove $IMG."
    done
else
    echo "      $IMAGE_DIR does not exist, nothing to remove."
fi
echo

# --- Remove image directory ---
echo "[3/3] Removing directory $IMAGE_DIR ..."
if [[ -d "$IMAGE_DIR" ]]; then
    rmdir "$IMAGE_DIR" 2>/dev/null \
        && echo "      Directory $IMAGE_DIR removed." \
        || echo "      Warning: Could not remove $IMAGE_DIR (may not be empty)."
else
    echo "      $IMAGE_DIR does not exist, nothing to do."
fi
echo

echo "=== Disk teardown complete ==="