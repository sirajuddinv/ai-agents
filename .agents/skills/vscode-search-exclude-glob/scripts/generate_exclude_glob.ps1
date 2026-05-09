<#
.SYNOPSIS
    Convert a list of repository-relative paths into a single VS Code Search-view
    "files to exclude" brace-glob expression.

.DESCRIPTION
    Base primitive of the layered Search-Exclude skill family. Reads paths from either
    the pipeline or a file, normalizes them (trims whitespace, strips leading "./",
    drops blanks and comments), sorts and deduplicates them deterministically, and
    emits a single brace-glob line to stdout.

    Output forms:
        - Single entry, no glob metacharacter:  "path/**"
        - Multiple entries, all directories:    "{p1,p2,...,pN}/**"
        - Mixed (some entries already contain a glob metacharacter): "{p1,p2,...}"

    The script is fully cross-compatible with Windows PowerShell 5.1+ and PowerShell
    Core 7+. It writes nothing except the single result line on stdout; diagnostics go
    to stderr. The script does NOT modify any settings file — the user pastes the
    output into the Search view's "files to exclude" input.

    Per the project script management rules, this script dot-sources the shared
    `Common-Utils.ps1` from the `powershell-scripts` submodule of `ai-agent-rules`,
    using a path that is relative to the script's own location for portability across
    filesystems and platforms.

.PARAMETER Path
    Optional path to a text file containing one repository-relative path per line.
    When omitted, paths are read from the pipeline.

.PARAMETER InputObject
    Pipeline input. One string per path entry. Bound automatically when the script is
    invoked via the pipeline (e.g. `Get-Content .gitmodules | generate_exclude_glob`).

.EXAMPLE
    PS> 'dir_a','dir_b','dir_c' | ./generate_exclude_glob.ps1
    {dir_a,dir_b,dir_c}/**

.EXAMPLE
    PS> ./generate_exclude_glob.ps1 -Path paths.txt
    {dir_a,dir_b,dir_c}/**

.EXAMPLE
    PS> 'foo' | ./generate_exclude_glob.ps1
    foo/**

.NOTES
    Exit codes:
        0 - glob printed successfully
        1 - input file missing, or no usable paths in input
#>
[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [string]$Path,

    [Parameter(ValueFromPipeline = $true)]
    [string[]]$InputObject
)

begin {
    Set-StrictMode -Version Latest
    $ErrorActionPreference = 'Stop'

    # Dot-source the shared Common-Utils.ps1 via a path anchored to this script's
    # location, so the lookup is portable regardless of the caller's cwd. The shared
    # module lives in the `powershell-scripts` submodule of `ai-agent-rules`.
    $ScriptDir = Split-Path -Parent -Path $MyInvocation.MyCommand.Path
    $CommonUtilsPath = Join-Path -Path $ScriptDir -ChildPath '..\..\..\..\ai-agent-rules\powershell-scripts\Common-Utils.ps1'
    if (-not (Test-Path -LiteralPath $CommonUtilsPath -PathType Leaf)) {
        [Console]::Error.WriteLine("Common-Utils.ps1 not found at: $CommonUtilsPath")
        [Console]::Error.WriteLine('Initialize the powershell-scripts submodule under ai-agent-rules.')
        exit 1
    }
    . $CommonUtilsPath

    $collected = New-Object 'System.Collections.Generic.List[string]'
}

process {
    if ($null -ne $InputObject) {
        foreach ($item in $InputObject) {
            if ($null -ne $item) {
                $collected.Add([string]$item)
            }
        }
    }
}

end {
    # File input takes precedence and replaces any pipeline input.
    if (-not [string]::IsNullOrWhiteSpace($Path)) {
        if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
            $msg = "input file not found: $Path"
            if (-not [string]::IsNullOrWhiteSpace($msg)) {
                Write-Message -Message $msg -Color 'Red'
            }
            exit 1
        }
        $collected = New-Object 'System.Collections.Generic.List[string]'
        foreach ($line in (Get-Content -LiteralPath $Path)) {
            $collected.Add([string]$line)
        }
    }

    # Normalize: trim whitespace, strip leading "./" (or ".\"), drop blanks and comments.
    $normalized = New-Object 'System.Collections.Generic.List[string]'
    foreach ($raw in $collected) {
        if ($null -eq $raw) { continue }
        $line = $raw.Trim()
        if ([string]::IsNullOrWhiteSpace($line)) { continue }
        if ($line.StartsWith('#')) { continue }
        # Strip a leading "./" or ".\" prefix.
        if ($line -match '^\.[\\/]') {
            $line = $line -replace '^\.[\\/]+', ''
        }
        if ([string]::IsNullOrWhiteSpace($line)) { continue }
        $normalized.Add($line)
    }

    if ($normalized.Count -eq 0) {
        $msg = 'no paths provided'
        if (-not [string]::IsNullOrWhiteSpace($msg)) {
            Write-Message -Message $msg -Color 'Red'
        }
        exit 1
    }

    # Sort case-sensitively (ordinal-ish) and deduplicate. -CaseSensitive ensures
    # determinism across locales: PowerShell's default Sort-Object is culture-aware.
    $sorted = $normalized | Sort-Object -CaseSensitive -Unique

    # Append "/**" to plain directory entries; preserve entries that already contain a
    # glob metacharacter (* ? [ { ).
    $globRegex = '[*?\[\{]'
    $processed = New-Object 'System.Collections.Generic.List[string]'
    foreach ($entry in $sorted) {
        if ($entry -match $globRegex) {
            $processed.Add($entry)
        }
        else {
            $processed.Add("$entry/**")
        }
    }

    if ($processed.Count -eq 1) {
        # Single entry: emit literal glob without braces.
        Write-Output $processed[0]
        return
    }

    # If every entry ends with "/**", share one trailing "/**" across the brace group.
    $allRecursive = $true
    foreach ($entry in $processed) {
        if (-not $entry.EndsWith('/**')) {
            $allRecursive = $false
            break
        }
    }

    if ($allRecursive) {
        $stripped = foreach ($entry in $processed) {
            $entry.Substring(0, $entry.Length - 3)
        }
        Write-Output ('{' + ([string]::Join(',', $stripped)) + '}/**')
    }
    else {
        Write-Output ('{' + ([string]::Join(',', $processed)) + '}')
    }
}
