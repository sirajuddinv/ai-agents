<#
.SYNOPSIS
    Collect a set of files listed in a plain-text manifest and package them
    into a single flat, timestamped zip archive.

.DESCRIPTION
    Reads a manifest file containing one relative path per line (blank lines
    and lines beginning with '#' are ignored), resolves each path against a
    root directory, copies every existing file into a flat staging area
    (no sub-directories), and compresses the staging area into a timestamped
    zip. Files that share a leaf name are auto-suffixed '_1', '_2', ... so no
    file is silently overwritten. Paths listed in the manifest that do not
    exist on disk are reported as missing but do not abort the run.

    The tool is intentionally self-contained: it has NO external module
    dependencies so it can be dropped into an arbitrary directory tree and
    run with nothing but a stock PowerShell 5.1+ runtime.

.PARAMETER Root
    The directory that manifest-relative paths are resolved against.
    Defaults to the PARENT of the directory this script lives in, which makes
    the common "drop a tool sub-folder into a project root and run it from
    there" deployment work with zero configuration.

.PARAMETER Manifest
    The manifest file to read. Defaults to a file named '<ScriptBaseName>.txt'
    sitting next to this script (e.g. Collect-ManifestFiles.txt).

.PARAMETER OutputDir
    Directory the resulting zip is written to. Defaults to the directory this
    script lives in.

.PARAMETER NamePrefix
    Prefix for the generated zip name. Defaults to the leaf name of -Root.
    Final name is '<NamePrefix>_<yyyyMMdd_HHmmss>.zip'.

.EXAMPLE
    .\Collect-ManifestFiles.ps1
    Resolve paths against the parent folder, read Collect-ManifestFiles.txt,
    write <parentLeaf>_<timestamp>.zip next to the script.

.EXAMPLE
    .\Collect-ManifestFiles.ps1 -Root 'C:\builds\projX' -Manifest .\pick.txt -NamePrefix projX_logs
    Collect the files listed in pick.txt relative to C:\builds\projX.

.NOTES
    Language tier: Tier 2 (PowerShell) per scripting-language-selection-rules
    section 4 -- the body IS shell glue around the Compress-Archive cmdlet and
    the deliverable is a self-contained tool dropped into an arbitrary tree.

    Common-Utils.ps1 dot-source is intentionally OMITTED: this tool's defining
    design constraint is zero external dependencies so it remains portable to
    any host where only stock PowerShell 5.1 is available. (skill-factory
    section 2.2.1.2 item 3 exemption.)

    ASCII-only source: the file MUST contain no characters above code point
    127 (no box-drawing glyphs, no em-dashes). PowerShell 5.1 reads a
    BOM-less UTF-8 file as the system ANSI code page and mis-tokenizes any
    non-ASCII byte, producing "string is missing the terminator" errors.

    Requires PowerShell 5.0+ for Compress-Archive.
#>

[CmdletBinding()]
param(
    [string] $Root,
    [string] $Manifest,
    [string] $OutputDir,
    [string] $NamePrefix
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# -- Resolve paths -------------------------------------------------------
$toolDir = Split-Path -Parent $MyInvocation.MyCommand.Definition

if (-not $Root) {
    $Root = Split-Path -Parent $toolDir
}
if (-not $Manifest) {
    $scriptBase = [System.IO.Path]::GetFileNameWithoutExtension($MyInvocation.MyCommand.Name)
    $Manifest   = Join-Path $toolDir "$scriptBase.txt"
}
if (-not $OutputDir) {
    $OutputDir = $toolDir
}
if (-not $NamePrefix) {
    $NamePrefix = Split-Path -Leaf $Root
}

$timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$zipName   = "${NamePrefix}_${timestamp}.zip"
$zipPath   = Join-Path $OutputDir $zipName

# -- Validate manifest ---------------------------------------------------
if (-not (Test-Path $Manifest)) {
    Write-Error "Manifest file not found: $Manifest"
    exit 1
}

$lines = Get-Content $Manifest |
         ForEach-Object { $_.Trim() } |
         Where-Object  { $_ -ne '' -and -not $_.StartsWith('#') }

if ($lines.Count -eq 0) {
    Write-Error "Manifest '$Manifest' contains no file entries."
    exit 1
}

# -- Stage files (flat - all files in staging root) ----------------------
$stagingDir = Join-Path $env:TEMP "ManifestCollect_${timestamp}"
New-Item -ItemType Directory -Path $stagingDir -Force | Out-Null

$collected = 0
$missing   = 0
$missingPaths = @()

foreach ($relPath in $lines) {
    $srcFull  = Join-Path $Root $relPath
    $fileName = Split-Path -Leaf $srcFull

    if (-not (Test-Path $srcFull)) {
        Write-Warning "File not found (skipped): $relPath"
        $missing++
        $missingPaths += $relPath
        continue
    }

    $destFull = Join-Path $stagingDir $fileName
    if (Test-Path $destFull) {
        $baseName = [System.IO.Path]::GetFileNameWithoutExtension($fileName)
        $ext      = [System.IO.Path]::GetExtension($fileName)
        $counter  = 1
        do {
            $destFull = Join-Path $stagingDir "${baseName}_${counter}${ext}"
            $counter++
        } while (Test-Path $destFull)
        Write-Warning "Duplicate name '$fileName' - saved as $(Split-Path -Leaf $destFull)"
    }

    Copy-Item -Path $srcFull -Destination $destFull -Force
    Write-Host "  [+] $relPath"
    $collected++
}

# -- Create zip ----------------------------------------------------------
if ($collected -eq 0) {
    Write-Error "No files were collected - zip not created."
    Remove-Item $stagingDir -Recurse -Force
    exit 1
}

if (Test-Path $zipPath) { Remove-Item $zipPath -Force }
Compress-Archive -Path (Join-Path $stagingDir '*') -DestinationPath $zipPath -Force

# -- Cleanup and summary -------------------------------------------------
Remove-Item $stagingDir -Recurse -Force

Write-Host ""
Write-Host "===== Manifest Collection Summary ====="
Write-Host "  Root      : $Root"
Write-Host "  Collected : $collected file(s)"
Write-Host "  Missing   : $missing file(s)"
Write-Host "  Output    : $zipPath"
Write-Host "======================================="

if ($missing -gt 0) {
    Write-Host ""
    Write-Host "Missing paths:"
    foreach ($mp in $missingPaths) { Write-Host "  [-] $mp" }
}
