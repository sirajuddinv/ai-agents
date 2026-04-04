<#
.SYNOPSIS
    Industrial Git Divergence Audit Script (v2)
    Compatible with PowerShell 5.1 and Core (7+)

.DESCRIPTION
    Automates the gap analysis between two diverged branches.
    Provides unique commits, unique technical assets, and tree parity verification.
    Generates an industrial CAM (Commit Action Mapping) table template in Markdown.

.PARAMETER LocalBranch
    The name of the local branch (default: main)

.PARAMETER RemoteBranch
    The name of the remote branch (default: origin/main)

.PARAMETER Markdown
    Switch to output a CAM table template in Markdown.
#>

Param (
    [string]$LocalBranch = "main",
    [string]$RemoteBranch = "origin/main",
    [switch]$Markdown
)

# 1. Environment Verification
Write-Host "### Industrial Git Divergence Audit" -ForegroundColor Cyan
Write-Host "Comparing: $LocalBranch <--> $RemoteBranch"

# 2. Divergence Discovery
try {
    $CommonBase = git merge-base $LocalBranch $RemoteBranch
    Write-Host "Divergence Point (Common Ancestor): $CommonBase" -ForegroundColor Green
} catch {
    Write-Error "Failed to find common ancestor. Ensure both branches exist."
    exit 1
}

# 3. Gap Analysis (Ahead)
Write-Host "`n#### Unique Commits on $LocalBranch (Ahead)" -ForegroundColor Yellow
$AheadCommits = git log --oneline "$CommonBase..$LocalBranch"
$AheadCommits | ForEach-Object { Write-Host $_ }

# 4. Gap Analysis (Behind)
Write-Host "`n#### Unique Commits on $RemoteBranch (Behind)" -ForegroundColor Yellow
$BehindCommits = git log --oneline "$CommonBase..$RemoteBranch"
$BehindCommits | ForEach-Object { Write-Host $_ }

# 5. Asset Identification & Categorization
Write-Host "`n#### Asset Identification (Stat)" -ForegroundColor Magenta

function Get-AssetCategory {
    param([string]$FilePath)
    if ($FilePath -match "\.agents/skills/" -or $FilePath -match "ai-agent-rules/" -or $FilePath -match "\.agent/") {
        return "Technical Asset"
    } elseif ($FilePath -match "\.md$" -or $FilePath -match "docs/") {
        return "Documentation"
    } elseif ($FilePath -match "\.vscode/" -or $FilePath -match "\.DS_Store") {
        return "Noise"
    } else {
        return "Other"
    }
}

Write-Host "--- Local ($LocalBranch) ---"
git diff --stat "$CommonBase..$LocalBranch"

Write-Host "--- Remote ($RemoteBranch) ---"
git diff --stat "$CommonBase..$RemoteBranch"

# 6. CAM Table Generation (Markdown)
if ($Markdown) {
    Write-Host "`n#### Industrial CAM (Commit Action Mapping) Table Template" -ForegroundColor Green
    Write-Host "| Commit Hash | Author | Category | Proposed Action (KEEP/DROP/SQUASH/REWORD) | Rationale |"
    Write-Host "| :--- | :--- | :--- | :--- | :--- |"

    # Process Ahead Commits
    foreach ($line in $AheadCommits) {
        $hash = $line.Split(' ')[0]
        $author = git log -1 --format='%an' $hash
        # Analyze files in commit to guess category
        $files = git diff-tree -r --no-commit-id --name-only $hash
        $category = "Other"
        if ($files) {
            $category = Get-AssetCategory $files[0]
        }
        Write-Host "| $hash | $author | $category | KEEP | Local refinement |"
    }

    # Process Behind Commits
    foreach ($line in $BehindCommits) {
        $hash = $line.Split(' ')[0]
        $author = git log -1 --format='%an' $hash
        $files = git diff-tree -r --no-commit-id --name-only $hash
        $category = "Other"
        if ($files) {
            $category = Get-AssetCategory $files[0]
        }
        Write-Host "| $hash | $author | $category | KEEP | Remote update |"
    }
}

# 7. Tree Parity Check
Write-Host "`n#### Current Tree Parity (Delta between tips)" -ForegroundColor Cyan
git diff --stat "$LocalBranch..$RemoteBranch"

Write-Host "`n### Audit Complete" -ForegroundColor Cyan
