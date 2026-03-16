<!--
title: Bug Scanner Analysis
description: General methodology for running, interpreting, and validating
    existing bug scanner tools against codebases — covering tool discovery,
    input preparation, execution, output classification, false positive
    identification, and cross-validation with alternative detection methods.
category: Quality Assurance & Defect Detection
-->

# Bug Scanner Analysis Skill

> **Skill ID:** `bug_scanner_analysis`
> **Version:** 1.0.0
> **Standard:** [Agent Skills (agentskills.io)](https://agentskills.io)

## Description

Execute and interpret existing bug scanner tools — standalone
executables, scripts, or lint-style analyzers — against a codebase
or build artifact to detect known defect patterns. This skill covers
the full analysis lifecycle:

1. **Tool Discovery** — Locate the scanner binary/script, determine
   its version, input format, and invocation method.
2. **Input Preparation** — Identify and validate the required input
   artifacts (log files, cross-reference files, build outputs, source
   trees).
3. **Execution** — Run the scanner with correct arguments, I/O
   piping, and working directory.
4. **Output Classification** — Parse scanner output into categorized
   findings (bugs, warnings, informational).
5. **False Positive Identification** — Apply domain knowledge to
   eliminate findings that cannot manifest as real defects.
6. **Cross-Validation** — Compare results against alternative
   detection methods (inline source scanners, manual review, reference
   baselines) to assess precision and recall.
7. **Impact Assessment** — Determine which product versions, releases,
   or builds are affected.

This is a **general methodology** skill. Organization-specific scanner
tools layer on top of this skill with concrete tool details, input
formats, and domain-specific false positive rules.

### Philosophy

Bug scanners are post-hoc detection tools — they analyze artifacts
**after** a build or code generation step. Their findings are
**necessary but not sufficient**: a scanner hit indicates a potential
issue, but dynamic confirmation (via inline instrumentation or manual
review) may be needed to prove the defect is real.

The agent MUST treat scanner output with appropriate skepticism:

- **Every finding** must be traced back to a concrete artifact
  (source file, log line, cross-reference entry)
- **False positives** must be identified and documented with
  rationale — not silently dropped
- **Negative results** (zero findings) are a valid and important
  outcome — they must be explicitly stated, not omitted

## Related Skills

| Skill | Relationship |
|---|---|
| [`bug_scanner_development`](../bug_scanner_development/SKILL.md) | Complementary — develops new inline scanners; this skill runs existing ones |
| [`loc_analysis`](../loc_analysis/SKILL.md) | Complementary — quantify scanner-detected code paths |
| [`git_atomic_commit`](../git_atomic_commit/SKILL.md) | Used after — commit scanner result documentation |

## Prerequisites

| Requirement | Minimum |
|---|---|
| Scanner tool | The bug scanner executable, script, or analyzer |
| Input artifacts | Build outputs, logs, or source trees required by the scanner |
| Shell | PowerShell 5.1+ or Bash 4+ |
| VCS | Git 2.x+ (for version/release impact analysis) |

## Environment & Dependencies

Before executing any analysis steps, verify:

```powershell
# Verify the scanner tool exists
Test-Path "<SCANNER_PATH>"

# Check scanner version/help
& "<SCANNER_PATH>" --help 2>&1
# or: & "<SCANNER_PATH>" --version 2>&1

# Verify input artifacts exist
Test-Path "<INPUT_ARTIFACT>"

# Quick sanity check on input
(Get-Content "<INPUT_ARTIFACT>" | Measure-Object -Line).Lines
```

```bash
# Verify scanner
ls -la <SCANNER_PATH>
<SCANNER_PATH> --help 2>&1 || <SCANNER_PATH> --version 2>&1

# Verify input
ls -la <INPUT_ARTIFACT>
wc -l <INPUT_ARTIFACT>
```

## When to Apply

Apply this skill when:

- A user asks to run a bug scanner tool on a codebase or artifact
- A user provides scanner output and asks for interpretation
- A user asks "is my project affected by defect X?" and a scanner
  tool exists for that defect
- A user asks to compare scanner output between two builds/versions
- A user asks about false positives in scanner results
- A user has an existing scanner (EXE, script, linter) and wants to
  operationalize it

Do NOT apply when:

- No scanner tool exists yet (use `bug_scanner_development` to create
  one)
- The user wants to modify or extend a scanner's detection logic
  (that is development, not analysis)
- The user wants runtime instrumentation rather than post-hoc
  analysis (use `bug_scanner_development`)
- The issue is a build failure, not a defect pattern (use build
  failure analysis skills)

---

## Step-by-Step Procedure

### Step 1 — Tool Discovery and Characterization

Before running a scanner, characterize it completely:

| Property | How to Determine | Why It Matters |
|---|---|---|
| Tool name & version | Run with `--version`, `--help`, or inspect binary metadata | Reproducibility — results must be tied to a specific tool version |
| Input format | Documentation, help output, or reverse engineering | Wrong input = wrong results or silent failure |
| Input source | Where the tool reads from — file argument, stdin, or both | Determines the invocation command structure |
| Output format | Run on a known-positive test case and inspect output | Parsing strategy depends on output structure |
| Exit codes | Documentation or experimentation | Distinguish "no findings" from "tool error" |
| Known limitations | Documentation, changelogs, or empirical testing | Identifies categories of false positives/negatives |

**Discovery commands:**

```powershell
# File metadata (Windows EXE)
Get-Item "<SCANNER_PATH>" | Select-Object Name, Length, LastWriteTime,
    @{N='Version'; E={$_.VersionInfo.FileVersion}}

# Try common help flags
& "<SCANNER_PATH>" --help 2>&1
& "<SCANNER_PATH>" -h 2>&1
& "<SCANNER_PATH>" /? 2>&1
```

```bash
# File metadata
file <SCANNER_PATH>
ls -la <SCANNER_PATH>

# Try common help flags
<SCANNER_PATH> --help 2>&1
<SCANNER_PATH> -h 2>&1
```

**If the tool has no documentation**, use reverse engineering:

1. Run against a known-good input (expect zero findings)
2. Run against a known-bad input (expect non-zero findings)
3. Compare outputs to understand the finding format
4. Test edge cases (empty input, malformed input) to understand
   error handling

### Step 2 — Input Preparation and Validation

Locate and validate all required input artifacts:

```powershell
# Verify file exists and is non-empty
$file = Get-Item "<INPUT_ARTIFACT>"
if (-not $file.Exists) { Write-Error "Input not found"; return }
if ($file.Length -eq 0) { Write-Error "Input is empty"; return }
"Input: $($file.FullName), $($file.Length) bytes"

# Check expected structure markers
Select-String -Path "<INPUT_ARTIFACT>" -Pattern "<EXPECTED_HEADER>" |
    Select-Object -First 3 LineNumber, Line
```

**Common input types and validation:**

| Input Type | Validation Check |
|---|---|
| Log file | Contains expected phase markers, timestamps, or section headers |
| Cross-reference file | Contains section delimiters and correctly formatted entries |
| Source tree | Expected directory structure, file extensions, entry points present |
| Build output | Build completed successfully (check exit code, summary lines) |
| Binary artifact | Correct file format (magic bytes), expected size range |

**Critical:** If the input is generated by a build tool, verify the
build completed **successfully** before analyzing its output. An
incomplete or failed build produces partial artifacts that cause
scanner false negatives (missed issues) or false positives (phantom
issues from truncated data).

### Step 3 — Execution

Run the scanner with the validated input. Match the tool's expected
invocation pattern:

**Pattern A — File argument:**

```powershell
& "<SCANNER_PATH>" "<INPUT_ARTIFACT>" | Out-File "<RESULT_FILE>" -Encoding utf8
```

**Pattern B — Stdin piping:**

```powershell
Get-Content "<INPUT_ARTIFACT>" |
    & "<SCANNER_PATH>" |
    Out-File "<RESULT_FILE>" -Encoding utf8
```

**Pattern C — Directory scanning:**

```powershell
& "<SCANNER_PATH>" --input "<SOURCE_DIR>" --output "<RESULT_FILE>"
```

**Capture both stdout and stderr:**

```powershell
& "<SCANNER_PATH>" "<INPUT_ARTIFACT>" 2>&1 |
    Out-File "<RESULT_FILE>" -Encoding utf8
```

**Record execution metadata** for reproducibility:

```powershell
$startTime = Get-Date
# ... run scanner ...
$endTime = Get-Date
$duration = $endTime - $startTime
"Scanner ran for $($duration.TotalSeconds)s"
```

### Step 4 — Output Classification

Parse the scanner output into structured categories:

```powershell
$results = Get-Content "<RESULT_FILE>"
"Total lines: $($results.Count)"

# Classify by finding type (adapt patterns to the specific scanner)
$bugs = ($results | Select-String -Pattern "^Bug|^ERROR|^CRITICAL").Count
$warnings = ($results | Select-String -Pattern "^Warning|^WARN|^ICE_MCOP").Count
$info = ($results | Select-String -Pattern "^Info|^NOTE").Count

"Classification: $bugs bugs, $warnings warnings, $info informational"
```

**Build a findings table:**

| # | Finding Type | Count | Severity | Action Required |
|---|---|---|---|---|
| 1 | Bug / Critical | N | High | Investigate each finding |
| 2 | Warning | N | Medium | Review for false positives |
| 3 | Informational | N | Low | Document for traceability |

### Step 5 — False Positive Identification

Apply domain-specific knowledge to filter false positives:

**Common false positive categories:**

| Category | Description | Resolution |
|---|---|---|
| Initialization-only paths | Code runs once at startup, cannot cause concurrent issues | Exclude initialization entries from analysis |
| Dead code paths | Scanner detects patterns in unreachable code | Verify reachability before flagging |
| Configuration-disabled paths | Feature is disabled in the build configuration | Check runtime config/feature flags |
| Test-only artifacts | Scanner hits in test code that never reaches production | Exclude test directories |
| Version-specific false positives | Tool version has known bugs in its detection logic | Document and cross-validate with newer tool version |

**Document every exclusion:**

```markdown
### False Positive Exclusions

| # | Finding | Reason for Exclusion |
|---|---|---|
| 1 | Message X flagged as Bug | Only INI-task writers — runs once at startup |
| 2 | File Y flagged as affected | Dead code — function never called |
```

**Critical:** Never silently drop a finding. Every exclusion MUST be
documented with specific rationale.

### Step 6 — Cross-Validation

Compare scanner results against alternative detection methods to
assess accuracy:

**Validation strategies:**

| Strategy | When to Use |
|---|---|
| Run scanner with `exclude=off` mode | Compare full vs filtered output to quantify false positive rate |
| Compare with reference baseline | Known-good baseline exists from a previous version |
| Cross-validate with inline scanner | Mode B (source instrumentation) confirms dynamic behavior |
| Manual code review | Sample a subset of findings and verify manually |
| Compare two scanner versions | Newer tool version may have fixes for known false positives |

**Baseline comparison command:**

```powershell
Compare-Object (Get-Content "result_baseline.txt") (Get-Content "result_current.txt")
```

```bash
diff result_baseline.txt result_current.txt
```

### Step 7 — Release Impact Analysis

Determine which product versions or releases are affected:

```powershell
cd "<REPO_ROOT>"

# Find the defect-introducing commit
git log --oneline --all --grep="<DEFECT_TICKET>" | Select-Object -First 5

# Find the fix commit
git log --oneline --all --grep="<FIX_TICKET>" | Select-Object -First 5

# Classify tags
$defect = "<defect_commit>"
$fix = "<fix_commit>"

git tag -l "<tag_pattern>" | ForEach-Object {
    $tag = $_
    git merge-base --is-ancestor $defect $tag 2>$null
    $hasDefect = $LASTEXITCODE -eq 0
    git merge-base --is-ancestor $fix $tag 2>$null
    $hasFix = $LASTEXITCODE -eq 0

    if (-not $hasDefect) { "$tag : NOT-AFFECTED (pre-defect)" }
    elseif ($hasDefect -and -not $hasFix) { "$tag : AFFECTED" }
    else { "$tag : FIXED" }
}
```

**Output format:**

| Category | Versions | Action |
|---|---|---|
| Pre-defect | ≤ X.Y.Z | No action needed |
| Affected | X.Y.Z – A.B.C | Scan all builds; recommend migration |
| Fixed | ≥ A.B.C | No action needed |

---

## Reporting

The final analysis report MUST include:

1. **Scanner identification** — tool name, version, invocation command
2. **Input identification** — artifact path, size, provenance
3. **Raw results** — total findings by category
4. **False positive analysis** — excluded findings with rationale
5. **Net findings** — actionable findings after filtering
6. **Cross-validation** — comparison with alternative methods
7. **Release impact** — affected version ranges
8. **Recommendation** — migrate, patch, or accept risk

---

## Common Pitfalls

| Pitfall | Solution |
|---|---|
| Running scanner on incomplete build output | Verify build completed successfully before analyzing artifacts |
| Treating all findings as confirmed bugs | Scanner findings are candidates — cross-validate before escalating |
| Silently dropping false positives | Document every exclusion with specific rationale |
| Not recording tool version | Results are not reproducible without version; different versions may produce different output |
| Using wrong input source (file arg vs stdin) | Check tool documentation or experiment with both patterns |
| Confusing zero findings with "tool didn't run" | Check exit code, stderr, and expected output format markers |
| Comparing results across different input versions | Ensure the same build/artifact version is used for apples-to-apples comparison |
| Ignoring scanner stderr warnings | Scanner may report parsing issues or skipped entries on stderr |

---

## Checklist

Before finalizing the analysis, verify:

- [ ] Scanner tool version identified and documented
- [ ] Input artifact exists, is non-empty, and was produced by a successful build
- [ ] Scanner invocation command matches the tool's expected pattern
- [ ] Results captured to a file (not just console)
- [ ] Findings classified by type and severity
- [ ] False positives identified and documented with rationale
- [ ] Cross-validation performed (if alternative methods available)
- [ ] Negative results explicitly documented (zero findings is a valid outcome)
- [ ] Release impact assessed (affected version ranges)
- [ ] Execution metadata recorded (timestamp, duration, tool version)
