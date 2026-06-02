<#
.SYNOPSIS
    Extract an archive with 7-Zip (progress-only output) and verify the
    extracted footprint matches the pre-flight report.

.DESCRIPTION
    Phase 3 + Phase 4 of the `archive-size-preflight-and-extract` skill
    (SKILL.md in this directory).

    Defaults the output directory to a fresh sibling folder of the archive
    named after the archive basename (without extension), so the extracted
    contents never pollute `$PWD`.

    Internally invokes:
        7z x <archive> -o<output-dir> -bso0 -bsp1 -y

    Then walks the output folder and confirms:
        - File count matches Get-ArchiveSizeReport's `FileCount`
        - Folder count matches `FolderCount`
        - Sum of file sizes matches `UncompressedBytes`

    Any mismatch is a HARD FAIL (exit 1 + diagnostic).

.PARAMETER ArchivePath
    Path to the archive to extract.

.PARAMETER OutputDir
    Optional output directory. Default: <archive-parent>\<archive-basename-without-ext>.

.PARAMETER Force
    Overwrite an existing OutputDir without prompting.

.OUTPUTS
    [PSCustomObject] with verification verdict.

.NOTES
    Does NOT dot-source `Common-Utils.ps1` — exempted because this skill is a
    leaf utility and the powershell-scripts submodule is not always present in
    consumer repos. The script is fully self-contained.
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string] $ArchivePath,

    [Parameter(Position = 1)]
    [string] $OutputDir,

    [switch] $Force
)

$ErrorActionPreference = 'Stop'

# --- Phase 1+2: pre-flight via sibling script --------------------------------
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$reportScript = Join-Path $here 'Get-ArchiveSizeReport.ps1'
if (-not (Test-Path -LiteralPath $reportScript)) {
    throw "Sibling script not found: $reportScript"
}
$report = & $reportScript -ArchivePath $ArchivePath

# --- Resolve OutputDir --------------------------------------------------------
if (-not $OutputDir) {
    $archiveItem = Get-Item -LiteralPath $report.ArchivePath
    $baseName = [System.IO.Path]::GetFileNameWithoutExtension($archiveItem.Name)
    # Strip a second extension layer for double-suffix archives (e.g. .tar.gz).
    if ($baseName -match '\.tar$') { $baseName = $baseName -replace '\.tar$', '' }
    $OutputDir = Join-Path $archiveItem.DirectoryName $baseName
}

if (Test-Path -LiteralPath $OutputDir) {
    if (-not $Force) {
        throw "OutputDir already exists: $OutputDir (pass -Force to overwrite contents)"
    }
}
else {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}

# --- Phase 3: extract ---------------------------------------------------------
Write-Host "Extracting:  $($report.ArchivePath)"
Write-Host "         ->  $OutputDir"
Write-Host "Pre-flight:  $($report.UncompressedBytes) bytes / $($report.FileCount) files / $($report.FolderCount) folders"
if ($report.ClusterOverheadWarning) {
    Write-Host "WARNING:     FileCount > 10000 — NTFS 4 KiB cluster overhead may push on-disk usage above the pre-flight uncompressed total." -ForegroundColor Yellow
}
Write-Host ''

& $report.SevenZipPath x $report.ArchivePath "-o$OutputDir" -bso0 -bsp1 -y
$extractExit = $LASTEXITCODE
if ($extractExit -ne 0) {
    throw "7z extraction failed (exit $extractExit)."
}

# --- Phase 4: verification ----------------------------------------------------
$entries = Get-ChildItem -LiteralPath $OutputDir -Recurse -Force
$actualFiles = @($entries | Where-Object { -not $_.PSIsContainer })
$actualFolders = @($entries | Where-Object { $_.PSIsContainer })
$actualBytes = ($actualFiles | Measure-Object -Property Length -Sum).Sum
if ($null -eq $actualBytes) { $actualBytes = 0 }

$mismatches = @()
if ($actualFiles.Count -ne $report.FileCount) {
    $mismatches += "FileCount: extracted=$($actualFiles.Count) expected=$($report.FileCount)"
}
if ($actualFolders.Count -ne $report.FolderCount) {
    $mismatches += "FolderCount: extracted=$($actualFolders.Count) expected=$($report.FolderCount)"
}
if ([long]$actualBytes -ne [long]$report.UncompressedBytes) {
    $mismatches += "UncompressedBytes: extracted=$actualBytes expected=$($report.UncompressedBytes)"
}

$verdict = if ($mismatches.Count -eq 0) { 'PASS' } else { 'FAIL' }

$result = [PSCustomObject]@{
    ArchivePath          = $report.ArchivePath
    OutputDir            = (Resolve-Path -LiteralPath $OutputDir).ProviderPath
    CompressedBytes      = $report.CompressedBytes
    CompressedMB         = $report.CompressedMB
    UncompressedBytes    = $report.UncompressedBytes
    UncompressedMB       = $report.UncompressedMB
    UncompressedGB       = $report.UncompressedGB
    FileCount            = $report.FileCount
    FolderCount          = $report.FolderCount
    Ratio                = $report.Ratio
    ExtractedFileCount   = $actualFiles.Count
    ExtractedFolderCount = $actualFolders.Count
    ExtractedBytes       = [long]$actualBytes
    Verdict              = $verdict
    Mismatches           = $mismatches
}

# --- Emit verdict table -------------------------------------------------------
Write-Host ''
Write-Host '--- Verdict ---' -ForegroundColor Cyan
$result | Format-List ArchivePath, OutputDir, CompressedMB, UncompressedMB, UncompressedGB, FileCount, FolderCount, Ratio, Verdict | Out-Host

if ($verdict -eq 'FAIL') {
    Write-Host 'Mismatches:' -ForegroundColor Red
    $mismatches | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
    $result
    exit 1
}

$result
