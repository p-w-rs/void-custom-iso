#!/bin/bash
# post-setup.sh - Runs before initramfs generation
# Receives ROOTFS path as $1

ROOTFS="$1"

echo "=== Custom Void Linux Setup ==="
echo "ROOTFS: $ROOTFS"
printf "\n\n\n\nI RAN!!!!!!\n\n\n\n"

# ─────────────────────────────────────────
#  kmscon on tty1
#
#  kmscon can't be enabled via -S like a normal runit service because it
#  replaces agetty on a specific TTY rather than running alongside it.
#  We disable the default agetty-tty1 service and enable kmscon instead.
# ─────────────────────────────────────────

echo "=== Configuring kmscon on tty1 ==="

# Disable the default agetty service for tty1
if [ -L "$ROOTFS/var/service/agetty-tty1" ]; then
    rm "$ROOTFS/var/service/agetty-tty1"
    echo "  Disabled agetty-tty1"
fi

# Enable kmscon (the package installs its runit service at /etc/sv/kmscon)
if [ -d "$ROOTFS/etc/sv/kmscon" ]; then
    ln -sf /etc/sv/kmscon "$ROOTFS/var/service/kmscon"
    echo "  Enabled kmscon"
else
    echo "  WARNING: /etc/sv/kmscon not found — kmscon service not enabled"
fi
