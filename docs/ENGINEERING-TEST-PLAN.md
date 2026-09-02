# Engineering validation plan

Do not publish the setup package to customers until every release gate below has
passed on physical hardware.

## Test inventory

Record one row for every hardware and OS combination.

| Pi model | OS and image date | Architecture | Kernel | Firmware | LCD batch | Result |
| --- | --- | --- | --- | --- | --- | --- |
| Zero |  | 32-bit |  |  |  | Not run |
| Zero W/WH |  | 32-bit |  |  |  | Not run |
| Zero 2 W/2 WH |  | 32-bit |  |  |  | Not run |
| Zero 2 W/2 WH |  | 64-bit |  |  |  | Not run |

Test the current Raspberry Pi OS release first. Test Bookworm or other releases
only if they will be listed as supported. Do not infer support from one similar
distribution.

## Software safety tests

For every supported OS:

- Start from a clean image and save the original `config.txt` checksum.
- Add representative customer settings: Wi-Fi, SSH, camera, UART, audio, custom
  comments, multiple `include` files, and conditional sections.
- Test installation on the running Pi.
- Test the public one-command HTTPS install on the running Pi. Confirm the exact
  published URL uses the reviewed repository and fails closed for HTTP errors.
- Run the one-command installer twice and confirm the embedded configuration is
  byte-for-byte identical to `config/mzp351hv00tr-kms.txt`.
- Download the public offline ZIP on another device and transfer it to each
  supported Pi. On Raspberry Pi OS Desktop, extract it and double-click
  `INSTALL`; confirm the terminal opens, requests elevation, and reboots. On
  Raspberry Pi OS Lite, extract it and run `bash INSTALL` without network
  access.
- Confirm the online command and downloaded ZIP install byte-for-byte identical
  managed display configuration.
- Confirm the installer creates a unique timestamped backup.
- Run the installer twice and confirm only one managed block exists.
- Confirm unrelated settings and included files remain byte-for-byte unchanged.
- Test uninstall and confirm only the managed block is removed.
- Confirm the disabled display fragment and all backups remain recoverable.
- Make the boot partition read-only and confirm installation stops safely.
- Add FKMS, legacy DPI, ADS7846, SPI0, and another DPI overlay one at a time;
  confirm installation stops before writing files.
- Put a conflicting setting in a nested `include`; confirm it is detected.
- Test missing and circular include files.
- Test LF, CRLF, UTF-8 comments, and a `config.txt` with no final newline.
- Test `os_prefix` and `overlay_prefix` layouts.
- Run `diagnose.sh` and verify that it contains no credentials or user data.

## Hardware and display tests

For each row in the inventory:

- Inspect and photograph correct 40-pin alignment.
- Perform 20 cold boots and 20 warm reboots.
- Confirm boot console, desktop, and full-screen application output.
- Test once with HDMI disconnected and once with HDMI connected.
- Confirm the native 480x320 mode and record the measured refresh rate.
- Run a solid red, green, blue, white, black, gradient, and fine checkerboard
  test pattern for at least 30 minutes.
- Check for rolling, flicker, colour-channel swaps, unstable sync, and excessive
  panel or Raspberry Pi temperature.
- Repeat with at least three LCD units from each production batch.
- Test touch at the centre, four corners, four edges, and during a continuous
  drag. Record dead zones, jitter, axis direction, and pressure behaviour.
- Test backlight off/on for 50 cycles and after screen blanking or suspend.
- Test with a known-good 5V supply and then with the minimum supported supply.
- Confirm the screen recovers after an unexpected power loss.
- Confirm GPIO19, GPIO25, and GPIO26 remain usable as documented.
- Confirm every other claimed GPIO is unavailable and clearly documented.

## Timing release gate

The current total timing and 12 MHz clock calculate to approximately 69.09 Hz,
not 60 Hz. Before publishing a refresh-rate claim:

1. Measure the actual DPI pixel clock and vertical refresh rate.
2. Test the current 12 MHz configuration across multiple panel batches.
3. Test any proposed 60 Hz timing separately; do not substitute 10.4208 MHz
   based only on arithmetic.
4. Record the final approved values and update the manual, product listing, and
   configuration together.

## Release gates

A release candidate passes only when:

- Every advertised Pi/OS combination has a completed test row.
- There are no unreviewed modifications outside the managed boot block and
  managed fragment.
- Install, repeated install, uninstall, and backup recovery all pass.
- Every known conflict produces an understandable English error before writing.
- The release ZIP has a version number and published SHA-256 checksum.
- The English Quick Start matches the online command and downloaded ZIP.
- Engineering signs off on display timing, touch calibration, backlight, power,
  and GPIO claims.

## Test result template

```text
Test ID:
Date:
Engineer:
Pi model and revision:
OS image and date:
Kernel:
Firmware:
LCD serial/batch:
Power supply:
Install method:
Expected result:
Actual result:
Pass/Fail:
Diagnostic report attached:
Photos/video attached:
Notes:
```
