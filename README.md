# MZP351HV00TR Easy Setup

Non-destructive setup for the MazerPi 3.51-inch 480x320 DPI LCD with resistive
touch. It is designed for customers who already have a configured Raspberry Pi
system and do not want to replace it with a vendor image.

The installer does **not** replace the OS or kernel, use DKMS, or modify
applications, network settings, and user data. It enables drivers and Device
Tree overlays already supplied by Raspberry Pi OS.

Customer instructions: [English Quick Start](QUICK_START.md)

Engineering must complete the [validation plan](docs/ENGINEERING-TEST-PLAN.md)
before a production release.

## Two customer installation methods

### 1. Online install — recommended

On a connected Raspberry Pi, open Terminal or connect by SSH and run:

```bash
curl -fsSL https://raw.githubusercontent.com/iUniker/P035260107-easy-setup/main/install.sh | sudo bash -s -- --reboot
```

The command downloads the installer over HTTPS, checks compatibility, creates a
timestamped backup, adds only the managed display settings, and reboots.

### 2. Downloaded ZIP — no Internet on the Raspberry Pi

[Download the ZIP](https://github.com/iUniker/P035260107-easy-setup/archive/refs/heads/main.zip)
on any connected device. Transfer it to the Raspberry Pi, extract it, open
Terminal in the extracted folder, and run:

```bash
sudo bash install.sh --reboot
```

The ZIP method performs the same checks and changes as the online method. It
does not require the Raspberry Pi to access GitHub while installing.

## What the installer changes

The installer:

1. Finds the active Raspberry Pi boot partition.
2. Verifies that the required overlay files exist.
3. Checks the board model and existing settings for conflicts.
4. Backs up `config.txt` with a timestamp.
5. Copies `mzp351hv00tr.txt` to the boot partition.
6. Adds one clearly marked managed block to the existing `config.txt`.

It never overwrites the entire `config.txt`. Running it again updates the
managed block instead of adding duplicates.

## Uninstall

From the downloaded and extracted setup folder on a running Raspberry Pi:

```bash
sudo bash uninstall.sh --reboot
```

The uninstaller removes only the managed block, preserves the display fragment
as a timestamped disabled file, and creates another `config.txt` backup.

## Diagnostics

From the downloaded and extracted setup folder:

```bash
sudo bash diagnose.sh | tee mzp351-diagnostic.txt
```

The report contains hardware, kernel, overlay, DRM, input, and backlight state.
It does not collect passwords, Wi-Fi credentials, or user files.

## Important compatibility notes

- Designed for Raspberry Pi Zero, Zero W/WH, and Zero 2 W/2 WH boards using
  current KMS-capable Raspberry Pi OS firmware and kernel overlays.
- Other distributions and custom kernels are unsupported until the exact
  release appears in the tested compatibility list.
- The display occupies 25 GPIOs. Existing DPI, ADS7846, SPI0, GPIO18, or GPIO27
  use may conflict with it.
- An original `mzp351hv00tr-new.txt` or `mzp351hv00tr-old.txt` include must be
  removed before switching to this managed installer.
- The 12 MHz panel timing remains unchanged until alternative timing has passed
  physical testing.

See [Technical notes](docs/TECHNICAL-NOTES.md) for the design rationale and
remaining hardware validation work.
