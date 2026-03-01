#!/bin/bash
# post-setup.sh — Runs before initramfs generation
# $1 = ROOTFS path (passed by mklive)
# VOID_ISO_MODE = "desktop" | "server" (set by wrapper)

ROOTFS="$1"
MODE="${VOID_ISO_MODE:-desktop}"

echo "=== Custom Void Linux Setup (${MODE}) ==="
echo "ROOTFS: $ROOTFS"


# ─────────────────────────────────────────
#  Desktop only: greetd on tty1
#  Server: agetty is left completely alone
# ─────────────────────────────────────────

if [ "$MODE" = "desktop" ]; then
    echo ""
    echo "=== [desktop] Configuring greetd on tty1 ==="

    chroot "$ROOTFS" useradd \
        --system --no-create-home --shell /sbin/nologin \
        greeter 2>/dev/null \
        && echo "  Created greeter user." \
        || echo "  greeter user already exists."

    AGETTY_TTY1="$ROOTFS/var/service/agetty-tty1"
    if [ -L "$AGETTY_TTY1" ]; then
        rm "$AGETTY_TTY1"
        echo "  Disabled agetty-tty1."
    fi

    GREETD_SV="$ROOTFS/etc/sv/greetd"
    GREETD_LINK="$ROOTFS/var/service/greetd"
    if [ -d "$GREETD_SV" ] && [ ! -L "$GREETD_LINK" ]; then
        ln -s /etc/sv/greetd "$GREETD_LINK"
        echo "  Enabled greetd on tty1."
    elif [ ! -d "$GREETD_SV" ]; then
        echo "  ERROR: $GREETD_SV not found — is greetd installed?"
        exit 1
    fi

else
    echo ""
    echo "=== [server] TTY left as default agetty ==="
    echo "  No TTY changes — standard Void agetty on tty1."
fi


# ─────────────────────────────────────────
#  Server: remove desktop-only config files
# ─────────────────────────────────────────

if [ "$MODE" = "server" ]; then
    echo ""
    echo "=== [server] Removing desktop config files ==="
    rm -rf "$ROOTFS/etc/greetd"
    echo "  Removed /etc/greetd/."
fi


# ─────────────────────────────────────────
#  Fish as default shell for new users
# ─────────────────────────────────────────

echo ""
echo "=== Setting fish as default shell ==="

USERADD_DEFAULTS="$ROOTFS/etc/default/useradd"
if [ -f "$USERADD_DEFAULTS" ]; then
    sed -i 's|^SHELL=.*|SHELL=/usr/bin/fish|' "$USERADD_DEFAULTS"
    echo "  Updated SHELL in $USERADD_DEFAULTS."
else
    echo "SHELL=/usr/bin/fish" >> "$USERADD_DEFAULTS"
    echo "  Created $USERADD_DEFAULTS."
fi


# ─────────────────────────────────────────
#  update-odin
# ─────────────────────────────────────────

echo ""
echo "=== Configuring update-odin ==="

UPDATE_ODIN="$ROOTFS/opt/update-odin"
if [ -f "$UPDATE_ODIN" ]; then
    chmod +x "$UPDATE_ODIN"
    echo "  Set +x on $UPDATE_ODIN."
else
    echo "  WARNING: $UPDATE_ODIN not found — skipping."
fi


echo ""
echo "=== Done (${MODE}) ==="
