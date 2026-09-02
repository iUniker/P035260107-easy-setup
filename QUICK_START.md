# MazerPi 3.51-inch LCD Quick Start

Model: MZP351HV00TR / P035260107

This setup keeps your existing operating system, applications, network
settings, and user files. It adds only the boot configuration required by the
display and resistive touchscreen.

## Before you begin

- Shut down and unplug the Raspberry Pi before connecting or removing the LCD.
- Carefully align the 40-pin connector. Incorrect alignment may damage the LCD
  or Raspberry Pi.
- Remove other GPIO HATs and accessories for the first test.
- Use a stable 5V power supply and a high-quality USB power cable.
- Disconnect HDMI during the first display test.
- This is a resistive touchscreen. It requires light pressure and does not
  support multi-touch gestures.

## Method 1 — Online install (recommended)

Use this method when the Raspberry Pi has Internet access and Terminal or SSH
is available. Run this single command on the Raspberry Pi:

```bash
curl -fsSL https://raw.githubusercontent.com/iUniker/P035260107-easy-setup/main/install.sh | sudo bash -s -- --reboot
```

The installer checks compatibility, creates a timestamped backup, installs the
managed display configuration, and reboots automatically.

## Method 2 — Install from downloaded ZIP

Use this method when the Raspberry Pi cannot access GitHub during installation.

1. [Download the ZIP](https://github.com/iUniker/P035260107-easy-setup/archive/refs/heads/main.zip)
   on any device with Internet access.
2. Transfer the ZIP to the Raspberry Pi and extract it.
3. Open Terminal inside the extracted folder.
4. Run:

```bash
sudo bash install.sh --reboot
```

The ZIP performs the same checks and changes as the online method.

## Expected result

After the reboot, allow 30–60 seconds for startup:

- Raspberry Pi OS Desktop should show the desktop.
- Raspberry Pi OS Lite should show a text login console. This is normal.
- The touchscreen should respond to light pressure in a graphical desktop.

## What changes

The installer creates `mzp351hv00tr.txt` in the boot partition and adds one
clearly marked block to the existing `config.txt`. It does not replace the
entire file. A timestamped backup is created before any change.

## Compatibility limits

- Intended for Raspberry Pi Zero, Zero W/WH, and Zero 2 W/2 WH with current
  Raspberry Pi OS overlays.
- Ubuntu, RetroPie, Batocera, Kali, LibreELEC, Android, and custom kernels are
  unsupported unless the exact release is listed as tested.
- Other DPI displays, SPI0 devices, GPIO HATs, and devices using GPIO18 or
  GPIO27 may conflict with this LCD.
- If the old setup already includes `mzp351hv00tr-new.txt` or
  `mzp351hv00tr-old.txt`, remove that old include before switching installers.
- A reboot is required before the display settings take effect.

## Troubleshooting

| Symptom | Check first |
| --- | --- |
| Backlight is on but the screen is white | Confirm installation completed, disconnect HDMI, and check 40-pin alignment. |
| Screen and backlight are completely off | Check the power supply, USB cable, GPIO alignment, and GPIO18 conflicts. |
| Picture works but touch does not | Remove other SPI devices and check GPIO27 and the touchscreen connector. |
| Touch direction is wrong | Return the display to its default orientation; rotation also requires a touch transform. |
| Picture flickers or colours are incorrect | Check power, header solder joints, connector seating, and panel batch. |
| HDMI works but the LCD does not | Disconnect HDMI for the first test so it is not selected as the primary display. |
| A window does not fit on screen | The native resolution is 480x320; some applications require a larger display. |
| Raspberry Pi does not boot after setup | Restore the timestamped `config.txt` backup from another boot method. |

## Remove the setup

From the downloaded and extracted setup folder:

```bash
sudo bash uninstall.sh --reboot
```

## Create a diagnostic report

From the downloaded and extracted setup folder:

```bash
sudo bash diagnose.sh | tee mzp351-diagnostic.txt
```

Send `mzp351-diagnostic.txt` to support with the Raspberry Pi model, OS name,
and a clear photo of the 40-pin connection. The report does not collect
passwords, Wi-Fi credentials, or user files.
