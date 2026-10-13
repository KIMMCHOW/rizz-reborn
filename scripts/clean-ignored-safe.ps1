#Requires -Version 7.0
<#
.SYNOPSIS
  Whitelist-based cleanup of git-ignored build output and caches in this repository.

.DESCRIPTION
  Never uses `git clean`. A path is only considered when all of the following hold:
    1. it resolves inside the repository root,
    2. Git reports it as ignored (git status --porcelain --ignored),
    3. Git reports no tracked files below it.
  Protected data (local_data/, local_outputs/, .env*) is not in the whitelist and is
  never touched, including nested caches below it. Release artifacts and dependency
  installs are protected candidates: they are only removed with an explicit opt-in
  switch.

.PARAMETER Apply
  Delete the whitelisted paths. Without this switch the script only reports them.

.PARAMETER IncludeRelease
  Also remove vendor/WeFlow/release (packaged installers and the win-unpacked app).
  Only pass this when you can rebuild or re-download the package.

.PARAMETER IncludeNodeModules
  Also remove vendor/WeFlow/node_modules. Regenerate it with `npm ci` inside
  vendor/WeFlow (requires network access).

.EXAMPLE
  pwsh -File scripts/clean-ignored-safe.ps1

.EXAMPLE
  pwsh -File scripts/clean-ignored-safe.ps1 -Apply
#>
[CmdletBinding()]
param(
    [switch]$Apply,
    [switch]$IncludeRelease,
    [switch]$IncludeNodeModules
)

$ErrorActionPreference = 'Stop'

if ($PSVersionTable.PSVersion.Major -lt 7) {
    throw 'PowerShell 7 or newer is required.'
}

$RepoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$Separator = [IO.Path]::DirectorySeparatorChar

function ConvertTo-RelativePath {
    param([Parameter(Mandatory)][string]$FullPath)
    return ($FullPath.Substring($RepoRoot.Length).TrimStart('\', '/') -replace '\\', '/')
}

function Get-PathSize {
    param([Parameter(Mandatory)][string]$FullPath)
    $files = Get-ChildItem -LiteralPath $FullPath -Recurse -File -Force -ErrorAction SilentlyContinue
    return [pscustomobject]@{
        Files = @($files).Count
        Bytes = [long](($files | Measure-Object -Property Length -Sum).Sum)
    }
}

$candidates = [System.Collections.Generic.List[object]]::new()

foreach ($rel in @(
        '.pytest_cache',
        '__pycache__',
        'tests/__pycache__',
        'tools/__pycache__',
        'src/simp_project/__pycache__'
    )) {
    $candidates.Add([pscustomobject]@{ Rel = $rel; Tier = 'cache' })
}

foreach ($rel in @('vendor/WeFlow/dist', 'vendor/WeFlow/dist-electron')) {
    $candidates.Add([pscustomobject]@{ Rel = $rel; Tier = 'build' })
}

if ($IncludeRelease) {
    $candidates.Add([pscustomobject]@{ Rel = 'vendor/WeFlow/release'; Tier = 'release' })
}

if ($IncludeNodeModules) {
    $candidates.Add([pscustomobject]@{ Rel = 'vendor/WeFlow/node_modules'; Tier = 'deps' })
}

# Discover any additional Python bytecode caches, but never inside node_modules or
# the private data roots.
$protectedPrefixes = @('local_data/', 'local_outputs/')
$known = @($candidates | ForEach-Object { $_.Rel })
Get-ChildItem -LiteralPath $RepoRoot -Recurse -Directory -Filter '__pycache__' -Force -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -notmatch '\\node_modules\\' } |
    ForEach-Object {
        $rel = ConvertTo-RelativePath -FullPath $_.FullName
        if ($protectedPrefixes | Where-Object { $rel.StartsWith($_, [StringComparison]::OrdinalIgnoreCase) }) {
            return
        }
        if ($known -notcontains $rel) {
            $known += $rel
            $candidates.Add([pscustomobject]@{ Rel = $rel; Tier = 'cache' })
        }
    }

$results = [System.Collections.Generic.List[object]]::new()
$protected = [System.Collections.Generic.List[object]]::new()

foreach ($candidate in $candidates) {
    $full = Join-Path $RepoRoot $candidate.Rel
    if (-not (Test-Path -LiteralPath $full)) { continue }

    $resolved = (Resolve-Path -LiteralPath $full).Path
    $inside = $resolved.StartsWith("$RepoRoot$Separator", [StringComparison]::OrdinalIgnoreCase)

    $ignoredLines = @(git -C $RepoRoot status --porcelain --ignored -- $candidate.Rel 2>$null)
    $isIgnored = $ignoredLines.Count -gt 0 -and $ignoredLines[0].StartsWith('!! ')

    $trackedLines = @(git -C $RepoRoot ls-files -- $candidate.Rel)
    $trackedCount = $trackedLines.Count

    if (-not $inside -or -not $isIgnored -or $trackedCount -gt 0) {
        $protected.Add([pscustomobject]@{
                Rel    = $candidate.Rel
                Reason = "guard: inside=$inside ignored=$isIgnored tracked=$trackedCount"
            })
        continue
    }

    $size = Get-PathSize -FullPath $resolved
    $results.Add([pscustomobject]@{
            Rel   = $candidate.Rel
            Tier  = $candidate.Tier
            Files = $size.Files
            MB    = [math]::Round($size.Bytes / 1MB, 1)
            Full  = $resolved
        })
}

$mode = if ($Apply) { 'APPLY' } else { 'DRY RUN' }
Write-Output "clean-ignored-safe ($mode) root=$RepoRoot"
Write-Output ''

if ($results.Count -eq 0) {
    Write-Output 'Nothing to do.'
}
else {
    $results | Sort-Object Tier, Rel | Format-Table -AutoSize Rel, Tier, Files, MB | Out-String | Write-Output
}

if ($Apply) {
    $freed = 0
    foreach ($item in $results) {
        Remove-Item -LiteralPath $item.Full -Recurse -Force
        $freed += [math]::Round($item.MB, 1)
        Write-Output "removed: $($item.Rel)"
    }
    Write-Output ''
    Write-Output ("removed {0} path(s), about {1} MB" -f $results.Count, [math]::Round($freed, 1))
}
else {
    $totalMB = [math]::Round((($results | Measure-Object -Property MB -Sum).Sum), 1)
    Write-Output ''
    Write-Output ("would remove {0} path(s), about {1} MB. Re-run with -Apply to delete." -f $results.Count, $totalMB)
}

if ($protected.Count -gt 0) {
    Write-Output ''
    Write-Output 'skipped by guard:'
    $protected | Sort-Object Rel | Format-Table -AutoSize Rel, Reason | Out-String | Write-Output
}

if (-not $IncludeRelease) {
    $release = Join-Path $RepoRoot 'vendor/WeFlow/release'
    if (Test-Path -LiteralPath $release) {
        $size = Get-PathSize -FullPath $release
        Write-Output ("protected candidate (use -IncludeRelease): vendor/WeFlow/release {0} files, {1} MB" -f $size.Files, [math]::Round($size.Bytes / 1MB, 1))
    }
}

if (-not $IncludeNodeModules) {
    $modules = Join-Path $RepoRoot 'vendor/WeFlow/node_modules'
    if (Test-Path -LiteralPath $modules) {
        $size = Get-PathSize -FullPath $modules
        Write-Output ("protected candidate (use -IncludeNodeModules): vendor/WeFlow/node_modules {0} files, {1} MB" -f $size.Files, [math]::Round($size.Bytes / 1MB, 1))
    }
}
