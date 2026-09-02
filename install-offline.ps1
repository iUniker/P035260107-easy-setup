[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [string]$BootDrive,
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$MarkerBegin = "# BEGIN MZP351HV00TR MANAGED CONFIG"
$MarkerEnd = "# END MZP351HV00TR MANAGED CONFIG"
$FragmentName = "mzp351hv00tr.txt"

function Resolve-BootRoot {
    param([string]$RequestedDrive)

    if ($RequestedDrive) {
        $root = $RequestedDrive.TrimEnd([char[]]@('\', '/')) + [IO.Path]::DirectorySeparatorChar
        if (-not (Test-Path (Join-Path $root "config.txt"))) {
            throw "config.txt was not found in $root"
        }
        return $root
    }

    $candidates = @(Get-CimInstance Win32_LogicalDisk | ForEach-Object {
        if ($_.DeviceID) {
            $root = $_.DeviceID + "\"
            if ((Test-Path (Join-Path $root "config.txt")) -and
                (Test-Path (Join-Path $root "overlays"))) {
                $root
            }
        }
    })

    if ($candidates.Count -eq 0) {
        throw "No mounted Raspberry Pi boot partition was found. Pass its drive letter, for example: .\install-offline.ps1 E:"
    }
    if ($candidates.Count -gt 1) {
        throw "More than one possible boot partition was found: $($candidates -join ', '). Pass the correct drive letter explicitly."
    }
    return $candidates[0]
}

function Write-Utf8File {
    param([string]$Path, [string]$Content)
    [IO.File]::WriteAllText($Path, $Content, [Text.UTF8Encoding]::new($false))
}

$bootRoot = Resolve-BootRoot $BootDrive
$configPath = Join-Path $bootRoot "config.txt"
$fragmentPath = Join-Path $bootRoot $FragmentName
$sourceFragment = Join-Path $PSScriptRoot "config\mzp351hv00tr-kms.txt"

if (-not (Test-Path $sourceFragment)) {
    throw "Configuration template not found: $sourceFragment"
}

$requiredOverlays = @("spi0-0cs.dtbo", "ads7846.dtbo", "vc4-kms-dpi-generic.dtbo")
$missing = @($requiredOverlays | Where-Object {
    -not (Test-Path (Join-Path $bootRoot "overlays\$_"))
})
if ($missing.Count -gt 0 -and -not $Force) {
    throw "Required overlay files are missing: $($missing -join ', '). Use a current OS/firmware image."
}
if ($missing.Count -gt 0) {
    Write-Warning "Missing overlay files: $($missing -join ', ')"
}

$config = [IO.File]::ReadAllText($configPath)
$managedPattern = "(?ms)^" + [Regex]::Escape($MarkerBegin) + "\r?\n.*?^" + [Regex]::Escape($MarkerEnd) + "\r?\n?"
$cleanConfig = [Regex]::Replace($config, $managedPattern, "")

if ($cleanConfig -match '(?m)^\s*include\s+mzp351hv00tr-(new|old)\.txt(?:\s|$)') {
    throw "The original mzp351hv00tr-new/old file is still included. Remove that include line before using this installer."
}

$conflictPattern = '(?m)^\s*(dtoverlay=vc4-(?:f)?kms-dpi-|dtoverlay=ads7846(?:[,\s]|$)|dtoverlay=spi0-0cs(?:[,\s]|$)|enable_dpi_lcd=1|dpi_(?:group|mode|output_format|timings)=)'
if ($cleanConfig -match $conflictPattern) {
    throw "A conflicting DPI or ADS7846 configuration is already present. No changes were made."
}

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss-fff"
$backupPath = "$configPath.backup-$timestamp"
Copy-Item -LiteralPath $configPath -Destination $backupPath
if (Test-Path $fragmentPath) {
    Copy-Item -LiteralPath $fragmentPath -Destination "$fragmentPath.backup-$timestamp"
}

$block = New-Object System.Collections.Generic.List[string]
$block.Add($MarkerBegin)
$block.Add("[all]")
if ($cleanConfig -notmatch '(?m)^\s*dtoverlay=vc4-kms-v3d(?:[,\s]|$)') {
    $block.Add("dtoverlay=vc4-kms-v3d")
}
if ($cleanConfig -notmatch '(?m)^\s*max_framebuffers\s*=\s*[2-9][0-9]*(?:\s*(?:#.*)?)?$') {
    $block.Add("max_framebuffers=2")
}
$block.Add("include $FragmentName")
$block.Add($MarkerEnd)

$newConfig = $cleanConfig.TrimEnd("`r", "`n") + "`r`n`r`n" + ($block -join "`r`n") + "`r`n"
$fragmentContent = [IO.File]::ReadAllText($sourceFragment).Replace("`n", "`r`n").Replace("`r`r`n", "`r`n")

Write-Utf8File -Path $fragmentPath -Content $fragmentContent
Write-Utf8File -Path $configPath -Content $newConfig

Write-Host "MZP351HV00TR configuration installed successfully."
Write-Host "Boot partition: $bootRoot"
Write-Host "Backup: $backupPath"
Write-Host "Safely eject the SD card before removing it."
