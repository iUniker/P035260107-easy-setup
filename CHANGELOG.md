# Changelog

## 0.4.1-engineering.1

- Added a small customer ZIP with a top-level `INSTALL` launcher.
- Desktop customers can double-click `INSTALL`; Lite and headless customers can
  run the short fallback command `bash INSTALL`.
- Removed website source and engineering files from the customer ZIP.
- Added a two-page US Letter PDF Quick Start covering online/offline and
  Desktop/Lite/headless installation paths.

## 0.4.0-engineering.1

- Reduced the customer installation choices to two: one-command online setup
  and an extracted ZIP run directly on the Raspberry Pi.
- Removed the browser SD-card writer and Windows PowerShell customer tools.
- Simplified the English setup page and Quick Start around the same two flows.

## 0.3.0-engineering.1

- Added a self-contained online installation path for a one-command customer
  setup on a running Raspberry Pi.
- Added a browser-based SD-card installer project for Chrome and Edge.
- Kept the downloadable ZIP and original TXT method as support fallbacks.

## 0.2.0-engineering.1

- Added non-destructive online and Windows/macOS/Linux offline configuration installers.
- Added timestamped backup and recoverable uninstall behaviour.
- Added hardware, overlay, conflict, and idempotency checks.
- Added a privacy-conscious diagnostic report.
- Added English and Simplified Chinese documentation.
- Added recursive include scanning and FKMS/legacy display conflict detection.
- Added explicit offline target confirmation and Windows drive information.
- Added a customer-facing English Quick Start and engineering validation plan.
