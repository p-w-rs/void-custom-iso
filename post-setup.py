#!/usr/bin/env python3
import sys
from pathlib import Path

if len(sys.argv) != 2:
    print("Usage: post-setup.py <rootfs_path>")
    sys.exit(1)

rootfs = Path(sys.argv[1])
print(f"Configuring system in: {rootfs}")

print("\n\n\n\nI AM RUNNING!!\n\n\n\n")
