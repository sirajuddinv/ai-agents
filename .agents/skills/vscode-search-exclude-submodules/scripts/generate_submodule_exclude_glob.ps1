<#
.SYNOPSIS
    Generate a VS Code Search-view "files to exclude" brace-glob that excludes every
    Git submodule registered in the parent repository's .gitmodules.

.DESCRIPTION
    Composer script for the layered Search-Exclude skill family. Reads .gitmodules in
    the current directory, extracts every `path = ...` entry, and pipes the resulting
    list into the base Search-Exclude-Glob script which performs sorting, deduplication,
    and brace-glob assembly. Emits a single line of the form
    "{submodule_a,submodule_b,...,submodule_z}/**" on stdout.

    Cross-compatible with Windows PowerShell 5.1+ and PowerShell Core 7+. The script
    does NOT modify any settings file or .gitignore — the user pastes the output into
    the Search view's "files to exclude" input.

    Per the project script management rules, this script dot-sources the shared
    `Common-Utils.ps1` from the `powershell-scripts` submodule of `ai-agent-rules`
    (used for `Write-Message` diagnostics) and delegates all glob-assembly to the base
    script — inlining is forbidden by the Layered Composition Mandate.

.PARAMETER GitmodulesPath
    Optional explicit path to a .gitmodules file. Defaults to ".gitmodules" in the
    current working directory.

.EXAMPLE
    PS> Set-Location <parent-repo-root>
    PS> ./generate_submodule_exclude_glob.ps1
    {ai-agent-rules,anthropics_skills,...,zxkane_aws-skills}/**

.EXAMPLE
    PS> ./generate_submodule_exclude_glob.ps1 -GitmodulesPath ../other-repo/.gitmodules
    {sub_a,sub_b}/**

.NOTES
    Exit codes:
        0 - glob printed successfully
        1 - .gitmodules missing, base script missing, or no submodule paths found
#>
[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [string]$GitmodulesPath = '.gitmodules'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# Resolve this script's directory once — used for both the Common-Utils dot-source and
# the base script lookup. Anchored to $MyInvocation so the script works regardless of
# the caller's cwd.
$ScriptDir = Split-Path -Parent -Path $MyInvocation.MyCommand.Path

# Dot-source the shared Common-Utils.ps1 from the `powershell-scripts` submodule of
# `ai-agent-rules`.
$CommonUtilsPath = Join-Path -Path $ScriptDir -ChildPath '..\..\..\..\ai-agent-rules\powershell-scripts\Common-Utils.ps1'
if (-not (Test-Path -LiteralPath $CommonUtilsPath -PathType Leaf)) {
    [Console]::Error.WriteLine("Common-Utils.ps1 not found at: $CommonUtilsPath")
    [Console]::Error.WriteLine('Initialize the powershell-scripts submodule under ai-agent-rules.')
    exit 1
}
. $CommonUtilsPath

# Resolve the base skill script relative to this composer's location, so the pipeline
# works regardless of the caller's current working directory.
$BaseScript = Join-Path -Path $ScriptDir -ChildPath '..\..\vscode-search-exclude-glob\scripts\generate_exclude_glob.ps1'
# Normalize the path (collapse ".." segments) for diagnostic clarity.
try {
    $BaseScript = (Resolve-Path -LiteralPath $BaseScript -ErrorAction Stop).ProviderPath
}
catch {
    $msg = "base skill script missing: $BaseScript"
    if (-not [string]::IsNullOrWhiteSpace($msg)) {
        Write-Message -Message $msg -Color 'Red'
    }
    exit 1
}

if (-not (Test-Path -LiteralPath $GitmodulesPath -PathType Leaf)) {
    $msg = "no .gitmodules found at: $GitmodulesPath"
    if (-not [string]::IsNullOrWhiteSpace($msg)) {
        Write-Message -Message $msg -Color 'Red'
    }
    exit 1
}

# Extract every `path = ...` line and strip the prefix. The base script handles sort,
# dedupe, and brace-glob assembly.
$pathRegex = '^\s*path\s*=\s*(.+?)\s*$'
$paths = New-Object 'System.Collections.Generic.List[string]'
foreach ($line in (Get-Content -LiteralPath $GitmodulesPath)) {
    if ($line -match $pathRegex) {
        $paths.Add($Matches[1])
    }
}

if ($paths.Count -eq 0) {
    $msg = 'no submodule paths found in .gitmodules'
    if (-not [string]::IsNullOrWhiteSpace($msg)) {
        Write-Message -Message $msg -Color 'Red'
    }
    exit 1
}

# Pipe into the base script. Capture exit code so failure propagates. $LASTEXITCODE
# is only set when the called script (or a native command) explicitly exits with a
# non-zero code, so guard the access under Set-StrictMode.
$paths | & $BaseScript
if (Test-Path -LiteralPath 'Variable:LASTEXITCODE') {
    exit $LASTEXITCODE
}
exit 0
