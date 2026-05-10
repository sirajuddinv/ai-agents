#!pwsh
#Requires -Version 5.1
<#
.SYNOPSIS
    Read-only survey of JDK/JRE pins across an Eclipse PDE/Tycho workspace.

.DESCRIPTION
    Scans every .classpath, MANIFEST.MF, *.launch, and pom.xml under the
    given workspace root and reports:

      * .classpath  - JRE_CONTAINER pinned to a specific EE vs unpinned
      * MANIFEST.MF - Bundle-RequiredExecutionEnvironment value
      * *.launch    - JRE_CONTAINER (specific VM id vs EE) plus PermGen
                      JVM args and presence of --add-opens flags
      * pom.xml     - PermGen JVM args inside <argLine> entries

    The script is the discovery primitive for the `eclipse-pde-jdk-migration`
    skill (Phase 1). It is intentionally read-only - all remediation is
    surgical and agent-driven (see SKILL.md Phase 3) because every launch
    can carry user-customised VM arguments that a blind editor would clobber.

    Compatible with Windows PowerShell 5.1+ and PowerShell Core 7+.

.PARAMETER WorkspaceRoot
    Absolute path to the Eclipse workspace (or any directory tree containing
    PDE plug-ins). Defaults to the current working directory.

.PARAMETER TargetEE
    Target execution environment string (e.g., 'JavaSE-17'). Used only to
    classify launches as "already migrated" vs "needs migration". Defaults
    to 'JavaSE-17'.

.EXAMPLE
    pwsh-preview -File Survey-JrePins.ps1 -WorkspaceRoot 'C:\workspace\my-pde'

.EXAMPLE
    pwsh-preview -File Survey-JrePins.ps1 -WorkspaceRoot . -TargetEE JavaSE-21

.NOTES
    Author    : eclipse-pde-jdk-migration skill
    SSOT      : ../SKILL.md (Phase 1 - Reference Survey)
    Exit code : 0 on success regardless of findings; 1 only on script error.
    Common-Utils.ps1 is dot-sourced from the powershell-scripts submodule
    of ai-agent-rules. Bootstrap with:
        git submodule update --init --recursive ai-agent-rules/powershell-scripts
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string]$WorkspaceRoot = (Get-Location).Path,

    [Parameter(Mandatory = $false)]
    [string]$TargetEE = 'JavaSE-17'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# ---------------------------------------------------------------------------
# Portable anchored path resolution for Common-Utils.ps1
# ---------------------------------------------------------------------------
$ScriptDir   = Split-Path -Parent $MyInvocation.MyCommand.Path
$CommonUtils = Join-Path $ScriptDir '..\..\..\..\ai-agent-rules\powershell-scripts\Common-Utils.ps1'

if (Test-Path -LiteralPath $CommonUtils) {
    . (Resolve-Path -LiteralPath $CommonUtils).Path
} else {
    # Minimal stub so the script still runs if the submodule is not yet bootstrapped.
    function Write-Message {
        param([string]$Message, [string]$Color = 'White')
        if (-not [string]::IsNullOrWhiteSpace($Message)) {
            Write-Host $Message -ForegroundColor $Color
        }
    }
    Write-Message "Common-Utils.ps1 not found at expected location:" 'Yellow'
    Write-Message "  $CommonUtils"                                    'Yellow'
    Write-Message "Continuing with embedded Write-Message stub."      'Yellow'
}

# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------
if (-not (Test-Path -LiteralPath $WorkspaceRoot -PathType Container)) {
    Write-Message "WorkspaceRoot does not exist or is not a directory: $WorkspaceRoot" 'Red'
    exit 1
}
$WorkspaceRoot = (Resolve-Path -LiteralPath $WorkspaceRoot).Path
Write-Host ""
Write-Message "Eclipse PDE JDK Pin Survey"                                             'Cyan'
Write-Message "Workspace : $WorkspaceRoot"                                             'White'
Write-Message "Target EE : $TargetEE"                                                  'White'
Write-Host ""

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
function Get-RelativePath {
    param([string]$FullPath)
    $rel = $FullPath.Substring($WorkspaceRoot.Length).TrimStart('\', '/')
    if ([string]::IsNullOrWhiteSpace($rel)) { return $FullPath }
    return $rel
}

function Find-Files {
    param([string]$Filter)
    Get-ChildItem -LiteralPath $WorkspaceRoot -Recurse -Filter $Filter -File -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName -notmatch '\\(target|bin|\.git|node_modules)\\' }
}

# ---------------------------------------------------------------------------
# 1. .classpath survey
# ---------------------------------------------------------------------------
Write-Message "[.classpath] JRE_CONTAINER pins"                                        'Cyan'
$classpathPinned   = New-Object System.Collections.Generic.List[string]
$classpathUnpinned = New-Object System.Collections.Generic.List[string]

foreach ($cp in (Find-Files '.classpath')) {
    $line = Select-String -LiteralPath $cp.FullName -Pattern 'JRE_CONTAINER' -SimpleMatch | Select-Object -First 1
    if ($null -eq $line) { continue }
    $rel = Get-RelativePath $cp.FullName
    if ($line.Line -match 'JRE_CONTAINER/[^"]*StandardVMType/([^"]+)') {
        $classpathPinned.Add(("  PINNED  -> {0,-20}  {1}" -f $Matches[1], $rel))
    } else {
        $classpathUnpinned.Add(("  unpinned             {0}" -f $rel))
    }
}

if ($classpathPinned.Count -eq 0) {
    Write-Message "  (no pinned .classpath entries found)"                             'Green'
} else {
    foreach ($entry in $classpathPinned) { Write-Message $entry 'Yellow' }
}
Write-Message ("  total pinned   : {0}" -f $classpathPinned.Count)                     'White'
Write-Message ("  total unpinned : {0}" -f $classpathUnpinned.Count)                   'White'
Write-Host ""

# ---------------------------------------------------------------------------
# 2. MANIFEST.MF survey
# ---------------------------------------------------------------------------
Write-Message "[MANIFEST.MF] Bundle-RequiredExecutionEnvironment"                      'Cyan'
$manifestEEs = @{}
foreach ($mf in (Find-Files 'MANIFEST.MF')) {
    if ($mf.FullName -notmatch 'META-INF\\MANIFEST\.MF$') { continue }
    $hit = Select-String -LiteralPath $mf.FullName -Pattern '^Bundle-RequiredExecutionEnvironment:\s*(.+)$' | Select-Object -First 1
    if ($null -eq $hit) { continue }
    $ee = $hit.Matches[0].Groups[1].Value.Trim()
    if (-not $manifestEEs.ContainsKey($ee)) { $manifestEEs[$ee] = 0 }
    $manifestEEs[$ee]++
}
if ($manifestEEs.Count -eq 0) {
    Write-Message "  (no Bundle-RequiredExecutionEnvironment headers found)"           'Green'
} else {
    foreach ($k in ($manifestEEs.Keys | Sort-Object)) {
        Write-Message ("  {0,-20} -> {1} bundle(s)" -f $k, $manifestEEs[$k])           'Yellow'
    }
}
Write-Host ""

# ---------------------------------------------------------------------------
# 3. *.launch survey
# ---------------------------------------------------------------------------
Write-Message "[*.launch] JRE_CONTAINER + PermGen + --add-opens"                       'Cyan'
$launchHardcoded = New-Object System.Collections.Generic.List[string]
$launchEE        = New-Object System.Collections.Generic.List[string]
$launchOnTarget  = New-Object System.Collections.Generic.List[string]
$launchPermGen   = New-Object System.Collections.Generic.List[string]
$launchNoOpens   = New-Object System.Collections.Generic.List[string]

foreach ($lc in (Find-Files '*.launch')) {
    $rel = Get-RelativePath $lc.FullName
    $content = Get-Content -LiteralPath $lc.FullName -Raw

    if ($content -match 'JRE_CONTAINER/[^"]*StandardVMType/([^"]+)') {
        $jre = $Matches[1]
        if ($jre -eq $TargetEE) {
            $launchOnTarget.Add(("  on-target    {0,-15}  {1}" -f $jre, $rel))
        } elseif ($jre -match '^JavaSE-') {
            $launchEE.Add(("  EE-pinned    {0,-15}  {1}" -f $jre, $rel))
        } else {
            $launchHardcoded.Add(("  HARDCODED    {0,-15}  {1}" -f $jre, $rel))
        }
    }

    if ($content -match '-XX:(Max)?PermSize') {
        $launchPermGen.Add("  PermGen      $rel")
    }
    if ($content -match 'VM_ARGUMENTS' -and $content -notmatch '--add-opens') {
        $launchNoOpens.Add("  no-add-opens $rel")
    }
}

if ($launchHardcoded.Count -gt 0) {
    Write-Message "  Hard-coded VM ids (will break when JDK uninstalled):"             'Red'
    foreach ($entry in $launchHardcoded) { Write-Message $entry 'Red' }
}
if ($launchEE.Count -gt 0) {
    Write-Message "  EE-pinned (not yet on target ${TargetEE}):"                       'Yellow'
    foreach ($entry in $launchEE) { Write-Message $entry 'Yellow' }
}
if ($launchOnTarget.Count -gt 0) {
    Write-Message "  Already on target ${TargetEE}:"                                   'Green'
    foreach ($entry in $launchOnTarget) { Write-Message $entry 'Green' }
}
if ($launchPermGen.Count -gt 0) {
    Write-Host ""
    Write-Message "  Launches with obsolete PermGen JVM args:"                         'Red'
    foreach ($entry in $launchPermGen) { Write-Message $entry 'Red' }
}
if ($launchNoOpens.Count -gt 0) {
    Write-Host ""
    Write-Message "  Launches with VM_ARGUMENTS but NO --add-opens (may fail on JDK 9+):" 'Yellow'
    foreach ($entry in $launchNoOpens) { Write-Message $entry 'Yellow' }
}
Write-Host ""

# ---------------------------------------------------------------------------
# 4. pom.xml survey
# ---------------------------------------------------------------------------
Write-Message "[pom.xml] PermGen in <argLine>"                                         'Cyan'
$pomPermGen = New-Object System.Collections.Generic.List[string]
foreach ($pom in (Find-Files 'pom.xml')) {
    $hit = Select-String -LiteralPath $pom.FullName -Pattern '-XX:(Max)?PermSize'
    if ($null -ne $hit) {
        $rel = Get-RelativePath $pom.FullName
        $pomPermGen.Add(("  PermGen ({0} hit(s)) {1}" -f $hit.Count, $rel))
    }
}
if ($pomPermGen.Count -eq 0) {
    Write-Message "  (no PermGen flags in any pom.xml)"                                'Green'
} else {
    foreach ($entry in $pomPermGen) { Write-Message $entry 'Red' }
}
Write-Host ""

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
Write-Message "Summary"                                                                'Cyan'
Write-Message ("  .classpath pinned to old EE        : {0}" -f $classpathPinned.Count) 'White'
Write-Message ("  *.launch hard-coded VM ids         : {0}" -f $launchHardcoded.Count) 'White'
Write-Message ("  *.launch EE-pinned but not target  : {0}" -f $launchEE.Count)        'White'
Write-Message ("  *.launch with PermGen flags        : {0}" -f $launchPermGen.Count)   'White'
Write-Message ("  *.launch missing --add-opens       : {0}" -f $launchNoOpens.Count)   'White'
Write-Message ("  pom.xml with PermGen flags         : {0}" -f $pomPermGen.Count)      'White'
Write-Host ""

exit 0
