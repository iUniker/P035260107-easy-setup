#!/usr/bin/env bash
set -u

readonly MARKER_BEGIN="# BEGIN MZP351HV00TR MANAGED CONFIG"
boot_dir=""

while (( $# > 0 )); do
  case "$1" in
    --boot-dir)
      [[ $# -ge 2 ]] || { printf 'ERROR: --boot-dir requires a path\n' >&2; exit 1; }
      boot_dir="${2%/}"
      shift 2
      ;;
    -h|--help)
      printf 'Usage: ./diagnose.sh [--boot-dir /path/to/bootfs]\n'
      exit 0
      ;;
    *) printf 'ERROR: unknown option: %s\n' "$1" >&2; exit 1 ;;
  esac
done

if [[ -z "${boot_dir}" ]]; then
  if [[ -f /boot/firmware/config.txt ]]; then
    boot_dir=/boot/firmware
  elif [[ -f /boot/config.txt ]]; then
    boot_dir=/boot
  else
    printf 'ERROR: boot configuration not found.\n' >&2
    exit 1
  fi
fi

config_file="${boot_dir}/config.txt"
fragment_file="${boot_dir}/mzp351hv00tr.txt"

printf '=== MZP351HV00TR diagnostic report ===\n'
printf 'Generated: %s\n' "$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
printf 'Boot directory: %s\n' "${boot_dir}"
printf 'Kernel: %s\n' "$(uname -a 2>/dev/null || printf 'unavailable')"

if [[ -r /proc/device-tree/model ]]; then
  printf 'Hardware: '
  tr -d '\000' < /proc/device-tree/model
  printf '\n'
fi

if [[ -r /etc/os-release ]]; then
  printf '\n--- OS release ---\n'
  grep -E '^(PRETTY_NAME|ID|VERSION_ID)=' /etc/os-release || true
fi

printf '\n--- Required overlays ---\n'
for overlay in spi0-0cs ads7846 vc4-kms-dpi-generic; do
  if [[ -f "${boot_dir}/overlays/${overlay}.dtbo" ]]; then
    printf 'OK      %s.dtbo\n' "${overlay}"
  else
    printf 'MISSING %s.dtbo\n' "${overlay}"
  fi
done

printf '\n--- Managed installation ---\n'
if grep -Fq "${MARKER_BEGIN}" "${config_file}" 2>/dev/null; then
  printf 'Managed config block: present\n'
else
  printf 'Managed config block: absent\n'
fi
if [[ -f "${fragment_file}" ]]; then
  printf 'Managed fragment: present (%s bytes)\n' "$(wc -c < "${fragment_file}" | tr -d ' ')"
else
  printf 'Managed fragment: absent\n'
fi

printf '\n--- Relevant boot configuration ---\n'
grep -En \
  'MZP351|mzp351|dtoverlay=(vc4|ads7846|spi0)|max_framebuffers|enable_dpi|dpi_|backlight-gpio|gpio=18' \
  "${config_file}" "${fragment_file}" 2>/dev/null || printf 'No relevant lines found.\n'

if [[ -d /sys/class/drm ]]; then
  printf '\n--- DRM connectors ---\n'
  for status_file in /sys/class/drm/card*/status; do
    [[ -e "${status_file}" ]] || continue
    printf '%s: %s\n' "$(basename "$(dirname "${status_file}")")" "$(cat "${status_file}")"
  done
fi

if [[ -d /sys/class/backlight ]]; then
  printf '\n--- Backlight ---\n'
  for backlight in /sys/class/backlight/*; do
    [[ -d "${backlight}" ]] || continue
    printf '%s brightness=%s max=%s\n' \
      "$(basename "${backlight}")" \
      "$(cat "${backlight}/brightness" 2>/dev/null || printf '?')" \
      "$(cat "${backlight}/max_brightness" 2>/dev/null || printf '?')"
  done
fi

if [[ -r /proc/bus/input/devices ]]; then
  printf '\n--- Touch/input matches ---\n'
  grep -Ei 'Name=|ads7846|touchscreen' /proc/bus/input/devices || true
fi

printf '\nThis report does not include passwords, Wi-Fi credentials, or user files.\n'
