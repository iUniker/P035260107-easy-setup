#!/usr/bin/env bash
set -Eeuo pipefail

repo_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
test_root="$(mktemp -d "${TMPDIR:-/tmp}/mzp351-tests.XXXXXX")"
trap 'rm -rf -- "${test_root}"' EXIT

fail() {
  printf 'FAIL: %s\n' "$*" >&2
  exit 1
}

assert_count() {
  local expected="$1"
  local pattern="$2"
  local file="$3"
  local actual
  actual="$(grep -Fc -- "${pattern}" "${file}" || true)"
  [[ "${actual}" == "${expected}" ]] || fail "Expected ${expected} occurrences of '${pattern}' in ${file}, found ${actual}"
}

make_boot_fixture() {
  local fixture="$1"
  mkdir -p "${fixture}/overlays"
  touch "${fixture}/overlays/spi0-0cs.dtbo"
  touch "${fixture}/overlays/ads7846.dtbo"
  touch "${fixture}/overlays/vc4-kms-dpi-generic.dtbo"
}

fixture_one="${test_root}/boot-one"
make_boot_fixture "${fixture_one}"
cat > "${fixture_one}/config.txt" <<'EOF'
# Existing customer configuration
dtparam=audio=on
dtoverlay=vc4-kms-v3d
max_framebuffers=2
EOF

"${repo_dir}/install.sh" --boot-dir "${fixture_one}" --yes
assert_count 1 "# BEGIN MZP351HV00TR MANAGED CONFIG" "${fixture_one}/config.txt"
assert_count 1 "include mzp351hv00tr.txt" "${fixture_one}/config.txt"
assert_count 1 "dtoverlay=vc4-kms-v3d" "${fixture_one}/config.txt"
[[ -f "${fixture_one}/mzp351hv00tr.txt" ]] || fail "Managed fragment was not installed"

"${repo_dir}/install.sh" --boot-dir "${fixture_one}" --yes
assert_count 1 "# BEGIN MZP351HV00TR MANAGED CONFIG" "${fixture_one}/config.txt"
assert_count 1 "include mzp351hv00tr.txt" "${fixture_one}/config.txt"
backup_count="$(find "${fixture_one}" -maxdepth 1 -name 'config.txt.backup-*' | wc -l | tr -d ' ')"
[[ "${backup_count}" == "2" ]] || fail "Repeated installs did not preserve two distinct backups"

"${repo_dir}/uninstall.sh" --boot-dir "${fixture_one}"
assert_count 0 "# BEGIN MZP351HV00TR MANAGED CONFIG" "${fixture_one}/config.txt"
assert_count 1 "dtoverlay=vc4-kms-v3d" "${fixture_one}/config.txt"
compgen -G "${fixture_one}/mzp351hv00tr.txt.disabled-*" >/dev/null || fail "Disabled fragment was not preserved"

fixture_two="${test_root}/boot-two"
make_boot_fixture "${fixture_two}"
cat > "${fixture_two}/config.txt" <<'EOF'
# Customer config without KMS entries
dtparam=audio=on
EOF

"${repo_dir}/install.sh" --boot-dir "${fixture_two}" --yes
assert_count 1 "dtoverlay=vc4-kms-v3d" "${fixture_two}/config.txt"
assert_count 1 "max_framebuffers=2" "${fixture_two}/config.txt"
"${repo_dir}/uninstall.sh" --boot-dir "${fixture_two}"
assert_count 0 "dtoverlay=vc4-kms-v3d" "${fixture_two}/config.txt"
assert_count 0 "max_framebuffers=2" "${fixture_two}/config.txt"

fixture_conflict="${test_root}/boot-conflict"
make_boot_fixture "${fixture_conflict}"
cat > "${fixture_conflict}/config.txt" <<'EOF'
dtoverlay=vc4-kms-dpi-generic
EOF

if "${repo_dir}/install.sh" --boot-dir "${fixture_conflict}" --yes >/dev/null 2>&1; then
  fail "Installer did not reject a conflicting display configuration"
fi
[[ ! -f "${fixture_conflict}/mzp351hv00tr.txt" ]] || fail "Conflict path modified the fixture"

fixture_include_conflict="${test_root}/boot-include-conflict"
make_boot_fixture "${fixture_include_conflict}"
cat > "${fixture_include_conflict}/config.txt" <<'EOF'
include usercfg.txt
EOF
cat > "${fixture_include_conflict}/usercfg.txt" <<'EOF'
dtoverlay=ads7846,penirq=27
EOF
if "${repo_dir}/install.sh" --boot-dir "${fixture_include_conflict}" --yes >/dev/null 2>&1; then
  fail "Installer did not detect a conflict in an included config file"
fi
[[ ! -f "${fixture_include_conflict}/mzp351hv00tr.txt" ]] || fail "Recursive conflict path modified the fixture"

fixture_fkms="${test_root}/boot-fkms"
make_boot_fixture "${fixture_fkms}"
printf 'dtoverlay=vc4-fkms-v3d\n' > "${fixture_fkms}/config.txt"
if "${repo_dir}/install.sh" --boot-dir "${fixture_fkms}" --yes >/dev/null 2>&1; then
  fail "Installer did not reject the legacy FKMS graphics stack"
fi

fixture_conditional="${test_root}/boot-conditional"
make_boot_fixture "${fixture_conditional}"
cat > "${fixture_conditional}/config.txt" <<'EOF'
[pi4]
dtoverlay=vc4-kms-v3d
[all]
dtparam=audio=on
EOF
"${repo_dir}/install.sh" --boot-dir "${fixture_conditional}" --yes >/dev/null
assert_count 2 "dtoverlay=vc4-kms-v3d" "${fixture_conditional}/config.txt"
"${repo_dir}/uninstall.sh" --boot-dir "${fixture_conditional}" >/dev/null
assert_count 1 "dtoverlay=vc4-kms-v3d" "${fixture_conditional}/config.txt"

fixture_prefix="${test_root}/boot-prefix"
mkdir -p "${fixture_prefix}/vendor/overlays"
touch "${fixture_prefix}/vendor/overlays/spi0-0cs.dtbo"
touch "${fixture_prefix}/vendor/overlays/ads7846.dtbo"
touch "${fixture_prefix}/vendor/overlays/vc4-kms-dpi-generic.dtbo"
cat > "${fixture_prefix}/config.txt" <<'EOF'
os_prefix=vendor/
overlay_prefix=overlays/
EOF
"${repo_dir}/install.sh" --boot-dir "${fixture_prefix}" --yes >/dev/null
[[ -f "${fixture_prefix}/mzp351hv00tr.txt" ]] || fail "Installer did not support os_prefix and overlay_prefix"

fixture_confirm="${test_root}/boot-confirm"
make_boot_fixture "${fixture_confirm}"
printf 'dtparam=audio=on\n' > "${fixture_confirm}/config.txt"
if "${repo_dir}/install.sh" --boot-dir "${fixture_confirm}" </dev/null >/dev/null 2>&1; then
  fail "Non-interactive offline install proceeded without --yes"
fi
[[ ! -f "${fixture_confirm}/mzp351hv00tr.txt" ]] || fail "Unconfirmed offline install modified the fixture"

fixture_crlf="${test_root}/boot-crlf"
make_boot_fixture "${fixture_crlf}"
printf '# Windows-style config\r\ndtparam=audio=on\r\n' > "${fixture_crlf}/config.txt"
"${repo_dir}/install.sh" --boot-dir "${fixture_crlf}" --yes >/dev/null
awk '{ sub(/\r$/, ""); printf "%s\r\n", $0 }' "${fixture_crlf}/config.txt" > "${fixture_crlf}/config.crlf"
mv "${fixture_crlf}/config.crlf" "${fixture_crlf}/config.txt"
"${repo_dir}/install.sh" --boot-dir "${fixture_crlf}" --yes >/dev/null
assert_count 1 "# BEGIN MZP351HV00TR MANAGED CONFIG" "${fixture_crlf}/config.txt"
"${repo_dir}/uninstall.sh" --boot-dir "${fixture_crlf}" >/dev/null
assert_count 0 "# BEGIN MZP351HV00TR MANAGED CONFIG" "${fixture_crlf}/config.txt"

printf 'All installer tests passed.\n'
