<!--
title: Scanner Product Packaging
description: General methodology for packaging an instrumented product as a
    standalone distributable — covering version discovery via VCS tags, base
    product copying, JAR/archive patching with instrumented classes, patch
    verification, archive creation, standalone runtime validation,
    runtime compatibility assessment, and wrapper script distribution.
category: Quality Assurance & Defect Detection
-->

# Scanner Product Packaging Skill

> **Skill ID:** `scanner_product_packaging`
> **Version:** 1.1.0
> **Standard:** [Agent Skills (agentskills.io)](https://agentskills.io)

## Description

Package an instrumented product (containing bug scanner logging) as
a standalone distributable artifact that can be executed by others
**without** an IDE or development environment. This skill covers the
full packaging lifecycle:

1. **Version Discovery** — Identify the latest stable product version
   by cross-referencing VCS tags, release branches, and installed
   product directories.
2. **Base Product Copying** — Copy the full product directory to a
   working location for patching.
3. **JAR/Archive Patching** — Replace specific class files inside
   JAR/ZIP archives with instrumented versions compiled from the
   development workspace.
4. **Patch Verification** — Confirm the patched class was injected
   correctly by comparing file sizes, entry listings, and archive
   integrity.
5. **Product Archiving** — Create a distributable archive (ZIP, TAR)
   of the complete patched product.
6. **Standalone Verification** — Run the patched product outside the
   IDE against a known-affected test input to confirm the scanner
   entries appear in output logs.
7. **Runtime Compatibility** — Identify and document any runtime
   constraints (Java version, environment variables, launcher
   arguments) that differ from the development environment.

### Core Principle — Distribute the Fix, Not the Source

The packaged product contains the **already-fixed** codebase with
scanner instrumentation added. Recipients do not need:

- Access to the source repository
- An IDE or build toolchain
- Knowledge of the instrumentation implementation

They only need the product archive, the correct runtime (e.g., Java),
and the input to scan (e.g., a PVER, project, or dataset).

### When This Skill Applies

This skill sits **downstream** of `bug_scanner_development`:

```
bug_scanner_development → scanner_product_packaging → bug_scanner_analysis
     (instrument)              (package & ship)            (run & analyze)
```

Apply this skill after the inline scanner has been implemented,
compiled, and validated in the IDE — and the goal is to create a
portable artifact others can run.

## Related Skills

| Skill | Relationship |
|---|---|
| [`bug_scanner_development`](../bug_scanner_development/SKILL.md) | Upstream — develops the inline scanner that this skill packages |
| [`bug_scanner_analysis`](../bug_scanner_analysis/SKILL.md) | Downstream — recipients use analysis methodology to interpret scanner output |
| [`git_atomic_commit`](../git_atomic_commit/SKILL.md) | Used after — commit packaging artifacts and documentation |
| [`ship_release_notes`](../ship_release_notes/SKILL.md) | Complementary — include usage instructions in the distributable |

## Prerequisites

| Requirement | Minimum |
|---|---|
| Instrumented source | Scanner logging compiled and verified in IDE (zero errors) |
| Base product | A released/installed version of the product matching the instrumented source base |
| Build output | Compiled class files (`.class`) in workspace `bin/` or `target/` |
| VCS | Git 2.x+ (for version/tag discovery) |
| Shell | PowerShell 5.1+ or Bash 4+ |
| Archive tools | .NET `System.IO.Compression` (PowerShell) or `zip`/`tar` (Bash) |
| Test input | A known-affected input for standalone verification |

## Environment & Dependencies

Before packaging, verify:

```powershell
# Verify the compiled scanner class exists
Test-Path "<WORKSPACE>/bin/<class_path>/<InstrumentedClass>.class"

# Check class file timestamp (must be after instrumentation)
(Get-Item "<WORKSPACE>/bin/<class_path>/<InstrumentedClass>.class").LastWriteTime

# Verify the base product directory exists
Test-Path "<PRODUCT_BASE>/<version>"
```

```bash
# Verify the compiled scanner class exists
ls -la <WORKSPACE>/bin/<class_path>/<InstrumentedClass>.class

# Verify the base product directory
ls -d <PRODUCT_BASE>/<version>
```

---

## Step 1 — Version Discovery

### 1.1 Identify the Source Base Version

The instrumented source is built on a specific product version. Find
it from VCS:

```powershell
cd "<REPO_ROOT>"

# Current branch/tag
git describe --tags --abbrev=0

# The tag that the current HEAD descends from
git log --oneline -1

# All release tags, sorted
git tag -l "<product_prefix>_*" | Sort-Object
```

### 1.2 Locate the Installed Product

The base product must be an **installed** (released) version — not a
development workspace. It contains the full runtime: launcher
executables, configuration, all plugin JARs, libraries, and
documentation.

```powershell
# List available product versions
Get-ChildItem "<PRODUCT_INSTALL_DIR>" -Directory |
    Sort-Object Name |
    ForEach-Object { $_.Name }
```

### 1.3 Match Tag to Product Version

Cross-reference the VCS tag with the installed product version.
The product version naming may differ from the VCS tag naming:

| VCS Tag | Product Directory | Match Method |
|---|---|---|
| `product_3.17.1` | `3.17.1` | Strip prefix |
| `v2024.2.1` | `2024.2.1` | Strip `v` |
| `release/2.0.0` | `2.0.0.dg` | Strip prefix + match base |

**Critical:** Always use the **latest stable** version, not release
candidates or alpha/test versions. Verify the tag is on the main
release branch:

```powershell
# Verify tag is ancestor of main branch
git merge-base --is-ancestor <TAG> origin/<MAIN_BRANCH>
# Exit code 0 = tag is on main lineage
```

### 1.4 Verify the JAR Matches

The product's JAR must contain the **same** class (pre-instrumentation)
as the workspace source base. Compare class sizes:

```powershell
Add-Type -AssemblyName System.IO.Compression.FileSystem

$jar = "<PRODUCT>/<plugins>/<bundle_jar>"
$zip = [System.IO.Compression.ZipFile]::OpenRead($jar)
$entry = $zip.Entries | Where-Object {
    $_.FullName -eq "<class/path/ClassName.class>"
}
"Original class size: $($entry.Length) bytes"
$zip.Dispose()

# Compare to workspace compiled class
"Scanner class size: $((Get-Item '<WORKSPACE>/bin/<class/path/ClassName.class>').Length) bytes"
```

The scanner class MUST be larger than the original (logging code adds
bytes). If the scanner class is the same size or smaller, the
instrumentation was not compiled.

---

## Step 2 — Base Product Copying

Copy the **entire** product directory — not just the JAR being
patched. The product must be self-contained and runnable.

```powershell
$source = "<PRODUCT_INSTALL_DIR>/<version>"
$dest = "<WORKING_DIR>/<product_name>_scanner_product"

Copy-Item -Path $source -Destination $dest -Recurse -Force

# Verify copy
$fileCount = (Get-ChildItem $dest -Recurse -File).Count
$totalSize = (Get-ChildItem $dest -Recurse -File |
    Measure-Object -Property Length -Sum).Sum
"Copied: $fileCount files, $([math]::Round($totalSize/1MB,1)) MB"
```

**Critical:** Copy the **full product** — not just the plugins
directory. The product launcher (`.exe`, `.sh`, `.cmd`), configuration
files (`.ini`), and documentation are all required for standalone
operation.

---

## Step 3 — JAR/Archive Patching

### 3.1 Identify the Target JAR

Locate the JAR within the product that contains the class to patch:

```powershell
Get-ChildItem "$dest/<plugins_dir>" -Filter "*<bundle_name>*.jar" |
    ForEach-Object { "$($_.Name) ($($_.Length) bytes)" }
```

### 3.2 Patch the JAR

Replace the class entry inside the JAR with the instrumented version.

**Method A — .NET ZipArchive (Recommended for PowerShell):**

The `jar uf` command may silently fail on certain JDK versions or
when the JAR has specific compression settings. Use .NET ZipArchive
for reliable patching:

```powershell
Add-Type -AssemblyName System.IO.Compression

$jarFile = "$dest/<plugins>/<bundle.jar>"
$classFile = "<WORKSPACE>/bin/<class/path/ClassName.class>"
$entryName = "<class/path/ClassName.class>"

# Open JAR for update
$zip = [System.IO.Compression.ZipFile]::Open(
    $jarFile,
    [System.IO.Compression.ZipArchiveMode]::Update
)

# Delete existing entry
$existing = $zip.Entries | Where-Object { $_.FullName -eq $entryName }
if ($existing) {
    $existing.Delete()
    "Deleted old entry"
}

# Add instrumented class
$newEntry = $zip.CreateEntry(
    $entryName,
    [System.IO.Compression.CompressionLevel]::Optimal
)
$stream = $newEntry.Open()
$classBytes = [System.IO.File]::ReadAllBytes($classFile)
$stream.Write($classBytes, 0, $classBytes.Length)
$stream.Close()

"Wrote $($classBytes.Length) bytes to new entry"
$zip.Dispose()
```

**Why NOT `jar uf`:**

The `jar uf` command can silently fail to update entries in certain
conditions (e.g., different compression method, signed JARs, specific
JDK implementations). The exit code is 0 but the entry remains
unchanged. Always verify after patching regardless of method used.

**Method B — `jar uf` (Java, use with verification):**

```powershell
$jarFile = "$dest/<plugins>/<bundle.jar>"
$classDir = "<WORKSPACE>/bin"

Push-Location $classDir
& "<JAVA_HOME>/bin/jar.exe" uf $jarFile "<class/path/ClassName.class>"
Pop-Location
```

### 3.3 Verify the Patch

**Always** verify the class size inside the JAR changed:

```powershell
Add-Type -AssemblyName System.IO.Compression.FileSystem

$zip = [System.IO.Compression.ZipFile]::OpenRead($jarFile)
$entry = $zip.Entries | Where-Object { $_.FullName -eq $entryName }

"Class in JAR: $($entry.Length) bytes"
"Expected:     $((Get-Item $classFile).Length) bytes"
"Match:        $($entry.Length -eq (Get-Item $classFile).Length)"
$zip.Dispose()
```

**The sizes MUST match.** If they do not, the patch failed — retry
with the alternative method.

Also verify the overall JAR size delta:

```powershell
$originalSize = <ORIGINAL_JAR_SIZE>  # Record before patching
$patchedSize = (Get-Item $jarFile).Length
"Original: $originalSize bytes"
"Patched:  $patchedSize bytes"
"Delta:    +$($patchedSize - $originalSize) bytes"
```

The delta should be positive (instrumentation adds code).

---

## Step 4 — Product Archiving

Create a distributable archive of the complete patched product:

```powershell
$zipFile = "<WORKING_DIR>/<product_name>_scanner_product.zip"

Remove-Item $zipFile -Force -ErrorAction SilentlyContinue

Compress-Archive `
    -Path "$dest\*" `
    -DestinationPath $zipFile `
    -CompressionLevel Optimal

"Archive: $zipFile"
"{0:N1} MB" -f ((Get-Item $zipFile).Length / 1MB)
```

**Verify the archive:**

```powershell
Add-Type -AssemblyName System.IO.Compression.FileSystem

$zip = [System.IO.Compression.ZipFile]::OpenRead($zipFile)
"Total entries: $($zip.Entries.Count)"

# Verify the patched JAR is inside
$zip.Entries | Where-Object {
    $_.FullName -match "<bundle_name>.*\.jar$"
} | ForEach-Object {
    "$($_.FullName) ($($_.Length) bytes)"
}

# Verify the launcher is inside
$zip.Entries | Where-Object {
    $_.FullName -match "<launcher>\.(exe|cmd|sh)$"
} | ForEach-Object {
    "$($_.FullName) ($($_.Length) bytes)"
}
$zip.Dispose()
```

---

## Step 5 — Standalone Verification

### 5.1 Identify Runtime Requirements

Before running the product standalone, determine:

| Requirement | Discovery Method |
|---|---|
| Java version | Check `.ini` file, launcher script, or product documentation |
| Launcher syntax | Check `*_cmd.txt`, `*.cmd`, or `*.sh` in product root |
| JVM arguments | Check `.cmd`/`.sh` launcher for `-Xmx`, `-Dosgi.*`, etc. |
| Required inputs | Check launcher documentation for argument format |

**Common runtime constraints:**

| Constraint | Symptom | Solution |
|---|---|---|
| Java version too high | JPMS `module does not opens` errors | Use Java 11 instead of 17+ |
| Missing JVM args | OSGi configuration errors, `@none` config area | Copy JVM args from launcher `.cmd`/`.sh` |
| Missing environment vars | Launcher script fails at initialization | Set required `TB_*` or `*_HOME` variables |
| Stale OSGi config | Previous run's cached configuration interferes | Delete `<user_home>/<product>_config/` before each run |

### 5.2 Run the Product

Execute the product against a known-affected test input:

```powershell
# Clean OSGi configuration cache
Remove-Item "$env:USERPROFILE\<product>_config" `
    -Recurse -Force -ErrorAction SilentlyContinue

# Set working directory to the test input root
Set-Location "<TEST_INPUT_ROOT>"

# Run the product
& "<PRODUCT_DIR>/<launcher>" `
    -data <workspace_path> `
    -vm "<JAVA_HOME>/bin/java.exe" `
    <additional_arguments> `
    -vmargs <jvm_arguments>
```

### 5.3 Monitor and Verify Scanner Output

Wait for the product to complete, then verify scanner entries:

```powershell
# Wait for the process to exit
while ($true) {
    Start-Sleep -Seconds 30
    $proc = Get-Process -Name "<process_name>" -ErrorAction SilentlyContinue
    if ($null -eq $proc) { "Process finished!"; break }
}

# Search for scanner entries
$logFile = "<TEST_INPUT_ROOT>/<log_path>/<tool_log>"
$hits = Select-String -Path $logFile -Pattern "<SCANNER_TAG>"
"Scanner hits: $($hits.Count)"
$hits | ForEach-Object { $_.Line }
```

### 5.4 Cross-Validate Results

Compare standalone results against the IDE-based run:

| Metric | IDE Run | Standalone Run | Match? |
|---|---|---|---|
| Scanner entry count | N | N | ✅ Must match |
| Detected entities | List | List | ✅ Must match |
| Non-scanner output | Reference | Current | ✅ Should match |

**If results differ:**

- **Zero entries standalone, N entries in IDE** — The compiled class
  in the patched JAR may not be the same version. Recompile and
  re-patch.
- **Different entry count** — Check if the product version matches
  the source version. A version mismatch can cause different code
  paths to execute.

---

## Step 6 — Distribution Documentation

When distributing the archive, document:

1. **Product base version** — Which release the archive is based on
2. **What was patched** — Which JAR(s) and class(es) were modified
3. **Scanner tag** — What string to grep for in logs
4. **Runtime requirements** — Java version, required JVM arguments
5. **How to run** — Exact command line or launcher invocation
6. **How to read results** — What each scanner entry means

---

## Step 7 — Re-Packaging After Code Changes

When the scanner instrumentation is modified after the initial
packaging (e.g., updated log tags, refactored code, additional scan
points), the product must be re-packaged from scratch. **Never
re-patch an already-patched product** — always start from a clean
base product copy.

### 7.1 Back Up the Previous Package

Before overwriting, preserve the previous packaged product for
comparison:

```powershell
$timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$backupName = "backup_<product_name>_scanner_product_$timestamp"

# Back up the product folder
Rename-Item -Path $dest -NewName $backupName

# Back up the archive
if (Test-Path $zipFile) {
    Rename-Item -Path $zipFile -NewName "$backupName.zip"
}
```

### 7.2 Compile and Verify the Updated Scanner

In the IDE:

1. Modify the scanner source file(s) as needed
2. Build the project — verify **zero** compilation errors
3. Confirm the updated class timestamp and size:

```powershell
$classFile = "<WORKSPACE>/bin/<class/path/ClassName.class>"
"Size:     $((Get-Item $classFile).Length) bytes"
"Modified: $((Get-Item $classFile).LastWriteTime)"
```

The class size may differ from the previous version — this is
expected when code changes are made.

### 7.3 Re-Execute the Packaging Pipeline

Repeat Steps 2 through 5 using the newly compiled class:

| Step | Action | Key Difference from Initial Run |
|---|---|---|
| Step 2 | Fresh copy from product install directory | Do NOT re-use the backup |
| Step 3 | Patch JAR with the newly compiled class | Class size may differ |
| Step 4 | Archive the patched product | New archive replaces old |
| Step 5 | Run standalone and verify scanner output | Compare with previous results |

### 7.4 Cross-Validate Against Previous Results

Compare the new run's output with the previous run:

| Metric | Previous | New | Expected |
|---|---|---|---|
| Scanner hit count | N | N | Same (unless scan points changed) |
| Detected entities | List | List | Same (unless scan points changed) |
| Log tag | Old tag | New tag | Different if tag was updated |
| Class file size | Old bytes | New bytes | May differ due to code changes |

If the hit count or entity list differs unexpectedly, the code
change may have inadvertently altered the scanner logic. Review the
source diff before accepting the new results.

---

## Step 8 — Wrapper Script Distribution

After the scanner product is packaged (Steps 1–6), wrap it in a
self-contained distributable with an automation script that handles
version detection, classification, execution, and result extraction.

### 8.1 Distribution Layout Pattern

```
<scanner_name>/
    <entry_script>               Entry point script (e.g., scan.ps1)
    README.txt                   Minimal usage instructions
    config/
        <config_file>            Version lists & scanner settings (YAML)
    product/                     Scanner product from Steps 1–6
        eclipse/
        docs/
        ...
```

All paths are auto-discovered relative to the entry script. The user
provides only the input path (e.g., PVER path).

### 8.2 Entry Script Responsibilities

The wrapper script automates the full scan lifecycle:

| Responsibility | Implementation |
|---|---|
| Config loading | Lightweight parser (no external modules) |
| Input version detection | Product-specific metadata parsing |
| Version classification | Exact lists → range fallback → heuristic |
| Runtime detection | Auto-detect Java / runtime from env vars & config |
| Scanner execution | Invoke the packaged product's launcher |
| Result extraction | Stream through output logs for scanner tag |
| Exit code mapping | Semantic codes: 0=clean, 1=issues, 2=error, 3=unknown |

### 8.3 Config File Pattern

Use a simple YAML (or similar) config with:

- **Scanner settings**: tag pattern, log file paths, plugin names
- **Affected versions**: explicit list of known-affected versions
- **Fixed versions**: explicit list of known-fixed versions
- **Pre-defect versions**: versions before the defect was introduced
- **Affected range**: numeric range with exceptions and additions
- **Runtime search paths**: ordered list of directories to search for
  the required runtime (Java JDK, etc.)

### 8.4 Packaging the Distribution

```powershell
$ts = Get-Date -Format 'yyyyMMdd_HHmmss'
Compress-Archive -Path '<scanner_name>\*' `
    -DestinationPath "<scanner_name>_$ts.zip" -Force
```

Timestamp the archive to enable version tracking. Recipients unzip
and run the entry script — no installation or configuration required.

### 8.5 Concrete Example

The `chain_task_copy_scanner` skill (Mode D) implements this pattern:

| Element | Concrete Implementation |
|---|---|
| Entry script | `scan.ps1` (PowerShell 5.1+, ~1100 lines) |
| Config | `config/scanner_config.yaml` (custom YAML parser) |
| Product | `product/` (ICE scanner product from Mode C) |
| Input detection | `tool_details.json` → `toolName: "dgs_ice"` → `toolVersion` |
| Runtime | Java 11 (auto-detected via env vars and config paths) |
| Scanner tag | `CHAIN-TASK-COPY-BUG-SCANNER` |
| Report | Structured text report in PVER's log directory |

---

## Common Pitfalls

| Pitfall | Solution |
|---|---|
| `jar uf` silently fails | Use .NET `ZipArchive` instead — it provides explicit entry deletion and insertion |
| Wrong product used as base | The product MUST match the VCS tag the scanner was built from. Cross-reference using `git describe` and product version directories |
| Only the JAR was zipped, not the full product | Copy the **entire** product directory, not just `plugins/`. The launcher, config, and docs are required for standalone operation |
| Java 17+ fails with JPMS errors | Many Eclipse/OSGi products with BeanShell or legacy reflection require Java 11. Check the product's launcher script for the expected Java version |
| Class compiled with wrong Java version | The class must be compiled with the same or lower Java version as the product's target. A Java 17-compiled class in a Java 11 product will fail with `UnsupportedClassVersionError` |
| Previous OSGi configuration cached | Delete `$env:USERPROFILE\<product>_config` before each standalone run. Stale configuration from previous IDE or standalone runs can cause bundle resolution failures |
| Patch verification skipped | **Always** verify the class size inside the patched JAR matches the compiled class. Silent `jar uf` failures are a known issue |
| Archived wrong directory | Verify the archive contains the launcher executable and the patched JAR by inspecting entries before distribution |
| Re-patched an already-patched product | Always start from a clean base product copy when re-packaging. Re-patching a previously patched JAR can leave stale entries or corrupt the archive |
| Forgot to back up before re-packaging | Always rename (not delete) the previous product folder and archive before re-packaging. Enables comparison and rollback |

---

## Checklist

Before distributing the archive:

- [ ] Latest stable product version identified via VCS tags
- [ ] Full product directory copied (not just plugins)
- [ ] Target JAR identified and original size recorded
- [ ] Class patched using .NET ZipArchive (or `jar uf` with verification)
- [ ] Patch verified: class size in JAR matches workspace compiled class
- [ ] JAR size delta is positive (instrumentation adds bytes)
- [ ] Archive created with all product files
- [ ] Archive verified: contains launcher AND patched JAR
- [ ] Standalone run completed against known-affected test input
- [ ] Scanner entries match IDE-based results (same count, same entities)
- [ ] Runtime requirements documented (Java version, JVM args)
- [ ] Distribution documentation prepared
- [ ] Previous product backed up before re-packaging (Step 7)
- [ ] Re-packaging used fresh base copy, not previous patched product (Step 7)
- [ ] Re-packaged scanner hits match previous run count (Step 7)
- [ ] Wrapper script has zero parse errors (Step 8)
- [ ] Config file has correct version lists for the target defect (Step 8)
- [ ] Distribution ZIP is self-contained and timestamped (Step 8)
- [ ] README.txt documents minimal invocation and prerequisites (Step 8)
- [ ] Entry script auto-detects runtime without user configuration (Step 8)
