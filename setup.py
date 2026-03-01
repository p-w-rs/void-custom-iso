#!/usr/bin/env python3
"""Void Linux custom ISO builder — interactive package and service selector."""

import os
import re
import stat
import subprocess
from datetime import date
from pathlib import Path

project_root = Path(__file__).parent.resolve()
mklive_root = project_root / "void-mklive"
services_path = project_root / "services"
packages_path = project_root / "packages"


# ─────────────────────────────────────────
#  Sanity checks
# ─────────────────────────────────────────

if not (mklive_root / "mkiso.sh").exists():
    print(f"  ERROR: {mklive_root / 'mkiso.sh'} not found.")
    print("  Make sure the void-mklive submodule is initialised:")
    print("    git submodule update --init")
    raise SystemExit(1)


# ─────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────


def load_package_file(file: Path) -> dict:
    """Read a package file and return its mode and package list.

    Files may begin with a ``# mode: <mode>`` comment where mode is one of
    'both', 'desktop', or 'server'.  If the header is absent the file is
    treated as 'both' (included regardless of build mode).
    """
    with open(file, "r") as f:
        content = f.read()

    mode = "both"
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.lower().startswith("# mode:"):
            mode = stripped.split(":", 1)[1].strip().lower()
            break
        elif stripped and not stripped.startswith("#"):
            break

    pkgs = []
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        pkgs.extend(stripped.split())

    return {"mode": mode, "packages": pkgs}


def parse_service_names(raw: str) -> list[str]:
    """Parse comma-separated service names, stripping parenthetical notes."""
    names = []
    for part in raw.split(","):
        name = re.sub(r"\s*\(.*?\)", "", part).strip()
        if name:
            names.append(name)
    return names


def load_service_file(file: Path) -> dict:
    """Parse a service description file.

    Fields:
      package:       xbps package name
      service:       comma-separated runit service name(s) to enable via -S
      user_service:  true → package installed, but NOT passed to -S
      server:        YES / NO / OPTIONAL / CONDITIONAL tag
    """
    with open(file, "r") as f:
        content = f.read()

    result = {
        "package": None,
        "services": None,
        "user_service": False,
        "server_tag": None,
        "content": content,
    }

    for line in content.splitlines():
        if line.startswith("package:"):
            result["package"] = line.split(":", 1)[1].strip()
        elif line.startswith("service:"):
            raw = line.split(":", 1)[1].strip()
            result["services"] = parse_service_names(raw)
        elif line.startswith("user_service:"):
            val = line.split(":", 1)[1].strip().lower()
            result["user_service"] = val in ("true", "yes", "1")
        elif line.startswith("server:"):
            result["server_tag"] = line.split(":", 1)[1].strip()

    return result


def prompt_yes_no(question: str, default: bool | None = None) -> bool:
    hint = {True: "[Y/n]", False: "[y/N]", None: "[y/n]"}[default]
    while True:
        answer = input(f"{question} {hint}: ").strip().lower()
        if not answer and default is not None:
            return default
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        print("  Please enter 'y' or 'n'.")


def service_recommendation(tag: str | None, mode: str) -> tuple[str, bool | None]:
    """Return a display label and prompt default based on server tag and build mode."""
    if tag is None or mode == "desktop":
        return ("", None)

    t = tag.upper()
    if "ESSENTIAL" in t:
        return (" 🟢 essential for servers", True)
    if "YES" in t and "NO" not in t:
        return (" 🟢 recommended for servers", True)
    if "CONDITIONAL" in t:
        return (" 🟡 conditional — read description", None)
    if "OPTIONAL" in t:
        return (" 🟡 optional for servers", None)
    if "NO" in t:
        return (" 🔴 not needed for servers", False)
    return ("", None)


# ─────────────────────────────────────────
#  Mode selection
# ─────────────────────────────────────────

print(f"\n{'═' * 58}")
print("  VOID LINUX — CUSTOM ISO BUILDER")
print(f"{'═' * 58}\n")
print("  [1] Desktop — mangowc compositor, greetd login manager,")
print("                audio (PipeWire), Bluetooth, GUI apps")
print("  [2] Server  — kmscon TTY on tty1, SSH-focused, no desktop\n")

while True:
    choice = input("  Build mode [1/2]: ").strip()
    if choice in ("1", "desktop"):
        mode = "desktop"
        break
    if choice in ("2", "server"):
        mode = "server"
        break
    print("  Enter 1 or 2.")

print(f"\n  → {mode.upper()} mode selected.\n")

packages: list[str] = []
services: list[str] = []


# ─────────────────────────────────────────
#  Packages
# ─────────────────────────────────────────

print(f"{'═' * 58}")
print("  PACKAGES")
print(f"{'═' * 58}")

for file in sorted(packages_path.glob("*")):
    info = load_package_file(file)
    pkg_list = info["packages"]

    if not pkg_list:
        continue

    file_mode = info["mode"]

    if mode == "server" and file_mode == "desktop":
        print(f"\n  {file.name}  🔴 desktop-only — skipped")
        continue
    if mode == "desktop" and file_mode == "server":
        print(f"\n  {file.name}  🔴 server-only — skipped")
        continue

    print(f"\n{'─' * 58}")
    tag = f"  [{file_mode}]" if file_mode != "both" else ""
    print(f"  {file.name}{tag}")
    print(f"{'─' * 58}")
    for pkg in pkg_list:
        print(f"  • {pkg}")

    if prompt_yes_no(
        f"\n  Add {len(pkg_list)} package(s) from '{file.name}'?", default=True
    ):
        packages.extend(pkg_list)
        print("  ✓ Added.")
    else:
        print("  ✗ Skipped.")


# ─────────────────────────────────────────
#  Services
# ─────────────────────────────────────────

print(f"\n{'═' * 58}")
print("  SERVICES")
print(f"{'═' * 58}")

for file in sorted(services_path.glob("*")):
    info = load_service_file(file)

    if not info["package"]:
        continue
    if not info["user_service"] and not info["services"]:
        continue

    rec_label, rec_default = service_recommendation(info["server_tag"], mode)

    print(f"\n{'─' * 58}")
    print(f"  {file.name}{rec_label}")
    print(f"{'─' * 58}")
    print(info["content"])

    if info["user_service"]:
        question = f"  Install '{info['package']}' (user service — enable after boot)?"
    else:
        svc = ", ".join(info["services"])
        question = f"  Enable {svc} (package: {info['package']})?"

    if prompt_yes_no(question, rec_default):
        packages.append(info["package"])
        if not info["user_service"]:
            services.extend(info["services"])
        print("  ✓ Added.")
    else:
        print("  ✗ Skipped.")


# ─────────────────────────────────────────
#  Dedup (preserve selection order)
# ─────────────────────────────────────────

packages = list(dict.fromkeys(packages))
services = list(dict.fromkeys(services))


# ─────────────────────────────────────────
#  Summary
# ─────────────────────────────────────────

print(f"\n{'═' * 58}")
print(f"  SUMMARY — {mode.upper()}")
print(f"{'═' * 58}")

print(f"\n  Packages ({len(packages)}):")
for pkg in packages or ["(none)"]:
    print(f"    • {pkg}")

print(f"\n  Services via -S ({len(services)}):")
for svc in services or ["(none)"]:
    print(f"    • {svc}")

print()

if not packages and not services:
    print("  Nothing selected — aborting.")
    raise SystemExit(1)


# ─────────────────────────────────────────
#  Output path and filename
# ─────────────────────────────────────────

print(f"{'═' * 58}")
print("  OUTPUT")
print(f"{'═' * 58}\n")

today = date.today().strftime("%Y%m%d")
default_dir = Path.home() / "void-isos"
default_name = f"void-custom-{mode}-{today}.iso"

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
#  Confirm and build
# ─────────────────────────────────────────

if not prompt_yes_no("  Build ISO with the above?"):
    print("  Aborted.")
    raise SystemExit(0)


# ─────────────────────────────────────────
#  Build
# ─────────────────────────────────────────

wrapper = project_root / ".post-setup-wrapper.sh"
with open(wrapper, "w") as f:
    f.write("#!/bin/bash\n")
    f.write(f'export VOID_ISO_MODE="{mode}"\n')
    f.write(f'exec "{project_root / "post-setup.sh"}" "$@"\n')
os.chmod(str(wrapper), stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP)

cmd = [
    "sudo",
    "./mkiso.sh",
    "-a",
    "x86_64",
    "-b",
    "base",
    "-r",
    "https://repo-default.voidlinux.org/current",
    "-r",
    "https://repo-default.voidlinux.org/current/nonfree",
    "-r",
    "https://repo-default.voidlinux.org/current/debug",
    "--",
    "-o",
    str(out_path),
    "-g",
    "linux6.12 linux6.12-headers",
    "-C",
    "mitigations=off nowatchdog threadirqs",
    "-v",
    "linux6.18",
    "-I",
    str(project_root / "custom-files"),
    "-x",
    str(wrapper),
    "-k",
    "us",
    "-l",
    "en_US.UTF-8",
    "-e",
    "/usr/bin/fish",
]

if services:
    cmd += ["-S", " ".join(services)]
if packages:
    cmd += ["-p", " ".join(packages)]

print("\n  Command:")
print("  " + " ".join(cmd))
print()

result = subprocess.run(cmd, cwd=mklive_root)

wrapper.unlink(missing_ok=True)

if result.returncode == 0:
    print(f"\n  ✓ ISO written to: {out_path}")
else:
    print(f"\n  ✗ Build failed (exit code {result.returncode}).")

raise SystemExit(result.returncode)
