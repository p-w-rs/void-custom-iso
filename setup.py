import re
import subprocess
from pathlib import Path

project_root = Path(__file__).parent.resolve()
mklive_root = project_root / "void-mklive"

services_path = project_root / "services"
services = []

packages_path = project_root / "packages"
packages = []


# ─────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────


def load_package_set(file: Path) -> list[str]:
    """Read and return all packages listed in a file (space or newline separated)."""
    with open(file, "r") as f:
        return [pkg for line in f for pkg in line.strip().split() if pkg]


def parse_service_names(raw: str) -> list[str]:
    """Parse service names from a service: field value.

    Handles comma-separated lists (e.g. 'socklog-unix, nanoklogd') and strips
    parenthetical notes (e.g. 'pipewire (user service)' → 'pipewire').
    """
    names = []
    for part in raw.split(","):
        name = re.sub(r"\s*\(.*?\)", "", part).strip()
        if name:
            names.append(name)
    return names


def load_service_file(file: Path) -> dict:
    """Parse a service file and return a dict with package, services, and raw content.

    Fields parsed:
      package:      the xbps package to install
      service:      comma-separated runit service name(s) to enable via -S
      user_service: true/yes — package installed but service NOT passed to -S
                    (must be enabled per-user in ~/.config/runit/sv/)
    """
    with open(file, "r") as f:
        content = f.read()

    result = {
        "package": None,
        "services": None,
        "user_service": False,
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

    # Skip files missing required fields.
    # user_service entries need package but no service: field.
    if not info["package"]:
        print(f"\n[{file.name}] — missing package field, skipping.")
        continue
    if not info["user_service"] and not info["services"]:
        print(
            f"\n[{file.name}] — missing service field and not a user_service, skipping."
        )
        continue

    print(f"\n{'─' * 40}")
    print(f"  {file.name}")
    print(f"{'─' * 40}")
    print(info["content"])

    if info["user_service"]:
        label = (
            f"package '{info['package']}' (user service — enable manually after boot)"
        )
        question = f"\nInstall {label}?"
    else:
        svc_label = ", ".join(info["services"])
        label = f"service(s) '{svc_label}' (package: '{info['package']}')"
        question = f"\nAdd {label}?"

    if prompt_yes_no(question):
        packages.append(info["package"])
        if not info["user_service"]:
            services.extend(info["services"])
        if info["user_service"]:
            print(
                f"  ✓ Added package '{info['package']}' (user service — see note above)."
            )
        else:
            print(f"  ✓ Added {label}.")
    else:
        print(f"  ✗ Skipped.")


# ─────────────────────────────────────────
#  Dedup (preserve selection order)
# ─────────────────────────────────────────

packages = list(dict.fromkeys(packages))
services = list(dict.fromkeys(services))


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

print(f"\n  Services to enable via -S ({len(services)} total):")
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
    "./mkiso.sh",
    # mkiso.sh options (before --)
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
    # mklive.sh options (after --)
    "--",
    "-g",
    "linux6.12 linux6.12-headers",
    "-C",
    "mitigations=off nowatchdog threadirqs",
    "-v",
    "linux6.18",
    "-I",
    str(project_root / "custom-files"),
    "-x",
    str(project_root / "post-setup.sh"),
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

print("  Running command:")
print("  " + " ".join(cmd))
print()

# Run from inside void-mklive so that ./lib.sh resolves correctly
result = subprocess.run(cmd, cwd=mklive_root)
raise SystemExit(result.returncode)
