#!/usr/bin/env python3
import subprocess
from datetime import date
from pathlib import Path

project_root = Path(__file__).parent.resolve()
mklive_root = project_root / "void-mklive"


# ─────────────────────────────────────────
#  Sanity checks
# ─────────────────────────────────────────

if not (mklive_root / "mklive.sh").exists():
    print(f"  ERROR: {mklive_root / 'mklive.sh'} not found.")
    print("  Make sure the void-mklive submodule is initialised:")
    print("    git submodule update --init")
    raise SystemExit(1)


# ─────────────────────────────────────────
#  Packages
# ─────────────────────────────────────────

kernel = ["linux-mainline", "linux-mainline-headers"]
shell = ["fish-shell"]
intel = ["linux-firmware-intel", "intel-media-driver", "intel-ucode"]
py = ["python", "uv"]
mesa = [
    "glu",
    "mesa-dri",
    "mesa-opencl",
    "mesa-vaapi",
    "mesa-vdpau",
    "mesa-vulkan-intel",
]
rm = [
    "linux6.12",
    "linux6.12-headers",
    "linux6.18",
    "linux6.18-headers",
]

packages = " ".join(set([*kernel, *shell, *intel, *py]))
remove = " ".join(rm)


# ─────────────────────────────────────────
#  Output path and filename
# ─────────────────────────────────────────

print(f"{'═' * 58}")
print("  OUTPUT")
print(f"{'═' * 58}\n")

today = date.today().strftime("%Y%m%d")
default_dir = Path.home()
default_name = f"void-{today}.iso"

raw_dir = input(f"  Output directory [{default_dir}]: ").strip()
out_dir = Path(raw_dir).expanduser() if raw_dir else default_dir

raw_name = input(f"  ISO filename [{default_name}]: ").strip()
out_name = raw_name if raw_name else default_name

if not out_name.endswith(".iso"):
    out_name += ".iso"

out_path = out_dir / out_name

print(f"\n  → ISO will be written to: {out_path}\n")

try:
    out_dir.mkdir(parents=True, exist_ok=True)
except OSError as e:
    print(f"  ERROR: Could not create output directory: {e}")
    raise SystemExit(1)


# ─────────────────────────────────────────
#  Build the iso
# ─────────────────────────────────────────

cmd = [
    "sudo",
    "./mklive.sh",
    "-a",
    "x86_64",
    "-b",
    "base-system",
    "-r",
    "https://repo-default.voidlinux.org/current",
    "-r",
    "https://repo-default.voidlinux.org/current/nonfree",
    "-o",
    str(out_path),
    "-p",
    packages,
    "-g",
    remove,
    "-I",
    str(project_root / "custom-files"),
    "-x",
    "post-setup.py",
    "-C",
    "mitigations=off nowatchdog threadirqs",
    "-v",
    "linux-mainline",
    "-k",
    "us",
    "-l",
    "en_US.UTF-8",
    "-e",
    "/usr/bin/fish",
]

result = subprocess.run(cmd, cwd=mklive_root)
if result.returncode == 0:
    print(f"\n  ✓ ISO written to: {out_path}")
else:
    print(f"\n  ✗ Build failed (exit code {result.returncode}).")
