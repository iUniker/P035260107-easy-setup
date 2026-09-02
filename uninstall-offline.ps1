[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [string]$BootDrive
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
                (Test-Path (Join-Path $root $FragmentName))) {
                $root
            }
        }
    })

    if ($candidates.Count -eq 0) {
        throw "No mounted SD card with the managed display configuration was found. Pass its drive letter, for example: .\uninstall-offline.ps1 E:"
    }
    if ($candidates.Count -gt 1) {
        throw "More than one possible boot partition was found: $($candidates -join ', '). Pass the correct drive letter explicitly."
    }
    return $candidates[0]
}

$bootRoot = Resolve-BootRoot $BootDrive
$configPath = Join-Path $bootRoot "config.txt"
$fragmentPath = Join-Path $bootRoot $FragmentName
$config = [IO.File]::ReadAllText($configPath)
$managedPattern = "(?ms)^" + [Regex]::Escape($MarkerBegin) + "\r?\n.*?^" + [Regex]::Escape($MarkerEnd) + "\r?\n?"

if ($config -notmatch $managedPattern) {
    throw "The managed configuration block is absent or incomplete. No changes were made."
}

$cleanConfig = [Regex]::Replace($config, $managedPattern, "")
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss-fff"
$backupPath = "$configPath.backup-$timestamp"
Copy-Item -LiteralPath $configPath -Destination $backupPath

[IO.File]::WriteAllText($configPath, $cleanConfig, [Text.UTF8Encoding]::new($false))

if (Test-Path $fragmentPath) {
    $disabledPath = "$fragmentPath.disabled-$timestamp"
    Move-Item -LiteralPath $fragmentPath -Destination $disabledPath
    Write-Host "Configuration fragment preserved as: $disabledPath"
}

Write-Host "Managed MZP351HV00TR configuration removed."
Write-Host "Backup: $backupPath"
Write-Host "Safely eject the SD card before removing it."
