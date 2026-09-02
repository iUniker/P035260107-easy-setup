# MZP351HV00TR Easy Setup

Non-destructive setup tools for the MazerPi 3.51-inch 480x320 DPI LCD with
resistive touch. This project is intended for customers who already have a
configured operating system and do not want to replace it with a vendor image.

This repository does **not** replace the OS, install a custom kernel, use DKMS,
or modify applications and user data. It configures drivers and Device Tree
overlays already supplied by the operating system.

## What the installer changes

The installer:

1. Finds the active Raspberry Pi boot partition.
2. Verifies that the required overlay files exist.
3. Backs up `config.txt` with a timestamp.
4. Copies one managed file named `mzp351hv00tr.txt` to the boot partition.
5. Adds one clearly marked block to the existing `config.txt`.

It never overwrites the entire `config.txt`. Re-running the installer updates
the managed block instead of adding duplicates.

## Install on an existing running system

Download and extract this repository, then run:

```bash
cd P035260107-easy-setup
sudo bash install.sh --reboot
```

The installer supports `/boot/firmware/config.txt` and the older
`/boot/config.txt` location. It checks the actual overlay files instead of
assuming a particular Linux distribution name.

## Configure an existing SD card without booting it

This mode changes only the small FAT boot partition. It does not mount or modify
the Linux root partition.

### Windows

Insert the SD card after flashing it, then double-click `install-windows.cmd`.
The tool automatically finds a mounted Raspberry Pi boot partition.

The equivalent PowerShell command is:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\install-offline.ps1
```

If more than one possible boot volume is connected, specify the drive letter:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\install-offline.ps1 E:
```

### macOS

```bash
bash install.sh --boot-dir /Volumes/bootfs
```

### Linux PC

```bash
bash install.sh --boot-dir /media/$USER/bootfs
```

Safely eject the card after a successful offline installation.

## Uninstall

On a running Raspberry Pi:

```bash
sudo bash uninstall.sh --reboot
```

For an offline card:

```bash
bash uninstall.sh --boot-dir /path/to/bootfs
```

The uninstaller removes only the managed block. It preserves the fragment as a
timestamped `.disabled-*` file and creates another `config.txt` backup.

On Windows with an offline SD card, double-click `uninstall-windows.cmd`.

## Diagnostics

```bash
sudo bash diagnose.sh | tee mzp351-diagnostic.txt
```

The report contains hardware, kernel, overlay, DRM, input, and backlight state.
It does not collect passwords, Wi-Fi credentials, or user files.

## Important compatibility notes

- Designed for Raspberry Pi Zero, Zero W/WH, and Zero 2 W/2 WH boards using
  current KMS-capable firmware and kernel overlays.
- The display occupies 25 GPIOs. Existing DPI, ADS7846, or overlapping GPIO
  configuration is treated as a conflict and is never overwritten silently.
- The original `mzp351hv00tr-new.txt` or `mzp351hv00tr-old.txt` installation
  must be removed from `config.txt` before using this managed installer.
- The current 12 MHz timing is preserved from the vendor configuration until
  alternative timing has been validated on physical hardware.

See [Technical notes](docs/TECHNICAL-NOTES.md) for the design rationale and the
remaining hardware validation work.
