<!--
title: Bug Scanner Development
description: General methodology for developing new inline bug scanners by
    instrumenting source code with diagnostic logging at known-fix guard
    points — covering defect archaeology, fix-point identification,
    instrumentation design, compilation verification, runtime validation,
    and release impact documentation.
category: Quality Assurance & Defect Detection
-->

# Bug Scanner Development Skill

> **Skill ID:** `bug_scanner_development`
> **Version:** 1.0.0
> **Standard:** [Agent Skills (agentskills.io)](https://agentskills.io)

## Description

Develop inline bug scanners by instrumenting source code with
diagnostic logging at the exact locations where a known defect was
fixed. The scanner proves whether a specific input (build, dataset,
configuration) **would be affected** by the defect on older,
unfixed versions — without modifying the application's functional
behavior.

This skill covers the full development lifecycle:

1. **Defect Archaeology** — Trace the defect's history through VCS
   to identify the introducing commit, the fix commit, and the
   affected version range.
2. **Fix-Point Identification** — Locate the exact code locations
   where the fix was applied — the guard conditions, the protected
   calls, the variables introduced.
3. **Instrumentation Design** — Design diagnostic logging that fires
   inside the fix's guard-true branch, capturing all relevant context
   (entity names, priorities, conditions) to prove the code path was
   entered.
4. **API Discovery** — Study the available API surface to determine
   which methods and fields can be safely called in the logging
   statements without introducing compilation errors.
5. **Compilation Verification** — Clean build and verify zero errors
   after instrumentation.
6. **Runtime Validation** — Run the instrumented application on a
   known-affected input and verify scanner entries appear in the log.
7. **Release Impact Documentation** — Classify all releases as
   pre-defect, affected, or fixed using VCS ancestry analysis.

### Core Principle — Instrument the Fix, Not the Bug

The scanner does NOT reproduce the bug. Instead, it instruments the
**fix's guard condition** to detect when the protected code path is
entered. The logic is:

> If the guard-true branch fires, the input exercises the code path
> that was **unguarded** on older versions. Therefore, the input
> **is affected** if processed by those older versions.

This approach is safe because:

- The fix is already in place — functional behavior is unchanged
- The logging is purely diagnostic — no state mutation
- The scanner runs on the **fixed** version, not the broken one
- False positives are impossible — the guard-true branch only fires
  when the condition genuinely holds

## Related Skills

| Skill | Relationship |
|---|---|
| [`bug_scanner_analysis`](../bug_scanner_analysis/SKILL.md) | Complementary — runs existing scanners; this skill creates new ones |
| [`git_atomic_commit`](../git_atomic_commit/SKILL.md) | Used after — commit scanner instrumentation changes |
| [`loc_analysis`](../loc_analysis/SKILL.md) | Used after — quantify scanner instrumentation LOC |

## Prerequisites

| Requirement | Minimum |
|---|---|
| Repository | Source repository containing the fix commit |
| VCS | Git 2.x+ (for commit archaeology) |
| Build system | Capable of incremental or clean rebuild |
| Logging framework | Application-level logger available (e.g., SLF4J, Log4j, ICELogger, `console.log`, `print`) |
| Test input | A known-affected input to validate the scanner |
| Shell | PowerShell 5.1+ or Bash 4+ |

## Environment & Dependencies

Before starting development, verify:

```powershell
# Verify repository is on a post-fix branch/tag
cd "<REPO_ROOT>"
git log --oneline -1
git describe --tags --abbrev=0

# Verify the fix commit exists
git log --oneline --all --grep="<FIX_TICKET>"

# Verify the fix is in the current branch
git merge-base --is-ancestor <FIX_COMMIT> HEAD
# Exit code 0 = fix is present
```

## When to Apply

Apply this skill when:

- A user asks to instrument code to detect affected inputs for a
  known defect
- A user asks to add diagnostic logging at a fix location
- A user asks "how can I tell if my build/input is affected by
  defect X?"
- An existing post-hoc scanner exists but dynamic confirmation is
  needed
- A user asks to prove a defect's impact on a specific input by
  running the fixed code with diagnostics
- A user wants to create a scanner that can be deployed temporarily
  in a product branch for field detection

Do NOT apply when:

- The defect has not been fixed yet (fix it first, then instrument)
- A post-hoc scanner already provides sufficient detection (use
  `bug_scanner_analysis`)
- The user wants to fix the defect, not detect its impact
- The instrumentation would modify functional behavior (violates
  the diagnostic-only principle)
- The logging framework is not available or would introduce
  dependencies

---

## Step-by-Step Procedure

### Step 1 — Defect Archaeology

Trace the defect's full lifecycle through VCS history.

#### 1.1 Locate the Fix Commit

```powershell
cd "<REPO_ROOT>"
git log --oneline --all --grep="<FIX_TICKET>" | Select-Object -First 5
```

#### 1.2 Inspect the Fix Diff

```powershell
git show <FIX_COMMIT> --stat
git show <FIX_COMMIT> -- "<AFFECTED_FILE>"
```

**Extract from the fix diff:**

| Field | What to Look For |
|---|---|
| Guard condition | New `if` statement that wraps the previously unguarded call |
| Protected call | The method or operation that was previously unconditional |
| New variables | Variables introduced to compute the guard condition |
| Affected method | The method containing the fix |
| Affected file(s) | All files modified by the fix |

#### 1.3 Locate the Defect-Introducing Commit

```powershell
# Use git log to find the commit that introduced the vulnerable code
git log --oneline --all --grep="<DEFECT_TICKET>"

# Or use git blame on the line before the fix
git blame <FIX_COMMIT>~1 -- "<AFFECTED_FILE>" | Select-String "<VULNERABLE_LINE>"
```

#### 1.4 Verify the Defect Range

```powershell
# The defect exists from the introducing commit to just before the fix
git log --oneline <DEFECT_COMMIT>..<FIX_COMMIT> -- "<AFFECTED_FILE>" |
    Measure-Object | Select-Object Count
```

**Document the timeline:**

| Event | Commit | Date | Ticket |
|---|---|---|---|
| Defect introduced | `<hash>` | YYYY-MM-DD | `<ticket>` |
| Defect fixed | `<hash>` | YYYY-MM-DD | `<ticket>` |
| Versions affected | X.Y.Z – A.B.C | — | — |

---

### Step 2 — Fix-Point Identification

Locate the exact code locations where the fix was applied.

#### 2.1 Find All Fix Locations

A single fix may touch multiple code paths within the same method
or across multiple methods/files. Each location needs its own
scanner instrumentation.

```powershell
# Search for the guard variable introduced by the fix
Select-String -Path "<AFFECTED_FILE>" -Pattern "<GUARD_VARIABLE>" -Context 3
```

**For each fix location, document:**

| # | File | Method | Line(s) | Guard Condition | Protected Call |
|---|---|---|---|---|---|
| 1 | `<file>` | `<method>` | ~N | `if (<guard>)` | `<call>` |
| 2 | `<file>` | `<method>` | ~M | `if (<guard>)` | `<call>` |

#### 2.2 Understand the Guard Logic

For each fix location, answer:

1. **What was the behavior BEFORE the fix?** — The protected call
   executed unconditionally (or under a weaker condition).
2. **What is the behavior AFTER the fix?** — The protected call
   only executes when the guard condition is met.
3. **When does the guard-true branch fire?** — The specific
   condition under which the optimization/operation is deemed safe.
4. **What does it mean for the scanner?** — If the guard-true
   branch fires, the input exercises the code path that was
   unguarded on older versions.

---

### Step 3 — API Discovery

Before writing the logging statements, discover which methods and
fields are safely callable on the objects in scope.

#### 3.1 Identify Available Objects

Examine the method signature and local variables at the fix
location to determine what context is available:

```powershell
# Read the method signature
Select-String -Path "<AFFECTED_FILE>" -Pattern "def |function |public.*\(" -Context 5 |
    Where-Object { $_.LineNumber -lt <FIX_LINE> } |
    Select-Object -Last 1
```

#### 3.2 Discover API Surface

For each object you plan to use in the log message:

```powershell
# Search for the type definition/interface
Select-String -Path "<SOURCE_DIR>/**/*.java" -Pattern "interface <TYPE>|class <TYPE>" -Recurse

# List available methods
Select-String -Path "<TYPE_FILE>" -Pattern "public .* get|public .* is" |
    Select-Object LineNumber, Line
```

**Critical — API validation rules:**

| Rule | Rationale |
|---|---|
| Only call methods that exist on the declared type | Compile error if the method does not exist |
| Avoid methods with side effects | Scanner must be diagnostic-only |
| Prefer `getShortName()` over `toString()` | Short names are more useful in log messages |
| Check for null-safety | Some getters may return null; use defensive access |
| Do NOT assume methods from related types | A `MessageAccessor` is not a `Task` — check the actual interface |

**Document the API surface:**

| Method | Returns | Available On | Safe for Logging |
|---|---|---|---|
| `getName()` | `String` | `<Type>` | Yes |
| `getPriority()` | `int` | `<Type>` | Yes |
| `getInternalState()` | `State` | `<Type>` | No (side effects) |

---

### Step 4 — Instrumentation Design

Design the diagnostic logging statements.

#### 4.1 Choose a Log Tag

Select a unique, grep-friendly tag for the scanner:

```
[<PROJECT>-<DEFECT>-SCANNER]
```

**Requirements:**

- Uppercase with hyphens for grep readability
- Wrapped in square brackets for easy `Select-String` extraction
- Includes the project/component and defect identifier
- Unique enough to not collide with existing log messages

**Verify uniqueness:**

```powershell
Select-String -Path "<SOURCE_DIR>/**/*" -Pattern "<LOG_TAG>" -Recurse
# Expected: zero matches before instrumentation
```

#### 4.2 Design the Log Message

The log message MUST include:

| Field | Purpose | Example |
|---|---|---|
| Log tag | Grep-friendly identifier | `[CHAIN-TASK-COPY-SCANNER]` |
| Entity identifier | Which input entity triggered the path | `Message 'CrCsHtr_stDesVal'` |
| Fix ticket reference | Traceability to the fix | `(PMT-40106)` |
| Context values | Guard condition inputs — names, priorities, indices | `Writer prio=5, Reader prio=4` |
| Impact statement | What this means for older versions | `On version X..Y this was unguarded` |
| Remediation | What to do about it | `Migrate to >= Z` |

**Template:**

```
[<LOG_TAG>] <Entity> '<name>' enters <description> (<fix_ticket>).
 <Context key1>=<value1>, <Context key2>=<value2>.
 On <affected_versions> this <protected_call> was <unguarded_behavior>.
 <Remediation_instruction>.
```

#### 4.3 Placement Rule

Insert the log statement **inside** the guard-true branch,
**immediately after** the protected call:

```
if (<guard_condition>) {
    <protected_call>;        // ← The original fix
    <SCANNER_LOG>;           // ← Insert HERE
}
```

**NOT before the call** (the call might throw), **NOT in an else
branch** (that means the guard blocked it — the input is safe),
**NOT outside the guard** (fires for all inputs, not just affected
ones).

#### 4.4 Multi-Location Consistency

If the fix was applied at multiple locations, each scanner log
statement MUST:

- Use the **same log tag** (for unified grep)
- Include a **location discriminator** (e.g., "scenario 3",
  "path A") to distinguish which fix location fired
- Log the **same field set** (for consistent parsing)

---

### Step 5 — Implementation

Apply the instrumentation to the source code.

#### 5.1 Verify the Logging Framework

Confirm the logger is available at the instrumentation point:

```powershell
# Check for existing logger import/usage
Select-String -Path "<AFFECTED_FILE>" -Pattern "import.*Logger|require.*logger|from.*logging"
```

If the logger is not imported, add the import. If no logging
framework is available, use the language's native output
(`System.out.println`, `console.log`, `print`).

#### 5.2 Insert the Instrumentation

Insert the log statement at each fix location, immediately after
the protected call inside the guard-true branch.

**Verify insertion points before editing:**

```powershell
Select-String -Path "<AFFECTED_FILE>" -Pattern "<PROTECTED_CALL>" -Context 5
```

Confirm the context matches the expected fix pattern. Then insert
the logging code.

#### 5.3 Verify Zero Compilation Errors

After inserting at ALL fix locations:

```powershell
# Language-specific build command
# Java:
javac <AFFECTED_FILE>
# Or use IDE error checking

# TypeScript:
npx tsc --noEmit

# Python:
python -m py_compile <AFFECTED_FILE>

# C/C++:
make <TARGET>
```

**Critical:** Fix ALL compilation errors before proceeding. Common
errors:

| Error | Cause | Fix |
|---|---|---|
| Method not found | Calling a method that doesn't exist on the type | Use API discovery (Step 3) to find the correct method |
| Type mismatch | Concatenating incompatible types in log message | Use explicit `String.valueOf()` or equivalent |
| Missing import | Logger class not imported | Add the import statement |
| Scope error | Referencing a variable not in scope at the log point | Use only variables visible at the insertion point |

---

### Step 6 — Runtime Validation

Run the instrumented application on a known-affected input.

#### 6.1 Prepare Test Input

Use an input that is known to trigger the defect on unpatched
versions. If no known-affected input is available, use the largest
or most complex available input (maximizes the chance of exercising
the code path).

#### 6.2 Rebuild Before Running

**Critical:** The application MUST be rebuilt after instrumentation.
If using an IDE with incremental compilation, verify the modified
file was recompiled. If using a build system, run a clean build.

```powershell
# Verify the build timestamp is after the source edit
$source = Get-Item "<AFFECTED_FILE>"
$binary = Get-Item "<COMPILED_OUTPUT>"
if ($binary.LastWriteTime -lt $source.LastWriteTime) {
    Write-Error "Binary is older than source — rebuild required"
}
```

#### 6.3 Run and Monitor

Run the application and monitor for scanner entries:

```powershell
# If log file is written during execution (may be locked)
$fs = [System.IO.FileStream]::new("<LOG_FILE>",
    [System.IO.FileMode]::Open,
    [System.IO.FileAccess]::Read,
    [System.IO.FileShare]::ReadWrite)
$sr = [System.IO.StreamReader]::new($fs)
$text = $sr.ReadToEnd()
$sr.Close(); $fs.Close()
$matches = [regex]::Matches($text, "<LOG_TAG>")
"Scanner entries found: $($matches.Count)"
```

```bash
# Tail the log for live monitoring
tail -f <LOG_FILE> | grep "<LOG_TAG>"
```

#### 6.4 Extract and Parse Entries

```powershell
Select-String -Path "<LOG_FILE>" -Pattern "<LOG_TAG>" |
    ForEach-Object { "Line $($_.LineNumber): $($_.Line)" }
```

#### 6.5 Validate Results

| Outcome | Meaning | Action |
|---|---|---|
| Zero entries | Input does not exercise the defect path | Input is NOT affected — document as negative result |
| Non-zero entries | Input exercises the defect path | Input IS affected on unpatched versions — document findings |
| Application crash | Instrumentation introduced an error | Debug — check null access, method signatures, scope |
| Stale results (zero entries but expected non-zero) | Binary not rebuilt | Clean build and re-run |

---

### Step 7 — Release Impact Documentation

Classify all product releases using VCS ancestry analysis.

```powershell
$defectCommit = "<DEFECT_COMMIT>"
$fixCommit = "<FIX_COMMIT>"
$tagPattern = "<TAG_PREFIX>*"

$preDef = @(); $affected = @(); $fixed = @()

git tag -l $tagPattern | ForEach-Object {
    $tag = $_
    git merge-base --is-ancestor $defectCommit $tag 2>$null
    $hasDef = $LASTEXITCODE -eq 0
    git merge-base --is-ancestor $fixCommit $tag 2>$null
    $hasFix = $LASTEXITCODE -eq 0

    if (-not $hasDef) { $preDef += $tag }
    elseif (-not $hasFix) { $affected += $tag }
    else { $fixed += $tag }
}

"Pre-defect: $($preDef.Count) tags"
"Affected:   $($affected.Count) tags"
"Fixed:      $($fixed.Count) tags"
```

**Output table:**

| Category | Version Range | Count | Status |
|---|---|---|---|
| Pre-defect | ≤ X.Y.Z | N | Not affected |
| Affected | X.Y.Z – A.B.C | N | **Scan recommended** |
| Fixed | ≥ A.B.C | N | Not affected |

---

## Architecture Decision: Inline vs Post-Hoc Scanners

| Aspect | Inline Scanner (this skill) | Post-Hoc Scanner (`bug_scanner_analysis`) |
|---|---|---|
| **When to build** | Fix exists; need to prove impact dynamically | Artifact exists; need static pattern matching |
| **Precision** | Very high — fires only when guard condition holds | Medium — may have false positives |
| **Requires rebuild** | Yes | No |
| **Runtime cost** | Minimal (one log call per guard-true hit) | Zero (runs on artifacts, not live application) |
| **Deployment** | Temporary instrumentation branch | Standalone tool |
| **Best for** | Proving specific inputs are affected | Batch-scanning many inputs |

Use **both** together for maximum confidence: post-hoc scanner for
broad screening, inline scanner for dynamic confirmation of flagged
inputs.

---

## Common Pitfalls

| Pitfall | Solution |
|---|---|
| Instrumenting the else branch instead of the if-true branch | The guard-true branch is where the fix allows the operation — that is the path that was unguarded before |
| Calling methods that don't exist on the type | Always verify the API surface before using a method in the log message |
| Forgetting to rebuild before running | The application uses compiled bytecode/binary — source edits are not live until rebuilt |
| Reading a locked log file | Use `FileStream` with `FileShare.ReadWrite` to read while the application is writing |
| Concluding "no entries" before the relevant phase completes | The scanner only fires during the specific processing phase — wait for completion |
| Modifying functional behavior | Scanner logging MUST be diagnostic-only — no state mutation, no conditional branching |
| Using a non-unique log tag | Verify the tag produces zero matches before instrumentation |
| Logging in a hot loop without rate limiting | If the guard-true branch fires millions of times, consider sampling or counting instead of per-hit logging |

---

## Checklist

Before finalizing the scanner, verify:

- [ ] Fix commit identified and inspected
- [ ] Defect-introducing commit identified
- [ ] All fix locations identified (guard conditions + protected calls)
- [ ] API surface verified — only existing methods used
- [ ] Log tag is unique (zero pre-existing matches)
- [ ] Log message includes entity ID, context values, fix ticket, impact statement
- [ ] Instrumentation placed inside guard-true branch, after protected call
- [ ] All fix locations instrumented (not just the first one)
- [ ] Zero compilation errors after instrumentation
- [ ] Application rebuilt before test run
- [ ] Scanner entries appear in log for known-affected input
- [ ] Entries parseable by grep/Select-String
- [ ] Release impact documented (pre-defect / affected / fixed)
- [ ] Instrumentation committed to a feature/scanner branch (not mainline)
