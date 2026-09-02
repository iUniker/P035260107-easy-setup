# MazerPi 3.51-inch LCD Quick Start

Model: MZP351HV00TR / P035260107

This setup keeps your existing operating system, applications, network settings,
and user files. It only adds the boot configuration required by the display and
touchscreen.

## Before you begin

- Shut down and unplug the Raspberry Pi before connecting or removing the LCD.
- Carefully align the 40-pin connector. Incorrect alignment may permanently
  damage the LCD or Raspberry Pi.
- Remove other GPIO HATs and accessories for the first test. This LCD uses 25
  GPIO pins, including the SPI0 pins used by the touchscreen.
- Use a stable 5V power supply and a high-quality USB power cable.
- Disconnect HDMI during the first test.
- This is a resistive touchscreen. Light pressure from a fingertip, fingernail,
  or stylus is required. Multi-touch gestures are not supported.
- Do not use the `--force` or `--yes` option unless instructed by support.

## Choose one installation method

### Method A - Online install (recommended)

If the Raspberry Pi has Internet access and you can open Terminal or connect by
SSH, copy and run this single command:

```bash
curl -fsSL https://raw.githubusercontent.com/iUniker/P035260107-easy-setup/main/install.sh | sudo bash -s -- --reboot
```

The Raspberry Pi checks compatibility, preserves the existing operating system
and settings, creates a timestamped backup, installs the display configuration,
and reboots. The URL becomes active after the separate setup repository is
published. Do not run a similar command from an unofficial URL.

### Method B - Install from a downloaded copy

Download and extract the setup ZIP on the Raspberry Pi, open Terminal in the
extracted folder, and run:

```bash
sudo bash install.sh --reboot
```

The installer checks compatibility, creates a timestamped backup, installs the
managed display configuration, and reboots the Raspberry Pi.

### Method C - Install from a web browser to the SD card

Use a current desktop version of Chrome or Microsoft Edge:

1. Shut down the Raspberry Pi and insert its microSD card into the computer.
2. Open the official MazerPi setup page.
3. Choose **SD-card install**.
4. Click **Select boot partition** and choose the small partition usually named
   `bootfs`.
5. Verify the selected name, then click **Install display setup**.
6. After the success message, safely eject the card.

The browser modifies only the folder selected by the customer. Nothing is
uploaded. If the browser method is unavailable, use Method D.

### Method D - Downloaded Windows tool

On a Windows PC:

1. Shut down the Raspberry Pi and remove the microSD card.
2. Insert the microSD card into the Windows PC.
3. Download and extract the setup ZIP.
4. Double-click `install-windows.cmd`.
5. Verify the drive letter, volume label, and capacity shown by the installer.
6. Type `INSTALL` when asked to confirm the correct SD card.
7. After the success message, safely eject the microSD card.
8. Insert it into the Raspberry Pi, connect the LCD, and power on.

The Windows tool modifies only the Raspberry Pi boot partition. It does not open
or modify the Linux system partition.

## What changes

The installer creates `mzp351hv00tr.txt` in the boot partition and adds one
clearly marked block to the existing `config.txt`. It does not replace the
entire file. A backup similar to the following is created first:

```text
config.txt.backup-20260901-120000-1234
```

## Important compatibility limits

- Intended for Raspberry Pi Zero, Zero W/WH, and Zero 2 W/2 WH systems that use
  the standard Raspberry Pi `config.txt` boot process and provide the required
  KMS overlays.
- A customised Raspberry Pi OS installation can be supported without removing
  the customer's applications or settings.
- Ubuntu, RetroPie, Batocera, Kali, LibreELEC, Android, and custom kernels are
  not supported unless the exact release has been listed as tested.
- Other DPI displays, SPI0 devices, GPIO HATs, and devices using GPIO18 or
  GPIO27 may conflict with this LCD.
- If `config.txt` already includes `mzp351hv00tr-new.txt` or
  `mzp351hv00tr-old.txt`, the original setup is already present. The managed
  installer stops without making changes.
- A reboot is required. The LCD configuration cannot take effect immediately.

## Troubleshooting

| Symptom | Check first |
| --- | --- |
| Backlight is on but the screen is white | Confirm the installer completed, disconnect HDMI, check the 40-pin alignment, then run the diagnostic tool. |
| Screen and backlight are completely off | Check the power supply, USB cable, GPIO alignment, and GPIO18 conflicts. |
| Picture works but touch does not | Remove other SPI devices and GPIO accessories; check GPIO27 and the touchscreen connector. |
| Touch direction is wrong | Return the display to its default orientation. Display rotation requires a matching touch transformation. |
| Picture flickers or colours are incorrect | Check the power supply, header solder joints, connector seating, and panel batch. |
| HDMI works but the LCD does not | Disconnect HDMI for the first test; the OS may have selected HDMI as the primary display. |
| A window does not fit on screen | The native desktop resolution is 480x320; some applications require a larger display. |
| Raspberry Pi does not boot after setup | Use the offline uninstaller or restore the timestamped `config.txt` backup. |
| Windows does not find the SD card | Reinsert the card, close Raspberry Pi Imager, check the write-lock switch, and confirm that the `bootfs` partition has a drive letter. |

## Remove the managed configuration

On a running Raspberry Pi:

```bash
sudo bash uninstall.sh --reboot
```

On Windows with the microSD card inserted, double-click
`uninstall-windows.cmd`. The original `config.txt` backups are preserved.

## Create a diagnostic report

```bash
sudo bash diagnose.sh | tee mzp351-diagnostic.txt
```

Send `mzp351-diagnostic.txt` to customer support together with the Raspberry Pi
model, OS name, and a clear photo of the 40-pin connection. The report does not
collect passwords, Wi-Fi credentials, or user files.
