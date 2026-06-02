<#
.SYNOPSIS
    Pre-flight an archive (zip / 7z / tar / tar.gz / ...) with 7-Zip and report
    compressed-on-disk size, uncompressed total, file count, folder count, and
    compression ratio without extracting.

.DESCRIPTION
    Phase 1 + Phase 2 of the `archive-size-preflight-and-extract` skill
    (SKILL.md in this directory).

    Resolves 7-Zip via PATH first, then the two canonical install roots:
      - C:\Program Files\7-Zip\7z.exe
      - C:\Program Files (x86)\7-Zip\7z.exe

    Parses the summary line emitted by `7z l <archive>` (always the last line
    before the trailing blank line) into a PSCustomObject.

.PARAMETER ArchivePath
    Path to the archive to inspect. Accepts relative or absolute paths.

.OUTPUTS
    [PSCustomObject] with the following properties:
        ArchivePath, CompressedBytes, UncompressedBytes, FileCount, FolderCount,
        Ratio, CompressedMB, CompressedGB, UncompressedMB, UncompressedGB,
        ClusterOverheadWarning (Boolean — true when FileCount > 10000)

.EXAMPLE
    PS> .\Get-ArchiveSizeReport.ps1 -ArchivePath .\example.zip
    ArchivePath           : C:\work\example.zip
    CompressedBytes       : 663679369
    UncompressedBytes     : 2785183062
    FileCount             : 34053
    FolderCount           : 1843
    Ratio                 : 4.2
    UncompressedGB        : 2.59
    ClusterOverheadWarning: True

.NOTES
    Does NOT dot-source `Common-Utils.ps1` — exempted because this skill is a
    leaf utility and the powershell-scripts submodule is not always present in
    consumer repos. The script is fully self-contained.
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string] $ArchivePath
)

$ErrorActionPreference = 'Stop'

# --- Resolve archive path -----------------------------------------------------
$resolved = (Resolve-Path -LiteralPath $ArchivePath).ProviderPath
$fi = Get-Item -LiteralPath $resolved
if ($fi.PSIsContainer) {
    throw "ArchivePath is a directory, not a file: $resolved"
}

# --- Resolve 7z.exe -----------------------------------------------------------
$candidates = @(
    'C:\Program Files\7-Zip\7z.exe',
    'C:\Program Files (x86)\7-Zip\7z.exe'
)
$sevenZip = $null
$onPath = Get-Command 7z.exe, 7z -ErrorAction SilentlyContinue | Select-Object -First 1
if ($onPath) { $sevenZip = $onPath.Source }
else {
    foreach ($c in $candidates) {
        if (Test-Path -LiteralPath $c) { $sevenZip = $c; break }
    }
}
if (-not $sevenZip) {
    throw "7-Zip not found on PATH or under '$($candidates -join ''', ''')'. Install via: winget install 7zip.7zip"
}

# --- Run `7z l` and capture stdout -------------------------------------------
$listing = & $sevenZip l -slt:off $resolved 2>&1
if ($LASTEXITCODE -ne 0) {
    throw "7z list failed (exit $LASTEXITCODE):`n$($listing -join [Environment]::NewLine)"
}

# --- Parse the summary line ---------------------------------------------------
# Expected format (last non-blank line):
#   <date> <time>        <uncompressed>     <compressed>  <N> files[, <M> folders]
# `folders` segment is absent for archives that contain only files.
$lines = $listing | Where-Object { $_ -is [string] -and $_.Trim().Length -gt 0 }
$summary = $lines[-1]

$rxBoth = '^\s*\S+\s+\S+\s+(?<unc>\d+)\s+(?<cmp>\d+)\s+(?<files>\d+)\s+files,\s+(?<folders>\d+)\s+folders?\s*$'
$rxFilesOnly = '^\s*\S+\s+\S+\s+(?<unc>\d+)\s+(?<cmp>\d+)\s+(?<files>\d+)\s+files?\s*$'

$uncompressed = $null; $files = 0; $folders = 0
if ($summary -match $rxBoth) {
    $uncompressed = [long]$Matches['unc']
    $files = [int]$Matches['files']
    $folders = [int]$Matches['folders']
}
elseif ($summary -match $rxFilesOnly) {
    $uncompressed = [long]$Matches['unc']
    $files = [int]$Matches['files']
    $folders = 0
}
else {
    throw "Unable to parse 7z summary line: '$summary'"
}

# --- Emit report --------------------------------------------------------------
$compressed = [long]$fi.Length
$ratio = if ($compressed -gt 0) { [math]::Round($uncompressed / $compressed, 2) } else { 0 }

[PSCustomObject]@{
    ArchivePath            = $resolved
    CompressedBytes        = $compressed
    UncompressedBytes      = $uncompressed
    FileCount              = $files
    FolderCount            = $folders
    Ratio                  = $ratio
    CompressedMB           = [math]::Round($compressed / 1MB, 2)
    CompressedGB           = [math]::Round($compressed / 1GB, 2)
    UncompressedMB         = [math]::Round($uncompressed / 1MB, 2)
    UncompressedGB         = [math]::Round($uncompressed / 1GB, 2)
    ClusterOverheadWarning = ($files -gt 10000)
    SevenZipPath           = $sevenZip
}
