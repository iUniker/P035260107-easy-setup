#!/usr/bin/env bash
set -Eeuo pipefail

readonly FRAGMENT_NAME="mzp351hv00tr.txt"
readonly MARKER_BEGIN="# BEGIN MZP351HV00TR MANAGED CONFIG"
readonly MARKER_END="# END MZP351HV00TR MANAGED CONFIG"

boot_dir=""
reboot_after=0
temporary_config=""

usage() {
  cat <<'EOF'
Remove only the configuration managed by the MZP351HV00TR installer.

Usage:
  sudo ./uninstall.sh [--reboot]
  ./uninstall.sh --boot-dir /path/to/bootfs
EOF
}

fail() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

cleanup() {
  if [[ -n "${temporary_config}" && -f "${temporary_config}" ]]; then
    rm -f -- "${temporary_config}"
  fi
}
trap cleanup EXIT

strip_managed_block() {
  local input_file="$1"
  local output_file="$2"

  awk -v begin="${MARKER_BEGIN}" -v end="${MARKER_END}" '
    {
      comparable = $0
      sub(/\r$/, "", comparable)
    }
    comparable == begin { in_block = 1; found = 1; next }
    comparable == end {
      if (!in_block) exit 41
      in_block = 0
      next
    }
    !in_block { print }
    END {
      if (in_block) exit 42
      if (!found) exit 43
    }
  ' "${input_file}" > "${output_file}"
}

resolve_boot_dir() {
  local candidate
  if [[ -n "${boot_dir}" ]]; then
    boot_dir="${boot_dir%/}"
    [[ -f "${boot_dir}/config.txt" ]] || fail "config.txt not found in ${boot_dir}"
    return
  fi
  for candidate in /boot/firmware /boot; do
    if [[ -f "${candidate}/config.txt" ]]; then
      boot_dir="${candidate}"
      return
    fi
  done
  fail "Boot configuration not found. Use --boot-dir for an offline SD card."
}

while (( $# > 0 )); do
  case "$1" in
    --boot-dir)
      (( $# >= 2 )) || fail "--boot-dir requires a path"
      boot_dir="$2"
      offline_mode=1
      shift 2
      ;;
    --reboot)
      reboot_after=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *) fail "Unknown option: $1" ;;
  esac
done

if [[ -z "${offline_mode:-}" && ${EUID} -ne 0 ]]; then
  fail "Run this uninstaller with sudo, or use --boot-dir for a writable offline SD card."
fi

resolve_boot_dir
config_file="${boot_dir}/config.txt"
fragment_file="${boot_dir}/${FRAGMENT_NAME}"
[[ -w "${boot_dir}" && -w "${config_file}" ]] || fail "Boot configuration is not writable: ${boot_dir}"

timestamp="$(date +%Y%m%d-%H%M%S)-$$"
config_backup="${config_file}.backup-${timestamp}"
cp -p -- "${config_file}" "${config_backup}"

temporary_config="$(mktemp "${boot_dir}/.config.txt.mzp351.XXXXXX")"
if ! strip_managed_block "${config_file}" "${temporary_config}"; then
  fail "Managed configuration markers were not found or are incomplete. No changes were made."
fi

chmod 0644 "${temporary_config}" 2>/dev/null || true
mv -f -- "${temporary_config}" "${config_file}"
temporary_config=""

if [[ -f "${fragment_file}" ]]; then
  disabled_fragment="${fragment_file}.disabled-${timestamp}"
  mv -- "${fragment_file}" "${disabled_fragment}"
  printf 'Configuration fragment preserved as: %s\n' "${disabled_fragment}"
fi

sync
printf 'Managed display configuration removed.\nBackup: %s\n' "${config_backup}"

if [[ -n "${offline_mode:-}" ]]; then
  printf 'Safely eject the SD card before removing it.\n'
elif (( reboot_after )); then
  reboot
else
  printf 'Reboot to apply the change: sudo reboot\n'
fi
