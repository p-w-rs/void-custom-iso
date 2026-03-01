# Void Linux — Installation Guide

This guide walks through installing Void Linux from the custom ISO produced
by `setup.py`. It assumes you already have a bootable USB drive — if not,
see the section below.

---

## Preparing the USB Drive

You do not need to know how to write ISOs if you use
[Ventoy](https://www.ventoy.net). Install Ventoy on a USB drive once, then
copy any ISO file onto it — no re-flashing required when you rebuild.

If you prefer the traditional method:

```sh
sudo dd if=void-custom-desktop-20260301.iso \
         of=/dev/sdX bs=4M status=progress conv=fsync
```

Replace `/dev/sdX` with your USB device (`lsblk` to confirm — do not guess).

Boot the target machine from the USB. The live environment will start
automatically.

---

## Running the Installer

From the live environment, run:

```sh
sudo void-installer
```

The installer is a text-mode wizard. Each section is covered below.

---

## Keyboard

```
keymap: us
```

Change if your keyboard layout differs (e.g. `uk`, `de`, `fr`).

---

## Network

The installer will scan for available interfaces. Select your network
interface and choose **DHCP**. Wait for the confirmation that a lease was
obtained before continuing. A working internet connection is required to
fetch packages.

---

## Source

```
Select: Network
```

This fetches the latest packages from the Void mirrors rather than using
the (potentially outdated) packages baked into the ISO.

---

## Mirror

Choose **Default** or the nearest Tier-1 mirror for your region. For
North America the default US mirror is a good choice. A closer mirror
will significantly speed up the package download phase.

---

## Hostname

The hostname is how this machine identifies itself on the network
(e.g. `thinkpad`, `homeserver`, `void-desktop`). Choose something short,
lowercase, and without spaces. You can change it later by editing
`/etc/hostname`.

---

## Locale

```
en_US.UTF-8
```

---

## Timezone

Select your region and city. For example:

```
America/Boise
America/New_York
America/Los_Angeles
Europe/London
```

---

## Root Password

The root password is for emergency recovery only — day-to-day work should
use your user account with `sudo`. Choose something strong and store it
somewhere safe. It does **not** need to match your user password.

---

## User Account

The installer will ask for:

- **Login name** — your Unix username (lowercase, no spaces, e.g. `alex`)
- **Password** — your daily-use login password
- **Full name** — your display name or anything you like (e.g. `Alex Johnson`)
- **Groups** — see the table below

### Group Selection

Read the table carefully. The installer pre-selects a reasonable set, but
several additions and removals are strongly recommended.

**Legend**

| Symbol | Meaning |
|--------|---------|
| ✔ | Pre-selected by installer — keep as-is |
| ✚ | Not pre-selected — add this |
| ✖ | Pre-selected — remove this |
| — | Not needed; leave unchecked |

---

#### Groups selected by the installer

| Group | Purpose | Server | Desktop |
|-------|---------|:------:|:-------:|
| `wheel` | `sudo` and `doas` access | ✔ | ✔ |
| `users` | General shared-resource group | ✔ | ✔ |
| `video` | `/dev/dri` — KMS, kmscon, and GPU access | ✔ | ✔ |
| `kvm` | `/dev/kvm` — hardware virtualisation (QEMU, VMs) | ✔ | ✔ |
| `xbuilder` | Build Void packages with `xbps-src` | ✔ | ✔ |
| `audio` | Legacy OSS/ALSA device access; superseded by PipeWire on desktop | ✖ remove | ✔ keep |
| `cdrom` | Optical drive access | ✔ | ✔ |
| `optical` | Optical drive alias | ✔ | ✔ |
| `floppy` | Floppy drive — no modern use | ✖ remove | ✖ remove |

#### Groups to add

| Group | Purpose | Server | Desktop |
|-------|---------|:------:|:-------:|
| `socklog` | Read logs in `/var/log/socklog/` without sudo | ✚ add | ✚ add |
| `input` | `/dev/input/*` — required for kmscon and input device access | ✚ add | ✚ add |
| `dialout` | Serial ports (`/dev/ttyUSB*`, `/dev/ttyS*`) — microcontrollers, USB-serial adapters | ✚ add | ✚ add |
| `storage` | Mount/unmount storage devices without sudo | ✚ add | ✚ add |
| `plugdev` | Unprivileged USB device access | ✚ add | ✚ add |
| `docker` | Run Docker without sudo (only if Docker is installed) | ✚ add | ✚ add |
| `network` | NetworkManager CLI tools (`nmcli`) | — | ✚ add |
| `scanner` | SANE scanner device access | — | ✚ add |

#### Groups to leave unchecked

| Group | Why |
|-------|-----|
| `disk` | Raw block device access — bypasses filesystem permissions entirely |
| `adm` | Broad system log and admin access |
| `daemon` / `bin` / `sys` | Internal daemon groups |
| `kmem` | Direct kernel memory read access |
| `tty` | All TTY devices — broader than needed |
| `tape` | Tape drive access |
| `lp` | Printer device files (manage printers through CUPS instead) |
| `utmp` | Write access to login records |
| `mail` | Mail spool access |
| `avahi` / `sgx` / `usbmon` | Daemon or specialised debugging groups — not for users |

#### Quick reference — applying changes after install

If you missed any groups during install, fix them afterwards:

```sh
# Server
sudo usermod -rG floppy "$USER"
sudo usermod -aG socklog,input,dialout,storage,plugdev,docker "$USER"

# Desktop
sudo usermod -rG floppy "$USER"
sudo usermod -aG socklog,input,dialout,storage,plugdev,docker,network,scanner "$USER"
```

Log out and back in (or reboot) for group changes to take effect.
Verify with: `id` or `groups`.

---

## Boot Loader

Select the disk you are installing to (e.g. `/dev/sda`, `/dev/nvme0n1`).
Use the **graphical terminal** option for the boot loader — it renders
fonts correctly in the live environment.

---

## Partitioning

Select your target disk and choose **cfdisk**. When prompted for partition
table type, select **GPT**.

Create partitions in this order:

| # | Size | Type | Mount |
|---|------|------|-------|
| 1 | 512 MB | EFI System | `/boot/efi` |
| 2 | 8 GB | Linux swap | swap |
| 3 | Remainder | Linux filesystem | `/` |

> **Note:** If you have 32 GB+ of RAM and do not plan to hibernate,
> a 4 GB swap is sufficient. For hibernation, swap should be at least
> the size of your RAM.

When done, navigate to **Write**, type `yes`, then **Quit**.

---

## Filesystems

The installer will ask you to assign a filesystem to each partition.

| Partition | Filesystem | Mount Point |
|-----------|-----------|-------------|
| 512 MB EFI | `vfat` | `/boot/efi` |
| 8 GB swap | `swap` | *(none — selected automatically)* |
| Remaining | `ext4` *(or `xfs`, `btrfs`)* | `/` |

If you are unsure, choose `ext4` for the root partition. It is stable,
well-supported, and easy to recover. `btrfs` is a good choice if you want
snapshots. Select **Done** when finished.

---

## Services

The installer will present a list of system services to enable at boot.
This is one of the most important steps — enabling the wrong services can
cause conflicts, and missing essential ones will leave your system broken
after first boot.

### Legend

| Symbol | Meaning |
|--------|---------|
| ✔ | Pre-selected — keep |
| ✚ | Not pre-selected — add this |
| ✖ | Pre-selected — remove this |
| — | Leave unchecked |

---

### Pre-selected services

These are checked by default in the installer. Review each one for your
build type.

| Service | Purpose | Server | Desktop |
|---------|---------|:------:|:-------:|
| `acpid` | Handles hardware events — power button, lid open/close, AC adapter. Essential on physical hardware for graceful shutdown and suspend scripting. | ✔ keep | ✔ keep |
| `avahi-daemon` | mDNS/Zeroconf — lets machines find each other by `hostname.local` on a LAN without a DNS server. Also enables printer and file share discovery. | ✔ keep if LAN discovery wanted; ✖ remove for locked-down servers | ✔ keep |
| `chronyd` | NTP time synchronisation. Void has no built-in time sync. Without this, clock drift will break TLS certificates, log timestamps, and cron. **Enable on everything.** | ✔ keep | ✔ keep |
| `cronie` | Cron daemon. Runs scheduled jobs from `/etc/cron.d/` and user crontabs. Required for certbot renewal, backups, and any periodic automation. | ✔ keep | ✔ keep |
| `dhcpcd` | DHCP client — automatically configures wired and wireless network interfaces. The Void default. Use this on servers and desktops that do not need NetworkManager. | ✔ keep | ✔ keep if not using NetworkManager |
| `nanoklogd` | Captures kernel log messages (equivalent to `klogd`). Part of the socklog system. Without it, kernel messages are silently lost. | ✔ keep | ✔ keep |
| `nftables` | Firewall. Loads rules from `/etc/nftables.conf`. The ISO ships a safe default: allow SSH and ping inbound, drop everything else. **Enable on everything exposed to a network.** | ✔ keep | ✔ keep |
| `socklog-unix` | Syslog daemon — collects log messages from all daemons writing to `/dev/log`. Writes plain-text logs to `/var/log/socklog/`. Without this, most daemon output is silently lost on Void. | ✔ keep | ✔ keep |
| `sshd` | OpenSSH server. Required for any remote access. Enable on servers unconditionally. On desktops, enable if you ever need to log in from another machine. | ✔ keep | ✔ keep |
| `wpa-supplicant` | Wi-Fi authentication daemon. Required for WPA2/WPA3 wireless networks. Not needed on machines with only wired Ethernet. **Note:** NetworkManager manages `wpa_supplicant` internally — do not run both on the same interface. | ✖ remove on wired-only servers | ✔ keep |

---

### Services not pre-selected

These are unchecked by default. Most should stay unchecked; add only
what you specifically need.

| Service | Purpose | Server | Desktop |
|---------|---------|:------:|:-------:|
| `agetty-hvc0` | Serial console for **Hyper-V** virtual machines (host-VM communication channel). Only relevant inside a Hyper-V VM. | ✚ add if running in Hyper-V | — |
| `agetty-hvsi0` | High-speed Hyper-V serial interface. A secondary Hyper-V console. Only relevant inside a Hyper-V VM. | ✚ add if running in Hyper-V | — |
| `agetty-ttyAMA0` | Serial console for **ARM** boards (Raspberry Pi, Rockchip, etc.). Exposes a TTY over the board's UART pins. | ✚ add if on ARM/RPi | — |
| `agetty-ttyS0` | Serial console on the first COM port (`/dev/ttyS0`). Useful for headless bare-metal servers managed over a serial line or IPMI/BMC. | ✚ add if using serial console | — |
| `agetty-ttyUSB0` | Serial console over USB-serial adapter. Useful for embedded hardware or out-of-band management via a USB-serial cable. | ✚ add if using USB serial console | — |
| `alsa` | Legacy ALSA sound daemon. **Not needed** on our custom build — PipeWire handles all audio, including ALSA compatibility via `alsa-plugins-ffmpeg`. Enabling both causes conflicts. | — | — |
| `bftpd` | FTP server daemon. Only enable if you explicitly need an FTP server on this machine. FTP is unencrypted — prefer `sftpgo` (SFTP) for file transfers. | ✚ add if serving FTP | — |
| `containerd` | Container runtime used by Docker and Kubernetes. Must be running if you use Docker or any OCI container tooling. | ✚ add if using containers | ✚ add if using containers |
| `dhcpcd-eth0` | `dhcpcd` scoped to a single interface. Useful if you want DHCP only on one interface and static config on others. **Conflicts with the general `dhcpcd` service** — use one or the other, not both. | — *(use `dhcpcd` instead)* | — |
| `dmeventd` | Device Mapper event daemon. Required if you use **LVM** (Logical Volume Manager). Monitors LVM volumes for events like low space or mirror failures. Only needed if your disk layout uses LVM. | ✚ add if using LVM | — |
| `docker` | Docker daemon. Enables `docker` CLI commands and container management. Requires `containerd` to also be enabled. Add both or neither. | ✚ add if using Docker | ✚ add if using Docker |
| `ip6tables` | Legacy IPv6 packet filter. **Replaced by nftables**, which handles both IPv4 and IPv6. Do not run alongside nftables. | — | — |
| `iptables` | Legacy IPv4 packet filter. **Replaced by nftables**. Do not run alongside nftables — they conflict. | — | — |
| `kmscon` | GPU-accelerated TTY. **Do not enable here** — the custom ISO's `post-setup.sh` configures kmscon automatically on the correct TTY (tty2 for desktop, tty1 for server). Enabling it via the installer will double-up the configuration. | — *(handled by post-setup.sh)* | — |
| `mdadm` | Linux software RAID daemon. Required if your storage uses MD RAID (`/dev/md0`, etc.). Only enable if you set up software RAID during partitioning. | ✚ add if using software RAID | — |
| `nvidia-powerd` | NVIDIA GPU power management daemon. Enables dynamic power scaling on **RTX 30-series and newer** NVIDIA GPUs. Only relevant if an NVIDIA GPU is installed. | — | ✚ add if NVIDIA RTX 30+ GPU |
| `rsyncd` | rsync server daemon. Only enable if this machine is acting as an rsync **server** that other machines pull from or push to. Not needed for running `rsync` as a client. | ✚ add if serving rsync | — |
| `sftpgo` | Full-featured SFTP/WebDAV/FTP server. Enable if you need a managed file-transfer server with user accounts and web UI. Prefer this over `bftpd` for anything serious. | ✚ add if serving SFTP/files | — |
| `tftpd-hpa` | TFTP server. A simple, unauthenticated file server used for PXE network booting and firmware updates. Only enable if this machine is a PXE boot server or serves firmware. | ✚ add if PXE server | — |
| `uuidd` | UUID generation daemon. Provides a kernel-assisted random UUID source for high-throughput applications (databases, container runtimes). Only needed if you run workloads that generate thousands of UUIDs per second. | — | — |

---

> **Summary for most installs:**
>
> *Server:* Keep all pre-selected except `avahi-daemon` and `wpa-supplicant`
> (remove both on a wired, non-LAN-discovery server). Add `docker` and
> `containerd` if using containers. Everything else: leave unchecked.
>
> *Desktop:* Keep everything pre-selected. Add `nvidia-powerd` if you have
> an RTX 30+ GPU. Add `docker` + `containerd` if you use Docker.
> Everything else: leave unchecked.

---

## Install

Select **Yes** to confirm and begin installation. The installer will:

1. Wipe and partition the target disk as configured
2. Copy the base system from the ISO
3. Fetch and install the selected package set from the network
4. Enable the selected services
5. Generate the initramfs and install the GRUB bootloader

This takes 5–20 minutes depending on disk speed and network. When it
completes, remove the USB drive and reboot.

---

## First Boot

After rebooting into the installed system:

### Both builds

Verify time synchronisation is working:

```sh
chronyc tracking
```

Confirm the firewall is active:

```sh
sudo nft list ruleset
```

Check that logs are being collected:

```sh
ls /var/log/socklog/
```

### Server

Harden SSH before doing anything else. Edit `/etc/ssh/sshd_config`:

```
PermitRootLogin no
PasswordAuthentication no
# Consider changing Port from 22
```

Copy your public key to the server first, then restart sshd:

```sh
sudo sv restart sshd
```

Open any additional firewall ports you need in `/etc/nftables.conf`, then:

```sh
sudo sv restart nftables
```

### Desktop

Enable user audio services (PipeWire + WirePlumber). These are user
services — they cannot be enabled via `sv` and must be linked in your
user session:

```sh
mkdir -p ~/.config/runit/sv
cp -r /usr/share/pipewire/service ~/.config/runit/sv/pipewire
cp -r /usr/share/pipewire/service ~/.config/runit/sv/pipewire-pulse
cp -r /usr/share/wireplumber/service ~/.config/runit/sv/wireplumber
ln -s ~/.config/runit/sv/pipewire     ~/.local/share/runit/service/
ln -s ~/.config/runit/sv/pipewire-pulse ~/.local/share/runit/service/
ln -s ~/.config/runit/sv/wireplumber  ~/.local/share/runit/service/
```

Refer to the [Void Handbook — User Services](https://docs.voidlinux.org/config/services/user-services.html)
for full details.

If you installed the Odin compiler, run the updater as root to build it:

```sh
sudo /opt/update-odin
```

---

## Troubleshooting

**No network after reboot** — Check that `dhcpcd` is running:
```sh
sudo sv status dhcpcd
sudo sv start dhcpcd
```

**Logs are missing** — Confirm both socklog services are running:
```sh
sudo sv status socklog-unix nanoklogd
```

**Audio not working** — Confirm PipeWire user services are linked and
running. Check `pgrep pipewire` and `pgrep wireplumber`.

**Screen is black after greetd starts (desktop)** — Switch to tty2
(`Ctrl+Alt+F2`) where kmscon is running. Check greetd logs:
```sh
cat /var/log/socklog/daemon/current | grep greetd
```

**SSH refuses password login** — If `PasswordAuthentication no` is set
in `sshd_config`, you must use an SSH key. Generate one on the client
and copy it with `ssh-copy-id`.
