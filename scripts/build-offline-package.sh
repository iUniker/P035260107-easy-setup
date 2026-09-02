#!/usr/bin/env bash
set -Eeuo pipefail

repo_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
version="$(tr -d '[:space:]' < "${repo_dir}/VERSION")"
output_path="${1:-${repo_dir}/dist-packages/iUniker-MZP351-Offline-Setup-${version}.zip}"
output_dir="$(dirname -- "${output_path}")"
output_name="$(basename -- "${output_path}")"
package_name="iUniker-MZP351-Offline-Setup"
temporary_dir="$(mktemp -d "${TMPDIR:-/tmp}/mzp351-package.XXXXXX")"

cleanup() {
  rm -rf -- "${temporary_dir}"
}
trap cleanup EXIT

mkdir -p "${output_dir}" "${temporary_dir}/${package_name}/config"
output_dir="$(cd -- "${output_dir}" && pwd -P)"
output_path="${output_dir}/${output_name}"
rm -f -- "${output_path}" "${output_path}.sha256"
install -m 0755 "${repo_dir}/packaging/offline/INSTALL" "${temporary_dir}/${package_name}/INSTALL"
install -m 0755 "${repo_dir}/install.sh" "${temporary_dir}/${package_name}/install.sh"
install -m 0755 "${repo_dir}/uninstall.sh" "${temporary_dir}/${package_name}/uninstall.sh"
install -m 0755 "${repo_dir}/diagnose.sh" "${temporary_dir}/${package_name}/diagnose.sh"
install -m 0644 "${repo_dir}/packaging/offline/START-HERE.txt" "${temporary_dir}/${package_name}/START-HERE.txt"
install -m 0644 "${repo_dir}/QUICK_START.md" "${temporary_dir}/${package_name}/QUICK_START.md"
install -m 0644 "${repo_dir}/output/pdf/iUniker-MZP351-Quick-Start.pdf" "${temporary_dir}/${package_name}/iUniker-MZP351-Quick-Start.pdf"
install -m 0644 "${repo_dir}/VERSION" "${temporary_dir}/${package_name}/VERSION"
install -m 0644 "${repo_dir}/config/mzp351hv00tr-kms.txt" "${temporary_dir}/${package_name}/config/mzp351hv00tr-kms.txt"

(
  cd -- "${temporary_dir}"
  zip -q -r -X "${output_path}" "${package_name}"
)

(
  cd -- "${output_dir}"
  shasum -a 256 "${output_name}" > "${output_name}.sha256"
)
printf '%s\n' "${output_path}"
printf '%s\n' "${output_path}.sha256"
