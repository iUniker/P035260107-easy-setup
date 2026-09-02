#!/usr/bin/env bash
set -Eeuo pipefail

readonly PRODUCT_NAME="MazerPi MZP351HV00TR 3.51-inch DPI LCD"
readonly FRAGMENT_NAME="mzp351hv00tr.txt"
readonly MARKER_BEGIN="# BEGIN MZP351HV00TR MANAGED CONFIG"
readonly MARKER_END="# END MZP351HV00TR MANAGED CONFIG"

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
source_fragment="${script_dir}/config/mzp351hv00tr-kms.txt"
boot_dir=""
reboot_after=0
force_checks=0
temporary_config=""
temporary_fragment=""

usage() {
  cat <<'EOF'
Install the MazerPi MZP351HV00TR display configuration without replacing the OS.

Usage:
  sudo ./install.sh [--reboot]
  ./install.sh --boot-dir /path/to/bootfs

Options:
  --boot-dir DIR  Configure a mounted SD-card boot partition instead of the
                  running Raspberry Pi.
  --reboot        Reboot the running Raspberry Pi after a successful install.
  --force         Continue when the model cannot be verified or an expected
                  overlay file is missing. Display-configuration conflicts
                  are never overridden automatically.
  -h, --help      Show this help.
EOF
}

log() {
  printf '%s\n' "$*"
}

fail() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

cleanup() {
  if [[ -n "${temporary_config}" && -f "${temporary_config}" ]]; then
    rm -f -- "${temporary_config}"
  fi
  if [[ -n "${temporary_fragment}" && -f "${temporary_fragment}" ]]; then
    rm -f -- "${temporary_fragment}"
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
    comparable == begin { in_block = 1; next }
    comparable == end {
      if (!in_block) {
        print "Found an end marker without a begin marker" > "/dev/stderr"
        exit 41
      }
      in_block = 0
      next
    }
    !in_block { print }
    END {
      if (in_block) {
        print "Managed configuration block is incomplete" > "/dev/stderr"
        exit 42
      }
    }
  ' "${input_file}" > "${output_file}"
}

resolve_boot_dir() {
  local candidate

  if [[ -n "${boot_dir}" ]]; then
    boot_dir="${boot_dir%/}"
    [[ -d "${boot_dir}" ]] || fail "Boot directory not found: ${boot_dir}"
    [[ -f "${boot_dir}/config.txt" ]] || fail "config.txt not found in ${boot_dir}"
    return
  fi

  for candidate in /boot/firmware /boot; do
    if [[ -f "${candidate}/config.txt" ]]; then
      boot_dir="${candidate}"
      return
    fi
  done

  fail "Could not find /boot/firmware/config.txt or /boot/config.txt. Use --boot-dir for an offline SD card."
}

check_model() {
  local model_file=""
  local model=""

  [[ -n "${offline_mode:-}" ]] && return

  if [[ -r /proc/device-tree/model ]]; then
    model_file=/proc/device-tree/model
  elif [[ -r /sys/firmware/devicetree/base/model ]]; then
    model_file=/sys/firmware/devicetree/base/model
  fi

  if [[ -n "${model_file}" ]]; then
    model="$(tr -d '\000' < "${model_file}")"
  fi

  case "${model}" in
    *"Raspberry Pi Zero"*) log "Detected hardware: ${model}" ;;
    "")
      if (( force_checks )); then
        log "WARNING: Raspberry Pi model could not be detected."
      else
        fail "Raspberry Pi model could not be detected. Use --force only after confirming compatible hardware."
      fi
      ;;
    *)
      if (( force_checks )); then
        log "WARNING: unverified hardware model: ${model}"
      else
        fail "Unsupported or unverified hardware model: ${model}"
      fi
      ;;
  esac
}

active_value() {
  local key="$1"
  local file="$2"

  awk -F= -v wanted="${key}" '
    /^[[:space:]]*#/ { next }
    {
      name = $1
      gsub(/^[[:space:]]+|[[:space:]]+$/, "", name)
      if (name == wanted) {
        value = substr($0, index($0, "=") + 1)
        gsub(/^[[:space:]]+|[[:space:]]+$/, "", value)
        result = value
      }
    }
    END { if (result != "") print result }
  ' "${file}"
}

check_overlays() {
  local config_file="$1"
  local overlay_prefix
  local overlay_dir
  local overlay
  local missing=()

  overlay_prefix="$(active_value overlay_prefix "${config_file}")"
  overlay_prefix="${overlay_prefix:-overlays}"
  overlay_prefix="${overlay_prefix#/}"
  overlay_dir="${boot_dir}/${overlay_prefix%/}"

  for overlay in spi0-0cs ads7846 vc4-kms-dpi-generic; do
    if [[ ! -f "${overlay_dir}/${overlay}.dtbo" ]]; then
      missing+=("${overlay}.dtbo")
    fi
  done

  if (( ${#missing[@]} > 0 )); then
    if (( force_checks )); then
      log "WARNING: missing overlay files in ${overlay_dir}: ${missing[*]}"
    else
      fail "Required overlay files are missing in ${overlay_dir}: ${missing[*]}. Update the OS/firmware, or use --force only if the OS stores overlays elsewhere."
    fi
  fi
}

check_conflicts() {
  local config_file="$1"
  local conflicts

  if grep -Eq '^[[:space:]]*include[[:space:]]+mzp351hv00tr-(new|old)\.txt([[:space:]]|$)' "${config_file}"; then
    fail "This system still includes the original mzp351hv00tr-new/old file. Remove that include line before using the managed installer."
  fi

  conflicts="$(grep -En \
    '^[[:space:]]*(dtoverlay=vc4-(f)?kms-dpi-|dtoverlay=ads7846([,[:space:]]|$)|dtoverlay=spi0-0cs([,[:space:]]|$)|enable_dpi_lcd=1|dpi_(group|mode|output_format|timings)=)' \
    "${config_file}" || true)"

  if [[ -n "${conflicts}" ]]; then
    printf 'Conflicting display configuration found in %s:\n%s\n' "${config_file}" "${conflicts}" >&2
    fail "No changes were made. Remove or disable the conflicting display configuration, then run the installer again."
  fi
}

has_kms_overlay() {
  grep -Eq '^[[:space:]]*dtoverlay=vc4-kms-v3d([,[:space:]]|$)' "$1"
}

has_max_framebuffers() {
  grep -Eq '^[[:space:]]*max_framebuffers[[:space:]]*=[[:space:]]*[2-9][0-9]*([[:space:]]*(#.*)?)?$' "$1"
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
    --force)
      force_checks=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      fail "Unknown option: $1"
      ;;
  esac
done

[[ -f "${source_fragment}" ]] || fail "Configuration template not found: ${source_fragment}"

if [[ -z "${offline_mode:-}" && ${EUID} -ne 0 ]]; then
  fail "Run this installer with sudo, or use --boot-dir for a writable offline SD-card boot partition."
fi

resolve_boot_dir
config_file="${boot_dir}/config.txt"
fragment_file="${boot_dir}/${FRAGMENT_NAME}"

[[ -w "${boot_dir}" && -w "${config_file}" ]] || fail "Boot configuration is not writable: ${boot_dir}"

log "Installing ${PRODUCT_NAME}"
log "Boot partition: ${boot_dir}"

check_model

temporary_config="$(mktemp "${boot_dir}/.config.txt.mzp351.XXXXXX")"
strip_managed_block "${config_file}" "${temporary_config}"
check_conflicts "${temporary_config}"
check_overlays "${temporary_config}"

timestamp="$(date +%Y%m%d-%H%M%S)-$$"
config_backup="${config_file}.backup-${timestamp}"
cp -p -- "${config_file}" "${config_backup}"

if [[ -f "${fragment_file}" ]]; then
  cp -p -- "${fragment_file}" "${fragment_file}.backup-${timestamp}"
fi

temporary_fragment="$(mktemp "${boot_dir}/.${FRAGMENT_NAME}.XXXXXX")"
cp -- "${source_fragment}" "${temporary_fragment}"
chmod 0644 "${temporary_fragment}" 2>/dev/null || true
mv -f -- "${temporary_fragment}" "${fragment_file}"
temporary_fragment=""

{
  printf '\n%s\n' "${MARKER_BEGIN}"
  printf '[all]\n'
  if ! has_kms_overlay "${temporary_config}"; then
    printf 'dtoverlay=vc4-kms-v3d\n'
  fi
  if ! has_max_framebuffers "${temporary_config}"; then
    printf 'max_framebuffers=2\n'
  fi
  printf 'include %s\n' "${FRAGMENT_NAME}"
  printf '%s\n' "${MARKER_END}"
} >> "${temporary_config}"

chmod 0644 "${temporary_config}" 2>/dev/null || true
mv -f -- "${temporary_config}" "${config_file}"
temporary_config=""
sync

log "Installation complete."
log "Backup: ${config_backup}"
log "Managed fragment: ${fragment_file}"

if [[ -n "${offline_mode:-}" ]]; then
  log "Safely eject the SD card, insert it into the Raspberry Pi, and power on."
elif (( reboot_after )); then
  log "Rebooting now."
  reboot
else
  log "Reboot to activate the display: sudo reboot"
fi
