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
assume_yes=0
temporary_config=""
temporary_fragment=""
config_files=()

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
  --yes           Skip the confirmation prompt for an offline SD card.
                  Intended for automated testing and support workflows.
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
    boot_dir="$(cd -- "${boot_dir}" && pwd -P)"
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

confirm_offline_target() {
  local answer

  [[ -n "${offline_mode:-}" ]] || return

  log "Selected offline boot partition: ${boot_dir}"
  df -h "${boot_dir}" 2>/dev/null | tail -n 1 || true

  if (( assume_yes )); then
    return
  fi

  if [[ ! -t 0 ]]; then
    fail "Offline installation requires confirmation. Run interactively, or add --yes only after verifying the target path."
  fi

  printf 'Type INSTALL to modify this SD-card boot partition: '
  read -r answer
  [[ "${answer}" == "INSTALL" ]] || fail "Installation cancelled. No changes were made."
}

config_file_seen() {
  local wanted="$1"
  local existing
  (( ${#config_files[@]} > 0 )) || return 1
  for existing in "${config_files[@]}"; do
    [[ "${existing}" == "${wanted}" ]] && return 0
  done
  return 1
}

collect_config_file() {
  local file="$1"
  local depth="$2"
  local line
  local include_name
  local include_file
  local include_dir

  (( depth <= 12 )) || fail "Configuration include depth exceeds 12 near ${file}. Check for an include loop."
  config_file_seen "${file}" && return
  config_files+=("${file}")

  while IFS= read -r line || [[ -n "${line}" ]]; do
    line="${line%$'\r'}"
    if [[ "${line}" =~ ^[[:space:]]*include[[:space:]]+([^#[:space:]]+) ]]; then
      include_name="${BASH_REMATCH[1]}"
      include_name="${include_name#/}"
      include_file="${boot_dir}/${include_name}"

      if [[ ! -f "${include_file}" ]]; then
        log "WARNING: included configuration file was not found: ${include_name}"
        continue
      fi

      include_dir="$(cd -- "$(dirname -- "${include_file}")" && pwd -P)"
      include_file="${include_dir}/$(basename -- "${include_file}")"
      case "${include_file}" in
        "${boot_dir}"/*) collect_config_file "${include_file}" "$((depth + 1))" ;;
        *) fail "Included configuration escapes the boot partition: ${include_name}" ;;
      esac
    fi
  done < "${file}"
}

collect_config_files() {
  config_files=()
  collect_config_file "$1" 0
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

active_value_in_file() {
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

active_value() {
  local key="$1"
  local file
  local value
  local result=""

  for file in "${config_files[@]}"; do
    value="$(active_value_in_file "${key}" "${file}")"
    [[ -n "${value}" ]] && result="${value}"
  done
  printf '%s\n' "${result}"
}

check_overlays() {
  local config_file="$1"
  local overlay_prefix
  local os_prefix
  local overlay_dir
  local candidate
  local overlay
  local missing=()
  local candidates=()

  overlay_prefix="$(active_value overlay_prefix)"
  overlay_prefix="${overlay_prefix:-overlays}"
  overlay_prefix="${overlay_prefix#/}"
  os_prefix="$(active_value os_prefix)"
  os_prefix="${os_prefix#/}"

  [[ -n "${os_prefix}" ]] && candidates+=("${boot_dir}/${os_prefix%/}/${overlay_prefix%/}")
  candidates+=("${boot_dir}/${overlay_prefix%/}" "${boot_dir}/overlays")

  overlay_dir=""
  for candidate in "${candidates[@]}"; do
    if [[ -f "${candidate}/spi0-0cs.dtbo" &&
          -f "${candidate}/ads7846.dtbo" &&
          -f "${candidate}/vc4-kms-dpi-generic.dtbo" ]]; then
      overlay_dir="${candidate}"
      break
    fi
  done

  [[ -n "${overlay_dir}" ]] && return
  overlay_dir="${candidates[0]}"

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
  local config_file
  local conflicts

  for config_file in "${config_files[@]}"; do
    if grep -Eq '^[[:space:]]*include[[:space:]]+mzp351hv00tr-(new|old)\.txt([[:space:]]|$)' "${config_file}"; then
      fail "The original mzp351hv00tr-new/old configuration is already included by ${config_file}. If the display works, no migration is required. Remove that include only when intentionally switching to the managed installer."
    fi

    conflicts="$(grep -En \
      '^[[:space:]]*(dtoverlay=vc4-(f)?kms-dpi-|dtoverlay=vc4-fkms-v3d([,[:space:]]|$)|dtoverlay=ads7846([,[:space:]]|$)|dtoverlay=spi0-0cs([,[:space:]]|$)|enable_dpi_lcd=1|dpi_(group|mode|output_format|timings)=|display_default_lcd=1)' \
      "${config_file}" || true)"

    if [[ -n "${conflicts}" ]]; then
      printf 'Conflicting display configuration found in %s:\n%s\n' "${config_file}" "${conflicts}" >&2
      fail "No changes were made. Remove or disable the conflicting display configuration, then run the installer again."
    fi
  done
}

file_has_effective_setting() {
  local file="$1"
  local setting="$2"

  awk -v wanted="${setting}" '
    BEGIN { applies = 1 }
    {
      line = $0
      sub(/\r$/, "", line)
      lower = tolower(line)
    }
    lower ~ /^[[:space:]]*\[[^]]+\][[:space:]]*$/ {
      tag = lower
      gsub(/^[[:space:]]*\[|\][[:space:]]*$/, "", tag)
      if (tag == "all" || tag == "pi0" || tag == "pi0w" || tag == "pi02") {
        applies = 1
      } else if (tag == "none" || tag ~ /^(pi[1-9]|pi3\+|pi400|pi500|cm0|cm1|cm3|cm3\+|cm4|cm4s|cm5)$/) {
        applies = 0
      } else {
        # Unknown runtime filters are treated as possibly active for safety.
        applies = 1
      }
      next
    }
    applies && lower ~ wanted { found = 1 }
    END { exit(found ? 0 : 1) }
  ' "${file}"
}

has_kms_overlay() {
  local file
  for file in "${config_files[@]}"; do
    if file_has_effective_setting "${file}" '^[[:space:]]*dtoverlay=vc4-kms-v3d([,[:space:]]|$)'; then
      return 0
    fi
  done
  return 1
}

has_max_framebuffers() {
  local file
  for file in "${config_files[@]}"; do
    if file_has_effective_setting "${file}" '^[[:space:]]*max_framebuffers[[:space:]]*=[[:space:]]*[2-9][0-9]*([[:space:]]*(#.*)?)?$'; then
      return 0
    fi
  done
  return 1
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
    --yes)
      assume_yes=1
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

confirm_offline_target
check_model

temporary_config="$(mktemp "${boot_dir}/.config.txt.mzp351.XXXXXX")"
strip_managed_block "${config_file}" "${temporary_config}"
collect_config_files "${temporary_config}"
check_conflicts
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
  if ! has_kms_overlay; then
    printf 'dtoverlay=vc4-kms-v3d\n'
  fi
  if ! has_max_framebuffers; then
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
