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
#  kmscon replaces agetty on a specific TTY rather than running alongside
#  it, so it can't be enabled via -S like a normal runit service.
#  We:
#    1. Ensure the run script is executable (git may not preserve the bit)
#    2. Disable the default agetty-tty1 service
#    3. Enable kmscon in its place
# ─────────────────────────────────────────

echo "=== Configuring kmscon on tty1 ==="

KMSCON_SV="$ROOTFS/etc/sv/kmscon"
KMSCON_RUN="$KMSCON_SV/run"

# 1. Make the run script executable
if [ -f "$KMSCON_RUN" ]; then
    chmod +x "$KMSCON_RUN"
    echo "  Set +x on $KMSCON_RUN"
else
    echo "  ERROR: $KMSCON_RUN not found — did custom-files copy correctly?"
    exit 1
fi

# 2. Disable agetty on tty1
AGETTY_LINK="$ROOTFS/var/service/agetty-tty1"
if [ -L "$AGETTY_LINK" ]; then
    rm "$AGETTY_LINK"
    echo "  Disabled agetty-tty1"
elif [ -e "$AGETTY_LINK" ]; then
    echo "  WARNING: $AGETTY_LINK exists but is not a symlink — leaving alone"
else
    echo "  agetty-tty1 not active (nothing to remove)"
fi

# 3. Enable kmscon
KMSCON_LINK="$ROOTFS/var/service/kmscon"
if [ -L "$KMSCON_LINK" ]; then
    echo "  kmscon already enabled (symlink exists)"
elif [ -d "$KMSCON_SV" ]; then
    ln -s /etc/sv/kmscon "$KMSCON_LINK"
    echo "  Enabled kmscon"
else
    echo "  ERROR: $KMSCON_SV not found — kmscon service not enabled"
    exit 1
fi


# ─────────────────────────────────────────
#  update-odin script
#
#  The script is shipped via custom-files into /usr/local/bin/update-odin.
#  We just ensure it is executable here since git may drop the bit.
#  The user runs "sudo update-odin" after first boot to build Odin + OLS
#  from source on their actual hardware.
# ─────────────────────────────────────────

echo "=== Configuring update-odin ==="

UPDATE_ODIN="$ROOTFS/usr/local/bin/update-odin"

if [ -f "$UPDATE_ODIN" ]; then
    chmod +x "$UPDATE_ODIN"
    echo "  Set +x on $UPDATE_ODIN"
else
    echo "  ERROR: $UPDATE_ODIN not found — did custom-files copy correctly?"
    exit 1
fi


echo "=== Done ==="
