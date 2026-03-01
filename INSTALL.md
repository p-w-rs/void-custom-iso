# Void Installer Instructions
## Keyboard
keymap us

## Network
Just make sure it comes back and says it worked, enable dhcp

## Source
local

## Mirror
choose default or the tier one for America

## Hostname
This will be the name of your computer in a sense

## Locale
en_US.UTF-8

## Timezone
America/Boise

## RootPassword
instruction how how to pick this and if is should be different than the user password

## UserAccount

it will ask you for your login name, password, and a actual name like your given name or whatever you want there then it will ask you to select your groups to be added to

The table below covers every group relevant to a Void Linux install.

**Legend**

| Symbol | Meaning |
|--------|---------|
| ✔ | Currently selected by the installer — keep |
| ✚ | Not selected — add this |
| ✖ | Currently selected — remove this |
| — | Leave unchecked; not needed |

---

### Groups selected by the Void installer

| Group | Purpose | Server / kmscon | Desktop |
|-------|---------|:--------------:|:-------:|
| `wheel` | `sudo` and `doas` access | ✔ | ✔ |
| `users` | General shared-resource group | ✔ | ✔ |
| `video` | `/dev/dri` — required for KMS, kmscon, and GPU access | ✔ | ✔ |
| `kvm` | `/dev/kvm` — hardware virtualisation (QEMU, VMs) | ✔ | ✔ |
| `xbuilder` | Build Void packages with `xbps-src` | ✔ | ✔ |
| `audio` | Legacy OSS/ALSA device access; superseded by PipeWire | ✖ remove | ✔ |
| `cdrom` | Optical drive access | ✔ | ✔ |
| `optical` | Optical drive access (alias of cdrom on some setups) | ✔ | ✔ |
| `floppy` | Floppy drive access — no modern use | ✖ remove | ✖ remove |

### Groups available to add

| Group | Purpose | Server / kmscon | Desktop |
|-------|---------|:--------------:|:-------:|
| `socklog` | Read logs in `/var/log/socklog/` without sudo | ✚ add | ✚ add |
| `docker` | Run Docker/container tools without sudo | ✚ add | ✚ add |
| `input` | `/dev/input/*` — input devices; needed for kmscon and device dev | ✚ add | ✚ add |
| `dialout` | Serial ports (`/dev/ttyUSB*`, `/dev/ttyS*`) — microcontrollers, USB-serial | ✚ add | ✚ add |
| `storage` | Mount/unmount storage devices without sudo | ✚ add | ✚ add |
| `plugdev` | Unprivileged USB device access | ✚ add | ✚ add |
| `network` | NetworkManager CLI tools; relevant if using `nmcli` | — | ✚ add |
| `scanner` | SANE scanner device access | — | ✚ add |
| `sgx` | Intel SGX enclave development only | — | — |
| `usbmon` | Raw USB packet capture — debugging only | — | — |
| `avahi` | Internal group for the avahi daemon — not for users | — | — |

### System / legacy groups — do not add

These exist for system daemons and historical Unix compatibility.
Adding a regular user to any of them grants unnecessarily broad or dangerous access.

| Group | Why to avoid |
|-------|-------------|
| `disk` | Raw read/write on block devices — can bypass filesystem permissions entirely |
| `adm` | Broad system log and admin access |
| `daemon` | Internal group for daemon processes |
| `bin` | Ownership of system binaries |
| `sys` | Kernel and system-level access |
| `kmem` | Direct read access to kernel memory |
| `tty` | All TTY devices; broader than needed |
| `tape` | Tape drive access |
| `lp` | Printer device files (use `cups` instead) |
| `utmp` | Write access to login records (`utmp`/`wtmp`) |
| `mail` | Mail spool access |

---

### Quick reference — `usermod` commands

#### Server / kmscon build

```sh
# Remove
sudo usermod -rG audio,cdrom,optical,floppy <user>

# Add
sudo usermod -aG socklog,docker,input,dialout,storage,plugdev <user>
```

#### Desktop build

```sh
# Remove
sudo usermod -rG cdrom,optical,floppy <user>

# Add
sudo usermod -aG socklog,docker,input,dialout,storage,plugdev,network,scanner <user>
```

> **Note:** Log out and back in (or reboot) after any `usermod` change for the new groups to take effect.
> Verify with `id <user>` or `groups`.

## BootLoader

Select the disk you want to install on (ex. /dev/sda)
use the graphical terminal for the bootloader

## Partition

Select the disk from before (/dev/sda)
Select use cfdisk
select gpt
with "Free space" highlighted select "New"
Partition size: 100M
now move to "Type" and select "EFI System"
now move down and highlight "Free space" again and select "New"
Parition size: 4G or 8G
now move to "Type" and select "Linux swap"
now move down and highlight "Free space" again and select "New"
Partition size: use the rest of the disk which should be prefilled in or select the rest of partition how you want if you know what you are doing
now move to "Type" and select "Linux filesystem"
now move to "Write" select it and then type "yes" then go to "Quit" and select it.

## Filesystems

Select your 100M EFI System partition and "Change", select "vfat", then "OK"
the mount point is "/boot/efi", then "Yes"

Select your 4G or 8G swap partition "Change",  select "swap", then "Yes"

Select your remaining parititon "Change",  select your file system (probably ext4, but you could also do xfs or btrfs) if you don't know choose ext4. The mount point will be "/", then "Yes"

select "Done"

## Install

Select "Yes" to wipe the install drive and install void.

It will do a bunch of file stuff and the eventually ask you about what services to enable by default
