#!/usr/bin/env python3
"""
post-setup.py <rootfs_path>

Runs inside the mklive chroot after packages are installed.
Configures 66 as the active init and tears down runit supervision.
"""

import subprocess
import sys
from pathlib import Path

if len(sys.argv) != 2:
    print("Usage: post-setup.py <rootfs_path>")
    sys.exit(1)

rootfs = Path(sys.argv[1])
print(f"Configuring system in: {rootfs}")


def chroot(cmd: list[str]) -> int:
    """Run a command inside the rootfs chroot."""
    result = subprocess.run(["chroot", str(rootfs), *cmd])
    return result.returncode


# ─────────────────────────────────────────
#  1. Disable runit supervision
#     (runit-void stays installed so the live env stays consistent,
#      but we don't want it running services at boot)
# ─────────────────────────────────────────

runsvdir = rootfs / "var" / "service"
if runsvdir.exists():
    for svc_link in runsvdir.iterdir():
        if svc_link.is_symlink():
            svc_link.unlink()
            print(f"  unlinked runit service: {svc_link.name}")

# ─────────────────────────────────────────
#  2. Initialise the 66 base tree
#     66 tree init creates /etc/66/... and /run/66/...
# ─────────────────────────────────────────

print("\nInitialising 66 base tree...")
rc = chroot(["66", "tree", "init", "boot"])
if rc != 0:
    print(f"  WARNING: '66 tree init boot' exited {rc} — may be expected on first run.")

# ─────────────────────────────────────────
#  3. Enable core 66 services
#     Adjust service names to match what your 66-init package ships.
#     Common ones from obarun/void 66 packaging:
# ─────────────────────────────────────────

services = [
    "boot@system",  # core boot bundle (mounts, udev, etc.)
    "getty@tty1",  # console login on tty1
    "getty@tty2",
    "dhcpcd",  # basic networking — swap for NetworkManager if preferred
]

print("\nEnabling 66 services...")
for svc in services:
    rc = chroot(["66", "enable", svc])
    print(f"  {'✓' if rc == 0 else '✗'} {svc}")

# ─────────────────────────────────────────
#  4. Set fish as root shell (backup in case useradd default doesn't apply)
# ─────────────────────────────────────────

passwd = rootfs / "etc" / "passwd"
if passwd.exists():
    text = passwd.read_text()
    text = text.replace("root:/bin/bash", "root:/usr/bin/fish", 1)
    text = text.replace("root:/bin/sh", "root:/usr/bin/fish", 1)
    passwd.write_text(text)
    print("\n✓ root shell → /usr/bin/fish")

print("\n✓ post-setup complete.")
