[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [string]$BootDrive,
    [switch]$Force,
    [switch]$Yes
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

function Confirm-BootRoot {
    param([string]$Root, [switch]$SkipPrompt)

    Write-Host "Selected Raspberry Pi boot partition: $Root"
    $driveRoot = [IO.Path]::GetPathRoot($Root).TrimEnd('\')
    try {
        $drive = Get-CimInstance Win32_LogicalDisk | Where-Object { $_.DeviceID -eq $driveRoot } | Select-Object -First 1
        if ($drive) {
            $sizeMb = if ($drive.Size) { [Math]::Round($drive.Size / 1MB) } else { "Unknown" }
            Write-Host "Drive: $($drive.DeviceID)  Label: $($drive.VolumeName)  Capacity: $sizeMb MB"
        }
    } catch {
        Write-Verbose "Drive metadata was unavailable: $($_.Exception.Message)"
    }

    if ($SkipPrompt) {
        return
    }

    $answer = Read-Host "Type INSTALL to modify this SD-card boot partition"
    if ($answer -cne "INSTALL") {
        throw "Installation cancelled. No changes were made."
    }
}

function Get-ConfigSources {
    param(
        [string]$Root,
        [string]$RootPath,
        [string]$RootContent
    )

    $sources = New-Object System.Collections.Generic.List[object]
    $queue = New-Object System.Collections.Generic.Queue[object]
    $seen = New-Object 'System.Collections.Generic.HashSet[string]' ([StringComparer]::OrdinalIgnoreCase)
    $rootPrefix = [IO.Path]::GetFullPath($Root).TrimEnd([char[]]@('\', '/')) + [IO.Path]::DirectorySeparatorChar
    $queue.Enqueue([PSCustomObject]@{ Path = [IO.Path]::GetFullPath($RootPath); Content = $RootContent })

    while ($queue.Count -gt 0) {
        if ($sources.Count -ge 32) {
            throw "More than 32 configuration files were included. Check for an include loop."
        }

        $source = $queue.Dequeue()
        if (-not $seen.Add($source.Path)) {
            continue
        }
        $sources.Add($source)

        $matches = [Regex]::Matches($source.Content, '(?m)^\s*include\s+([^#\s]+)')
        foreach ($match in $matches) {
            $includeName = $match.Groups[1].Value.TrimStart([char[]]@('\', '/'))
            $includePath = [IO.Path]::GetFullPath((Join-Path $Root $includeName))
            if (-not $includePath.StartsWith($rootPrefix, [StringComparison]::OrdinalIgnoreCase)) {
                throw "Included configuration escapes the boot partition: $includeName"
            }
            if (-not (Test-Path -LiteralPath $includePath -PathType Leaf)) {
                Write-Warning "Included configuration file was not found: $includeName"
                continue
            }
            $queue.Enqueue([PSCustomObject]@{
                Path = $includePath
                Content = [IO.File]::ReadAllText($includePath)
            })
        }
    }

    return $sources.ToArray()
}

function Get-LastConfigValue {
    param([object[]]$Sources, [string]$Name)
    $result = $null
    $pattern = '(?m)^\s*' + [Regex]::Escape($Name) + '\s*=\s*([^#\r\n]+)'
    foreach ($source in $Sources) {
        foreach ($match in [Regex]::Matches($source.Content, $pattern)) {
            $result = $match.Groups[1].Value.Trim()
        }
    }
    return $result
}

function Test-EffectiveSetting {
    param([object[]]$Sources, [string]$Pattern)

    foreach ($source in $Sources) {
        $applies = $true
        foreach ($line in ($source.Content -split "\r?\n")) {
            $lower = $line.ToLowerInvariant()
            if ($lower -match '^\s*\[([^]]+)\]\s*$') {
                $tag = $Matches[1]
                if ($tag -in @('all', 'pi0', 'pi0w', 'pi02')) {
                    $applies = $true
                } elseif ($tag -eq 'none' -or $tag -match '^(pi[1-9]|pi3\+|pi400|pi500|cm0|cm1|cm3|cm3\+|cm4|cm4s|cm5)$') {
                    $applies = $false
                } else {
                    # Unknown runtime filters are treated as possibly active.
                    $applies = $true
                }
                continue
            }
            if ($applies -and $lower -match $Pattern) {
                return $true
            }
        }
    }
    return $false
}

$bootRoot = Resolve-BootRoot $BootDrive
$configPath = Join-Path $bootRoot "config.txt"
$fragmentPath = Join-Path $bootRoot $FragmentName
$sourceFragment = Join-Path $PSScriptRoot "config\mzp351hv00tr-kms.txt"

if (-not (Test-Path $sourceFragment)) {
    throw "Configuration template not found: $sourceFragment"
}

Confirm-BootRoot -Root $bootRoot -SkipPrompt:$Yes

$config = [IO.File]::ReadAllText($configPath)
$managedPattern = "(?ms)^" + [Regex]::Escape($MarkerBegin) + "\r?\n.*?^" + [Regex]::Escape($MarkerEnd) + "\r?\n?"
$cleanConfig = [Regex]::Replace($config, $managedPattern, "")
$configSources = @(Get-ConfigSources -Root $bootRoot -RootPath $configPath -RootContent $cleanConfig)

foreach ($source in $configSources) {
    if ($source.Content -match '(?m)^\s*include\s+mzp351hv00tr-(new|old)\.txt(?:\s|$)') {
        throw "The original mzp351hv00tr-new/old configuration is already included by $($source.Path). If the display works, no migration is required."
    }
    $conflictPattern = '(?m)^\s*(dtoverlay=vc4-(?:f)?kms-dpi-|dtoverlay=vc4-fkms-v3d(?:[,\s]|$)|dtoverlay=ads7846(?:[,\s]|$)|dtoverlay=spi0-0cs(?:[,\s]|$)|enable_dpi_lcd=1|dpi_(?:group|mode|output_format|timings)=|display_default_lcd=1)'
    if ($source.Content -match $conflictPattern) {
        throw "A conflicting display, FKMS, DPI, SPI0, or ADS7846 configuration was found in $($source.Path). No changes were made."
    }
}

$overlayPrefix = Get-LastConfigValue -Sources $configSources -Name "overlay_prefix"
if (-not $overlayPrefix) { $overlayPrefix = "overlays/" }
$osPrefix = Get-LastConfigValue -Sources $configSources -Name "os_prefix"
if (-not $osPrefix) { $osPrefix = "" }
$relativeOverlay = ($osPrefix + $overlayPrefix).TrimStart([char[]]@('\', '/')).Replace('/', [IO.Path]::DirectorySeparatorChar)
$overlayCandidates = @(
    (Join-Path $bootRoot $relativeOverlay),
    (Join-Path $bootRoot $overlayPrefix.TrimStart([char[]]@('\', '/'))),
    (Join-Path $bootRoot "overlays")
) | Select-Object -Unique
$requiredOverlays = @("spi0-0cs.dtbo", "ads7846.dtbo", "vc4-kms-dpi-generic.dtbo")
$overlayRoot = $overlayCandidates | Where-Object {
    $candidate = $_
    ($requiredOverlays | Where-Object { -not (Test-Path (Join-Path $candidate $_)) }).Count -eq 0
} | Select-Object -First 1

if (-not $overlayRoot -and -not $Force) {
    throw "Required overlay files were not found in the configured overlay directories. Use a current OS/firmware image."
}
if (-not $overlayRoot) {
    Write-Warning "Required overlay files could not be verified."
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
if (-not (Test-EffectiveSetting -Sources $configSources -Pattern '^\s*dtoverlay=vc4-kms-v3d(?:[,\s]|$)')) {
    $block.Add("dtoverlay=vc4-kms-v3d")
}
if (-not (Test-EffectiveSetting -Sources $configSources -Pattern '^\s*max_framebuffers\s*=\s*[2-9][0-9]*(?:\s*(?:#.*)?)?$')) {
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
