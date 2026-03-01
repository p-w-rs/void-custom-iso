#!/bin/bash
# post-setup.sh - Runs before initramfs generation
# Receives ROOTFS path as $1

ROOTFS="$1"

echo "=== Custom Void Linux Setup ==="
echo "ROOTFS: $ROOTFS"


# ─────────────────────────────────────────
#  greetd on tty1
#
#  greetd is a display manager that handles login and launches mangowc.
#  It takes over tty1 from agetty.
#  The greeter system user must exist before the service starts.
# ─────────────────────────────────────────

echo "=== Configuring greetd on tty1 ==="

# 1. Create the greeter system user (required by greetd)
chroot "$ROOTFS" useradd \
    --system \
    --no-create-home \
    --shell /sbin/nologin \
    greeter 2>/dev/null \
    && echo "  Created greeter user." \
    || echo "  greeter user already exists — skipping."

# 2. Disable agetty on tty1
AGETTY_TTY1="$ROOTFS/var/service/agetty-tty1"
if [ -L "$AGETTY_TTY1" ]; then
    rm "$AGETTY_TTY1"
    echo "  Disabled agetty-tty1."
elif [ -e "$AGETTY_TTY1" ]; then
    echo "  WARNING: $AGETTY_TTY1 exists but is not a symlink — leaving alone."
else
    echo "  agetty-tty1 not active (nothing to remove)."
fi

# 3. Enable greetd on tty1
GREETD_SV="$ROOTFS/etc/sv/greetd"
GREETD_LINK="$ROOTFS/var/service/greetd"
if [ -L "$GREETD_LINK" ]; then
    echo "  greetd already enabled (symlink exists)."
elif [ -d "$GREETD_SV" ]; then
    ln -s /etc/sv/greetd "$GREETD_LINK"
    echo "  Enabled greetd."
else
    echo "  ERROR: $GREETD_SV not found — is greetd installed?"
    exit 1
fi


# ─────────────────────────────────────────
#  kmscon on tty2
#
#  kmscon provides a GPU-accelerated fallback terminal on tty2.
#  Switch to it with Ctrl+Alt+F2 from the graphical session.
#  We disable agetty on tty2 and enable kmscon in its place.
# ─────────────────────────────────────────

echo "=== Configuring kmscon on tty2 ==="

KMSCON_SV="$ROOTFS/etc/sv/kmscon"
KMSCON_RUN="$KMSCON_SV/run"

# 1. Make the run script executable
if [ -f "$KMSCON_RUN" ]; then
    chmod +x "$KMSCON_RUN"
    echo "  Set +x on $KMSCON_RUN."
else
    echo "  ERROR: $KMSCON_RUN not found — did custom-files copy correctly?"
    exit 1
fi

# 2. Disable agetty on tty2
AGETTY_TTY2="$ROOTFS/var/service/agetty-tty2"
if [ -L "$AGETTY_TTY2" ]; then
    rm "$AGETTY_TTY2"
    echo "  Disabled agetty-tty2."
elif [ -e "$AGETTY_TTY2" ]; then
    echo "  WARNING: $AGETTY_TTY2 exists but is not a symlink — leaving alone."
else
    echo "  agetty-tty2 not active (nothing to remove)."
fi

# 3. Enable kmscon on tty2
KMSCON_LINK="$ROOTFS/var/service/kmscon"
if [ -L "$KMSCON_LINK" ]; then
    echo "  kmscon already enabled (symlink exists)."
elif [ -d "$KMSCON_SV" ]; then
    ln -s /etc/sv/kmscon "$KMSCON_LINK"
    echo "  Enabled kmscon."
else
    echo "  ERROR: $KMSCON_SV not found — kmscon service not enabled."
    exit 1
fi


# ─────────────────────────────────────────
#  Fish as the default shell for new users
#
#  /etc/default/useradd is read by useradd when creating new accounts.
#  Changing SHELL= here means any user created on the installed system
#  (by a graphical installer, adduser, useradd, etc.) gets fish by default.
# ─────────────────────────────────────────

echo "=== Setting fish as default shell for new users ==="

USERADD_DEFAULTS="$ROOTFS/etc/default/useradd"
if [ -f "$USERADD_DEFAULTS" ]; then
    sed -i 's|^SHELL=.*|SHELL=/usr/bin/fish|' "$USERADD_DEFAULTS"
    echo "  Updated SHELL in $USERADD_DEFAULTS."
else
    # File may not exist on minimal installs — create the relevant line
    echo "SHELL=/usr/bin/fish" >> "$USERADD_DEFAULTS"
    echo "  Created $USERADD_DEFAULTS with SHELL=/usr/bin/fish."
fi


# ─────────────────────────────────────────
#  update-odin script
#
#  Shipped via custom-files into /opt/update-odin.
#  Ensure it is executable since git may drop the bit.
# ─────────────────────────────────────────

echo "=== Configuring update-odin ==="

UPDATE_ODIN="$ROOTFS/opt/update-odin"

if [ -f "$UPDATE_ODIN" ]; then
    chmod +x "$UPDATE_ODIN"
    echo "  Set +x on $UPDATE_ODIN."
else
    echo "  ERROR: $UPDATE_ODIN not found — did custom-files copy correctly?"
    exit 1
fi


echo "=== Done ==="
