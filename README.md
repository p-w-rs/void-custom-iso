# Void Linux — Custom ISO Builder

A scriptable, interactive ISO builder for Void Linux, built on top of
[void-mklive](https://github.com/void-linux/void-mklive). It produces a
bootable x86_64 ISO with a curated package set, enabled runit services,
custom dotfiles, and a post-setup hook — all chosen through an interactive
terminal menu.

Two build targets are supported:

- **Desktop** — mangowc Wayland compositor, greetd login manager, PipeWire
  audio, Bluetooth, GPU acceleration, and GUI applications.
- **Server** — kmscon TTY on tty1, SSH-hardened, firewall preconfigured,
  no desktop stack.

---

## Requirements

The build must run on an existing Void Linux host (bare metal, VM, or
another Void install). The following must be present:

```sh
sudo xbps-install -S git python3 xorriso squashfs-tools
```

Root access is required by `mkiso.sh` (via `sudo`).

---

## Setup

Clone the repository and initialise the void-mklive submodule:

```sh
git clone https://github.com/yourname/void-custom-iso
cd void-custom-iso
git submodule update --init
```

Python 3.14+ is required. If you use `uv` (recommended):

```sh
uv run setup.py
```

Or with the system Python directly:

```sh
python3 setup.py
```

---

## Running the Builder

```sh
uv run setup.py
```

The script walks you through four stages:

### 1 — Build mode

Choose **Desktop** or **Server**. Package files and services marked
`# mode: desktop` or `# mode: server` are automatically included or
excluded based on your choice. Mixed files (no mode tag) are always
offered.

### 2 — Package selection

Each file in `packages/` is presented with its full package list. Confirm
or skip each group. Desktop-only groups are hidden in server mode and vice
versa.

### 3 — Service selection

Each file in `services/` is presented with a full description, a
server-suitability rating, and a recommended default (yes/no). Services
marked as user services (PipeWire, WirePlumber) are installed but not
passed to `-S` — they must be enabled after first boot.

### 4 — Output path and build

You will be prompted for:

- **Output directory** — where the finished ISO is written. Defaults to
  `~/void-isos/` (created automatically if it does not exist).
- **ISO filename** — defaults to
  `void-custom-<mode>-<date>.iso` (e.g. `void-custom-desktop-20260301.iso`).

A summary of all selected packages and services is shown before the build
begins. Confirm to proceed; the build invokes `mkiso.sh` via `sudo` and
may take several minutes depending on your internet connection and CPU.

---

## Output

The finished ISO is written to your chosen output path, for example:

```
~/void-isos/void-custom-desktop-20260301.iso
```

Write it to a USB drive with `dd` or use [Ventoy](https://www.ventoy.net)
to boot it without re-flashing on every rebuild:

```sh
# dd method — replaces all USB contents
sudo dd if=~/void-isos/void-custom-desktop-20260301.iso \
         of=/dev/sdX bs=4M status=progress conv=fsync

# Ventoy — copy the ISO file to the Ventoy partition; no dd needed
cp ~/void-isos/void-custom-desktop-20260301.iso /run/media/$USER/Ventoy/
```

See [INSTALL.md](INSTALL.md) for the full post-boot installation walkthrough.

---

## Repository Layout

```
void-custom-iso/
├── setup.py                  # Interactive ISO builder
├── post-setup.sh             # Runs inside the rootfs before initramfs
├── packages/                 # Package lists, one file per category
│   ├── base.txt
│   ├── audio.txt             # mode: desktop
│   ├── bluetooth.txt         # mode: desktop
│   └── ...
├── services/                 # Service description files
│   ├── openssh.txt
│   ├── chrony.txt
│   └── ...
├── custom-files/             # Files copied verbatim into the ISO rootfs
│   ├── etc/
│   │   ├── greetd/config.toml
│   │   ├── kmscon/kmscon.conf
│   │   └── nftables.conf
│   └── opt/
│       └── update-odin
└── void-mklive/              # git submodule — upstream Void ISO tooling
```

### Adding packages

Create a new `.txt` file in `packages/`. Optionally add `# mode: desktop`
or `# mode: server` as the first non-blank line. List one package per line;
blank lines and `#` comments are ignored.

### Adding services

Create a new `.txt` file in `services/` following the existing format.
Required fields: `package:`, `service:` (or `user_service: true`), and
`server:` (YES / NO / OPTIONAL / CONDITIONAL).

### Custom files

Anything placed under `custom-files/` is copied into the ISO rootfs by
`mkiso.sh -I`. Use this for configs, scripts, or anything that needs to
land at a specific path on the installed system.

---

## Kernel and Boot Parameters

The builder targets the **linux6.18** kernel. The following boot parameters
are applied by default:

| Parameter | Effect |
|-----------|--------|
| `mitigations=off` | Disables Spectre/Meltdown patches — improves performance on trusted hardware |
| `nowatchdog` | Disables hardware watchdog timers — reduces spurious NMIs |
| `threadirqs` | Forces threaded IRQ handlers — improves audio and latency |

Edit the `cmd` list in `setup.py` to change kernel version or boot
parameters before building.

---

## Rebuilding and Updating

After changing packages, services, or custom-files, re-run `setup.py` and
write the new ISO to USB. Ventoy users can simply overwrite the old ISO
file — no re-flashing required.

To update the void-mklive submodule to the latest upstream:

```sh
git submodule update --remote void-mklive
git commit -am "Update void-mklive submodule"
```
