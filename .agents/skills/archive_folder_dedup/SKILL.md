<!--
title: Archive & Folder Deduplication Audit
description: Cross-compare folders and archives (zip/7z) to detect duplicates, near-matches, and unique content — enabling safe cleanup of extracted directories, redundant archives, and trash leftovers.
category: Code Hygiene & Maintenance
-->

# Archive & Folder Deduplication Audit Skill

> **Skill ID:** `archive_folder_dedup`
> **Version:** 1.0.0
> **Standard:** [Agent Skills (agentskills.io)](https://agentskills.io)

## Description

Systematically cross-compare every folder against every archive (zip/7z),
and every archive against every other archive, to identify exact
duplicates, near-matches, and unique items. This skill produces
actionable verdicts: which folders are safe to delete (their content is
preserved in an archive), which archives are duplicates of each other,
and which items contain unique content requiring manual review.

Extracted folders that duplicate their source archive waste disk space
and create confusion about which copy is authoritative. Archives renamed
or duplicated under different names cause the same problem. This skill
catches all of these — including cross-name matches where a folder name
differs from its source archive name.

## Prerequisites

| Requirement | Minimum |
|---|---|
| Shell | PowerShell 5.1+ (Windows) or Bash 4+ (Linux/macOS) |
| .NET | System.IO.Compression.FileSystem assembly (ships with .NET Framework 4.5+ / .NET Core) |
| 7-Zip | `7z.exe` in PATH or at `C:\Program Files\7-Zip\7z.exe` (only if `.7z` files are present) |
| Access | Read access to all directories and archives being compared |

## When to Apply

Apply this skill when:

- A directory contains both archives (zip/7z) and extracted folders, and
  the user wants to know which folders are safe to delete
- A user asks to "deduplicate", "find duplicates", or "clean up archives"
- A trash/leftover directory exists alongside a clean directory and the
  user wants to verify what can be permanently deleted
- Archives may have been renamed, duplicated, or re-packaged under
  different names
- Folders may have been extracted from archives with different packaging
  structures (e.g., root-level files vs. subfolder-wrapped files)

Do NOT apply when:

- The user wants byte-level identical file comparison (use `diff` or
  `fc` for that — this skill compares file **listings**, not content)
- The user wants to merge or consolidate archives (this skill audits
  only — it does not modify files)
- A single file needs comparison (this skill operates on directory trees
  and archive listings)

---

## Key Concepts

### Normalization

Archives and folders package files differently. The same test case may
appear as:

- **Root-level:** `dfc_pavast.xml`, `os_auto_conf_sched.xml`
- **Subfolder-wrapped:** `TestCase1/dfc_pavast.xml`, `TestCase1/os_auto_conf_sched.xml`
- **Convention-prefixed:** `_pavast/dfc_pavast.xml`, `_pavast/os_auto_conf_sched.xml`

The normalization function MUST strip these packaging differences so that
content is compared by its **logical identity**, not its packaging path.

#### Normalization Rules (Applied in Order)

1. **Filter ignored directories** — Remove entries matching ignore
   patterns (e.g., `_log/`, `tmp/`, `tmp - Copy/`).

2. **Strip single common root** — If all entries share a single root
   folder prefix (e.g., `TestCase1/`), strip it. This handles the case
   where a zip wraps everything in one top-level folder.

3. **Strip convention prefixes** — Remove known convention prefixes
   like `_pavast/` that represent packaging style rather than content
   identity. This list is project-specific and MUST be configurable.

> **Why this matters:** Without normalization, a folder extracted at root
> level and the same content inside a zip under `_pavast/` will appear
> as completely different, generating false negatives.

### Comparison Categories

| Category | Definition | Action |
|---|---|---|
| **MATCH** | File listings are identical after normalization | Safe to delete the duplicate |
| **NEAR-MATCH** | File listings differ by ≤5 files after normalization | Review the diff — may be safe |
| **DIFF** | File listings differ by >5 files | Genuinely different content |
| **BOTH_EMPTY** | Both sources have 0 files | Both are empty — delete freely |
| **ONE_EMPTY** | One source has 0 files, the other does not | Cannot be duplicates |

---

## Step-by-Step Procedure

### Step 1 — Identify Scan Scope

Determine which directories to scan. A typical layout has:

- **Clean directory** — The authoritative source (archives + curated folders)
- **Trash directory** — Leftovers, old extractions, working copies
- **External archive directory** — Additional zip/7z storage

Ask the user to confirm:

1. Which directory is the **clean** (priority) source?
2. Are there **trash** or **leftover** directories to audit?
3. Are there **external archive** directories to include?

**Example layout:**

```text
project/
├── test_cases_clean/      ← clean: archives + curated folders
│   ├── TestA.zip
│   ├── TestB.7z
│   ├── FolderC/
│   └── FolderD/
├── test_cases_trash/      ← trash: old extractions, leftovers
│   ├── OldFolderA/
│   └── OldFolderB/
└── archive_storage/       ← external: additional archives
    └── Backup.zip
```

### Step 2 — Build Inventories

For each source (folder, zip, or 7z), extract a normalized file listing.

#### 2.1 — List Files in a Zip Archive

**PowerShell:**

```powershell
Add-Type -AssemblyName System.IO.Compression.FileSystem

function Get-ZipFiles($path) {
    $zip = [System.IO.Compression.ZipFile]::OpenRead($path)
    $files = $zip.Entries |
        Where-Object { $_.Length -gt 0 } |
        ForEach-Object { $_.FullName -replace '\\','/' }
    $zip.Dispose()
    return Normalize $files
}
```

> `[System.IO.Compression.ZipFile]::OpenRead()` — opens the zip in
> read-only mode without extracting to disk.
> `Where-Object { $_.Length -gt 0 }` — filters out directory entries
> (which have zero length in zip metadata).
> `-replace '\\','/'` — normalizes path separators to forward slash.

#### 2.2 — List Files in a 7z Archive

**PowerShell (requires 7-Zip):**

```powershell
function Get-7zFiles($path) {
    $out = & $7z l -ba $path 2>$null
    $files = @()
    foreach ($line in $out) {
        $t = $line.Trim()
        if ($t -match '^D') { continue }
        if ($t -match '\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\s+(.+)$') {
            $f = $Matches[1].Trim() -replace '\\','/'
            if ($f -ne '') { $files += $f }
        }
    }
    return Normalize $files
}
```

> `7z l -ba` — lists archive contents in bare (machine-parseable) format.
> `-ba` — suppresses headers and footers, outputting only file entries.
> `'^D'` — skips lines starting with `D` (directory attribute marker).
> The regex `\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\s+(.+)$` captures
> the filename after the date-time columns.

#### 2.3 — List Files in a Directory

**PowerShell:**

```powershell
function Get-FolderFiles($path) {
    $resolved = (Resolve-Path $path).Path
    $files = Get-ChildItem -Path $resolved -Recurse -File |
        ForEach-Object {
            $_.FullName.Substring($resolved.Length + 1) -replace '\\','/'
        }
    return Normalize $files
}
```

> `Substring($resolved.Length + 1)` — strips the base path to produce
> relative paths.
> `-Recurse -File` — recurses all subdirectories, returns files only
> (no directory entries).

#### 2.4 — The Normalize Function

**PowerShell:**

```powershell
$ignoreRx = '(^|/)(_log|tmp|tmp - Copy|tmp_2019|tmp_before)/'

function Normalize($paths) {
    $filtered = @($paths | Where-Object { $_ -notmatch $ignoreRx })
    if ($filtered.Count -eq 0) { return @() }

    # Strip single common root folder prefix
    $first = $filtered[0]
    if ($first -match '^([^/]+)/') {
        $root = $Matches[1]
        $allMatch = ($filtered |
            Where-Object { $_ -like "$root/*" }).Count -eq $filtered.Count
        if ($allMatch) {
            $filtered = $filtered | ForEach-Object {
                $_ -replace "^$([regex]::Escape($root))/", ""
            }
        }
    }

    # Strip convention prefixes (project-specific)
    $filtered = $filtered | ForEach-Object { $_ -replace '^_pavast/', '' }

    return @($filtered | Sort-Object)
}
```

> `$ignoreRx` — regex matching directories to exclude from comparison.
> Customize per project (e.g., add `tmp_backup/`, `old/`).
> The common-root stripping handles zips that wrap all content in a
> single top-level folder (e.g., `MyTest/file.xml` → `file.xml`).
> Convention prefix stripping (`_pavast/`) handles packaging variations
> where the same files live at root level in one source and under a
> convention folder in another.

### Step 3 — Cross-Compare: Folder vs Archive

Compare **every** folder against **every** archive (zip and 7z). This
catches cases where a folder was extracted from a differently-named
archive.

**PowerShell:**

```powershell
function Compare-Listings($a, $b) {
    if ($a.Count -eq 0 -and $b.Count -eq 0) { return "BOTH_EMPTY" }
    if ($a.Count -eq 0 -or $b.Count -eq 0) { return "ONE_EMPTY" }
    $diff = Compare-Object $a $b
    if ($null -eq $diff) { return "MATCH" }
    $onlyA = @($diff | Where-Object { $_.SideIndicator -eq '<=' })
    $onlyB = @($diff | Where-Object { $_.SideIndicator -eq '=>' })
    return "DIFF(A-only:$($onlyA.Count),B-only:$($onlyB.Count))"
}
```

> `Compare-Object` — compares two sorted arrays element-by-element.
> `SideIndicator '<='` — item exists only in the left (first) array.
> `SideIndicator '=>'` — item exists only in the right (second) array.
> Returns `$null` when the arrays are identical.

**Execution loop — every folder × every archive:**

```powershell
$archiveKeys = @($allSources.Keys |
    Where-Object { $_ -match '^\[(ZIP|7Z)' } | Sort-Object)
$folderKeys  = @($allSources.Keys |
    Where-Object { $_ -match '^\[DIR\]' } | Sort-Object)

foreach ($fk in $folderKeys) {
    foreach ($ak in $archiveKeys) {
        $result = Compare-Listings $allSources[$fk] $allSources[$ak]
        if ($result -eq "MATCH") {
            Write-Output "MATCH: $fk  <-->  $ak"
        }
    }
}
```

> **Why every-to-every?** Folder names often don't match archive names.
> A folder `CallbackProcess/` may have been extracted from
> `ChainTaskIssue.zip`. Only an exhaustive cross-compare catches this.

### Step 4 — Cross-Compare: Archive vs Archive

Compare every archive against every other archive to detect renamed
duplicates.

```powershell
for ($i = 0; $i -lt $archiveKeys.Count; $i++) {
    for ($j = $i + 1; $j -lt $archiveKeys.Count; $j++) {
        $result = Compare-Listings `
            $allSources[$archiveKeys[$i]] `
            $allSources[$archiveKeys[$j]]
        if ($result -eq "MATCH") {
            Write-Output "MATCH: $($archiveKeys[$i])  <-->  $($archiveKeys[$j])"
        }
    }
}
```

> The `$i + 1` start for `$j` avoids comparing an archive with itself
> and avoids duplicate pairs (A↔B is the same as B↔A).

### Step 5 — Detect Near-Matches

Near-matches (≤5 file differences) often indicate packaging variations
or minor version differences. Report them with the exact diff.

```powershell
foreach ($fk in $folderKeys) {
    foreach ($ak in $archiveKeys) {
        $a = $allSources[$fk]; $b = $allSources[$ak]
        if ($a.Count -eq 0 -or $b.Count -eq 0) { continue }
        $diff = Compare-Object $a $b
        if ($null -ne $diff) {
            $total = ($diff | Measure-Object).Count
            if ($total -le 5 -and $total -gt 0) {
                Write-Output "NEAR($total): $fk  <-->  $ak"
                $diff | ForEach-Object {
                    Write-Output "    $($_.SideIndicator) $($_.InputObject)"
                }
            }
        }
    }
}
```

> `Measure-Object` — counts the total number of diff entries.
> The threshold of 5 is a practical default — adjust per project.
> `<=` prints the file exists only in the left source (folder).
> `=>` prints the file exists only in the right source (archive).

### Step 6 — Audit Trash Against Clean

When a trash directory exists, compare every trash item against every
clean item. Priority is always **clean** — if trash matches clean, trash
is safe to delete.

**Comparison matrix:**

| Comparison | Purpose |
|---|---|
| Trash folder → every clean archive | Trash folder is an old extraction |
| Trash folder → every clean folder | Trash folder is a stale copy |
| Trash archive → every clean archive | Trash archive is a renamed duplicate |
| Trash archive → every clean folder | Trash archive matches curated content |
| Trash item → every other trash item | Internal trash duplicates |

**Classification of trash items:**

| Result | Meaning | Action |
|---|---|---|
| Exact match with clean item | Content preserved in clean | 🗑️ Safe to delete |
| Near-match with clean item | Minor diff — likely packaging variation | ⚠️ Review the diff |
| No match in clean at all | Unique content only in trash | 🔴 Review before deleting |
| Empty (0 files) | Abandoned empty directory | 🗑️ Safe to delete |

### Step 7 — Deep-Dive Unique Trash Items

For each trash item marked as UNIQUE (no match in clean), produce a
detailed analysis explaining **why** it differs:

1. **List all files** in the trash item
2. **Identify the closest clean counterpart** (by name or near-match)
3. **Show the exact diff** — which files exist only in trash, which only
   in clean
4. **Classify the extra trash content:**

| Content Pattern | Meaning | Typical Action |
|---|---|---|
| `tmp/`, `tmp_backup/`, `tmp_back/` | ICE/tool execution output backups | 🗑️ Generated — safe to delete |
| `old/`, `pre_codefreez/` | Historical result snapshots | 🗑️ Reference only — safe to delete |
| `Results_beforeFix/`, `Results_afterFix/` | Before/after bug-fix comparison outputs | ⚠️ May be valuable for regression |
| `files_for_validation/` | Curated validation reference files | ⚠️ May be valuable for testing |
| `*_referenceResults_manualyMade/` | Hand-verified expected outputs | 🔴 High value — keep or archive |
| Pavast XML files (unique names) | Test input data for specific scenarios | 🔴 Unique test data — keep |

### Step 8 — Report Verdicts

#### Clean Folder Verdict Table

| # | Item | Type | Files | Match | Verdict |
|---|---|---|---|---|---|
| 1 | `FolderA/` | DIR | 6 | `TestA.zip` | ✅ Safe to delete folder |
| 2 | `FolderB/` | DIR | 3 | (none) | 🔴 Unique — keep |
| 3 | `TestX.zip` | ZIP | 6 | `TestY.zip` | ✅ Duplicate archive — keep one |

#### Trash Verdict Table

| # | Trash Item | Files | Clean Match | Verdict |
|---|---|---|---|---|
| 1 | `trash/OldFolder/` | 103 | `Clean.zip` | 🗑️ Safe to delete |
| 2 | `trash/WorkDir/` | 220 | (none — unique) | 🔴 Review — has hand-made reference results |
| 3 | `trash/empty/` | 0 | N/A | 🗑️ Empty — safe to delete |

#### Archive Duplicate Table

| # | Archive A | Archive B | Verdict |
|---|---|---|---|
| 1 | `Test.zip` | `Test (2).zip` | ✅ Identical — keep one |

#### Verdict Symbols

| Symbol | Meaning |
|---|---|
| ✅ | Safe — exact duplicate, content preserved elsewhere |
| ⚠️ | Near-match — review the 1-5 file diff before deciding |
| 🗑️ | Safe to delete — empty or fully duplicated |
| 🔴 | Unique content — review before deleting, may contain valuable data |

---

## Edge Cases

### Archives with Nested Archives

If a zip contains another zip inside it, the inner zip is treated as a
single file (by its filename), not expanded. This skill compares file
**listings**, not recursive archive contents. If inner-archive comparison
is needed, extract first and compare as folders.

### Very Large Directories (1000+ files)

For directories with many files, the `Compare-Object` cmdlet may be
slow. Pre-sort both arrays (the `Normalize` function already does this)
to ensure optimal comparison performance.

### Case Sensitivity

Windows file systems are case-insensitive. The `Compare-Object` cmdlet
in PowerShell is case-insensitive by default, which is correct for
Windows. On Linux/macOS, add `-CaseSensitive` if the file system is
case-sensitive.

### Corrupt or Password-Protected Archives

If `[System.IO.Compression.ZipFile]::OpenRead()` or `7z l` fails, catch
the error and report the archive as **UNREADABLE** in the inventory.
Do not skip it silently.

```powershell
try {
    $files = Get-ZipFiles $path
} catch {
    Write-Output "UNREADABLE: $path — $($_.Exception.Message)"
    $files = @()
}
```

### Convention Prefix Variations

Different projects use different convention prefixes. Common patterns:

| Prefix | Usage |
|---|---|
| `_pavast/` | DAMOS/ICE pavast test data packaging |
| `Manual/` | Manual test inputs (sometimes wraps `_pavast/`) |
| `src/` | Source code packaging in zip distributions |
| `data/` | Data file packaging |

The `Normalize` function MUST be extended per project. Document which
prefixes are stripped and why.

---

## Prohibited Behaviors

- **DO NOT** delete any files automatically — this skill audits and
  reports only; the user decides what to delete
- **DO NOT** compare file **content** (byte-level) — this skill compares
  file **listings** (names and paths) for performance; use `diff` or
  hash comparison for content verification
- **DO NOT** skip the every-to-every comparison — folder names frequently
  differ from archive names; only exhaustive cross-compare catches all
  duplicates
- **DO NOT** report a folder as "safe to delete" unless it has an exact
  MATCH with at least one archive — near-matches require review
- **DO NOT** assume trash items are disposable — always classify unique
  trash content (Step 7) before recommending deletion
- **DO NOT** ignore 7z files — they MUST be included alongside zip files
  in all comparison passes

---

## Environment & Dependencies

### PowerShell (Windows)

```powershell
# Verify .NET assembly availability
Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile] | Get-Member -Static | Select-Object Name
```

> If this fails, the .NET Framework version is too old. Upgrade to .NET
> Framework 4.5+ or use .NET Core / .NET 5+.

```powershell
# Verify 7-Zip (only needed if .7z files exist)
& "C:\Program Files\7-Zip\7z.exe" --help
```

> If 7-Zip is not installed: download from https://www.7-zip.org/ or
> install via `winget install 7zip.7zip`.

### Bash (Linux/macOS)

```bash
# Verify unzip
which unzip && unzip -v

# Verify 7z (p7zip)
which 7z && 7z --help
```

> Install if missing:
> - **macOS:** `brew install p7zip`
> - **Debian/Ubuntu:** `sudo apt install p7zip-full`
> - **RHEL/CentOS:** `sudo yum install p7zip p7zip-plugins`
