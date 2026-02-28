import subprocess
from pathlib import Path

services_path = Path("./services")
services = []

packages_path = Path("./packages")
packages = []


# ─────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────


def load_package_set(file: Path) -> list[str]:
    """Read and return all packages listed in a file (space or newline separated)."""
    with open(file, "r") as f:
        return [pkg for line in f for pkg in line.strip().split() if pkg]


def load_service_file(file: Path) -> dict:
    """Parse a service file and return a dict with package, service, and raw content."""
    with open(file, "r") as f:
        content = f.read()

    result = {"package": None, "service": None, "content": content}

    for line in content.splitlines():
        if line.startswith("package:"):
            result["package"] = line.split(":", 1)[1].strip()
        elif line.startswith("service:"):
            result["service"] = line.split(":", 1)[1].strip()

    return result


def prompt_yes_no(question: str) -> bool:
    while True:
        answer = input(f"{question} [y/n]: ").strip().lower()
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        print("  Please enter 'y' or 'n'.")


# ─────────────────────────────────────────
#  Packages
# ─────────────────────────────────────────

print(f"\n{'═' * 40}")
print("  PACKAGES")
print(f"{'═' * 40}")

for file in sorted(packages_path.glob("*")):
    pkg_list = load_package_set(file)

    if not pkg_list:
        print(f"\n[{file.name}] — empty, skipping.")
        continue

    print(f"\n{'─' * 40}")
    print(f"  {file.name}")
    print(f"{'─' * 40}")
    for pkg in pkg_list:
        print(f"  • {pkg}")

    if prompt_yes_no(f"\nAdd all {len(pkg_list)} package(s) from '{file.name}'?"):
        packages.extend(pkg_list)
        print(f"  ✓ Added {len(pkg_list)} package(s).")
    else:
        print(f"  ✗ Skipped.")


# ─────────────────────────────────────────
#  Services
# ─────────────────────────────────────────

print(f"\n{'═' * 40}")
print("  SERVICES")
print(f"{'═' * 40}")

for file in sorted(services_path.glob("*")):
    info = load_service_file(file)

    if not info["package"] or not info["service"]:
        print(f"\n[{file.name}] — missing package or service field, skipping.")
        continue

    print(f"\n{'─' * 40}")
    print(f"  {file.name}")
    print(f"{'─' * 40}")
    print(info["content"])

    if prompt_yes_no(
        f"\nAdd service '{info['service']}' (package: '{info['package']}')?"
    ):
        packages.append(info["package"])
        services.append(info["service"])
        print(f"  ✓ Added service '{info['service']}' and package '{info['package']}'.")
    else:
        print(f"  ✗ Skipped.")


# ─────────────────────────────────────────
#  Summary
# ─────────────────────────────────────────

print(f"\n{'═' * 40}")
print("  SUMMARY")
print(f"{'═' * 40}")

print(f"\n  Packages ({len(packages)} total):")
if packages:
    for pkg in packages:
        print(f"    • {pkg}")
else:
    print("    (none selected)")

print(f"\n  Services ({len(services)} total):")
if services:
    for svc in services:
        print(f"    • {svc}")
else:
    print("    (none selected)")

print(f"\n{'═' * 40}\n")

if not packages and not services:
    print("  Nothing selected — aborting.")
    raise SystemExit(1)

if not prompt_yes_no("Run mkiso.sh with the above selection?"):
    print("  Aborted.")
    raise SystemExit(0)


# ─────────────────────────────────────────
#  Build command and run
# ─────────────────────────────────────────

cmd = [
    "sudo",
    "./void-mklive/mkiso.sh",
    "-a",
    "x86_64",
    "-b",
    "base",
    "-v",
    "linux-mainline",
    "-r",
    "https://mirrors.servercentral.com/voidlinux/current",
    "-r",
    "https://mirrors.servercentral.com/voidlinux/current/nonfree",
    "-I",
    "./custom-files",
    "-x",
    "./post-setup.sh",
    "--",
    "-k",
    "linux-mainline",
    "-e",
    "/usr/bin/fish",
]

if services:
    cmd += ["-S", " ".join(services)]

if packages:
    cmd += ["-p", " ".join(packages)]

print("  Running command:")
print("  " + " ".join(cmd))
print()

result = subprocess.run(cmd)
raise SystemExit(result.returncode)
