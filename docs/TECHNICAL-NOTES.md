# Technical notes

## Why this is configuration, not a third-party kernel driver

The existing modern configuration uses three overlays supplied by current
Raspberry Pi kernels and firmware:

- `spi0-0cs` frees the two SPI0 chip-select GPIOs for the DPI data bus.
- `ads7846` binds the in-kernel resistive touchscreen driver.
- `vc4-kms-dpi-generic` describes the RGB565 panel and its timing.

The setup package therefore does not need to compile code, replace the kernel,
or install a persistent background service.

## Managed boot configuration

The installer keeps product configuration in `mzp351hv00tr.txt` and adds this
block to the customer's existing `config.txt`:

```ini
# BEGIN MZP351HV00TR MANAGED CONFIG
[all]
# Added only if the existing config does not already contain these settings:
dtoverlay=vc4-kms-v3d
max_framebuffers=2
include mzp351hv00tr.txt
# END MZP351HV00TR MANAGED CONFIG
```

This makes installation idempotent and allows uninstallation without guessing
which lines belong to the customer.

## Timing validation still required

The preserved KMS timing has:

- Horizontal total: `480 + 20 + 10 + 10 = 520`
- Vertical total: `320 + 10 + 2 + 2 = 334`
- Pixel clock: `12,000,000 Hz`

The calculated refresh rate is approximately:

```text
12,000,000 / (520 x 334) = 69.09 Hz
```

That does not match the 60 Hz claim in the original manual. A nominal 60 Hz
clock for those totals would be 10,420,800 Hz. Do not change the production
timing based on arithmetic alone: verify cold boot, image stability, colour,
touch behaviour, and supported clock divisors on real Zero and Zero 2 hardware.

## Suggested physical test matrix

- Raspberry Pi Zero / Zero W with a current 32-bit OS and kernel.
- Raspberry Pi Zero 2 W with current 32-bit and 64-bit OS kernels.
- Raspberry Pi OS Trixie and supported Bookworm installations.
- At least one current Ubuntu Raspberry Pi image if Ubuntu support is claimed.
- Desktop and console-only boots.
- Cold boot, warm reboot, screen blanking, backlight off/on, and repeated touch
  calibration checks.

Record the exact OS image date, kernel, firmware package, board revision, and
panel batch for every pass/fail result.
