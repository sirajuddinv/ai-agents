<!--
title: Generate Release Notes
description: Author user-facing and developer-only release notes with strict content separation — ensuring end users see features and fixes while developers retain implementation context.
category: Documentation & Packaging
-->

# Generate Release Notes Skill

> **Skill ID:** `generate_release_notes`
> **Version:** 1.0.0
> **Standard:** [Agent Skills (agentskills.io)](https://agentskills.io)

## Description

Author release notes for a new version by splitting content into
**user-facing** (`RELEASE_NOTES_*.md`) and **developer-only**
(`DEV_NOTES_*.md`) files.  This skill defines the boundary between
user and developer content, provides templates for both file types,
and establishes classification rules for common content categories.

The core principle: **Would an end user running the shipped product
need or benefit from this information?**  If yes, it belongs in
`RELEASE_NOTES`.  If it requires source code, build tools, or internal
knowledge to be useful, it belongs in `DEV_NOTES`.

### Companion Skills

| Skill | Relationship |
|---|---|
| `ship_release_notes` | Covers **packaging and distributing** the notes.  Apply this skill to write the notes, then `ship_release_notes` to ship them. |
| `split_user_vs_dev_docs` | Same user/dev boundary principle applied to `README.md` and `AGENTS.md`. |

## Prerequisites

| Requirement | Minimum |
|---|---|
| Files | `releases/` directory exists |
| Context | List of changes since last release (git log, issue tracker, or manual) |
| Context | Understanding of which changes affect end users vs developers |

## When to Apply

Apply this skill when:

- A new version is being prepared and needs release documentation
- Existing release notes mix user-facing and developer-only content
  in a single file
- A single monolithic `CHANGELOG.md` needs splitting into per-version
  user/dev files
- Release notes contain internal tool names, class names, or build
  system details that end users should not see
- Content was removed from release notes and lost instead of being
  transferred to developer notes

Do NOT apply when:

- Release notes are auto-generated from conventional commits
  (the generator should apply these rules)
- The project is a library consumed only by developers
  (all content is developer-facing)
- Release notes are managed externally (GitHub Releases, Jira)

---

## Step-by-Step Procedure

### Step 1 — Gather Changes

Collect all changes since the last release from available sources:

```powershell
# Git log since last tag/release
git log v1.5.0..HEAD --oneline

# Or since a specific commit
git log abc1234..HEAD --oneline
```

Also check:

- Issue tracker (closed issues, merged PRs)
- Manual notes from the development cycle
- Build system changes
- Dependency updates

### Step 2 — Classify Each Change

Apply the **User/Dev Boundary Rule** to every change:

> **Would an end user running the shipped product need or benefit
> from this information?**

#### Classification Reference

| Content | Classification | Reasoning |
|---|---|---|
| New CLI arguments or modes | **User** | Users invoke the CLI |
| Bug fix affecting output | **User** | Users see the fixed output |
| Breaking change to CLI or config | **User** | Users must update scripts |
| Minimum Java/runtime version change | **User** | Users must update environment |
| Release notes ship with product | **User** | Users benefit from knowing this |
| New feature (described by behaviour) | **User** | Users use the feature |
| Status (deployed, packed, in dev) | **User** | Users know version lifecycle |
| Internal class/enum names | **Dev** | Users never see source code |
| Internal constant names or values | **Dev** | Users never see constants |
| Refactoring details | **Dev** | No user-visible change |
| Build script changes | **Dev** | Users don't build from source |
| Internal tool names (`nvmsplit.exe`, `srec_cat.exe`) | **Dev** | Users don't invoke internal tools directly |
| Logging framework integration | **Dev** | Internal infrastructure |
| Distribution layout changes | **Dev** | Users see the layout, don't need a map |
| JDK test matrix (specific versions) | **Dev** | Users need the minimum version, not the test matrix |
| Dependency JAR changes | **Dev** | Users don't manage JARs |
| Investigation documents, root-cause analysis | **Dev** | Internal knowledge |
| Project restructuring | **Dev** | Internal organisation |
| IDE configuration changes | **Dev** | Users don't use the IDE setup |

#### Grey Areas

Some content has both user and dev aspects.  Split them:

| Content | User-Facing Part | Dev-Only Part |
|---|---|---|
| Java version requirement raised | "Minimum Java version is now 11" | "JNA 5.14.0 requires Java 11 as minimum runtime" |
| Release notes included in product | "Release notes are now included in the distribution" | "Ant release target uses `includes="RELEASE_NOTES_*.md"`" |
| PIB mode stability fix | "Resolved warnings in PIB converter mode" | "Warnings were JDK-version-dependent; root-cause analysis in `docs/`" |
| HEX file generation mode | "New HEX mode generates Intel HEX files" | "Uses `srec_cat.exe` to produce Intel HEX files" |
| Improved reliability | "Internal improvements to logging and error handling" | "TUL logging integration, JNA-based native platform resolution" |

### Step 3 — Write the User-Facing Release Notes

Create `releases/RELEASE_NOTES_{VERSION}.md` with the following
template:

```markdown
# {Product} v{VERSION} — Release Notes

**Release Date:** {YYYY-MM-DD}
**Status:** {In development | Packed | Deployed}

## What's New

### {Feature Title}

{Describe the feature in terms of user behaviour, not implementation.
Use verbs like "generates", "supports", "displays", not "refactored",
"extracted", "renamed".}

### {Another Feature}

{Same principle — user behaviour, not implementation.}

## Bug Fixes

- {Describe what the user sees fixed, not the root cause.}

## Breaking Changes

- **{What changed.}** {What the user must do to adapt.}

## Available Modes

{Include a modes/features table if the product has multiple modes.
This gives users a quick reference regardless of what's new.}

| Mode | Description |
|---|---|
| FM | Firmware conversion |
| ... | ... |

## Requirements

- Java {VERSION}+
```

#### Content Rules for RELEASE_NOTES

| Rule | Example (Good) | Example (Bad) |
|---|---|---|
| Describe behaviour, not implementation | "Unified 4-argument CLI" | "ConversionMode enum centralises mode metadata" |
| No internal tool names | "Generates Intel HEX files" | "Uses `srec_cat.exe` to produce HEX files" |
| No class/variable names | "Fixed exit code handling" | "Removed `System.exit(0)` from converter classes" |
| No build system references | "Release notes included with product" | "Ant `includes=` pattern copies release notes" |
| No dependency details | "Minimum Java 11" | "JNA 5.14.0 requires Java 11" |
| Include migration steps for breaks | "Scripts using 3-arg format must be updated" | "Breaking change" (no guidance) |
| Status reflects lifecycle | "Packed — awaiting deployment" | (no status) |

### Step 4 — Write the Developer Notes

Create `releases/DEV_NOTES_{VERSION}.md` with the following template:

```markdown
# {Product} v{VERSION} — Developer Notes

## {Implementation Topic}

{Detailed technical description — class names, constants, algorithms,
trade-offs, root causes.  This is where all the internal context lives.}

## {Another Topic}

{Same depth.  Link to design docs, investigation files, UML diagrams.}

## Key Files Changed

- `{File.java}` — {what changed and why}
- `{OtherFile.java}` — {what changed and why}
```

#### Content Rules for DEV_NOTES

| Rule | Reasoning |
|---|---|
| Use exact class, method, and variable names | Developers need precise references |
| Link to internal docs (`docs/`, investigation files) | Preserves traceability |
| Explain root causes and trade-offs | Future developers need the "why" |
| List key files changed | Helps code review and archaeology |
| Include dependency version details | Developers manage the classpath |
| Document build script changes | Developers run the build |
| Include test matrix results | Developers verify compatibility |

### Step 5 — Write the README Table Entry

Add a row to the Release Notes table in `README.md`:

```markdown
| [1.6.0](releases/RELEASE_NOTES_1.6.0.md) | In development | Unified 4-argument CLI, release notes included with product |
```

#### README Notes Column Rules

- **One-line summary** — the most important user-facing changes.
- **No implementation details** — "central constants", "ConversionMode
  enum", "TUL logging" are meaningless to end users.
- **No internal tool names** — "srec_cat", "nvmsplit" should not appear.
- **User-benefit language** — "PIB mode stability" not
  "JDK-version-dependent warnings resolved".

### Step 6 — Cross-Check: Nothing Lost

Every piece of content from the change list (Step 1) MUST appear in
either `RELEASE_NOTES` or `DEV_NOTES`.  Nothing should be discarded.

```powershell
# Compare change count to documented items
$changes = git log v1.5.0..HEAD --oneline | Measure-Object -Line
Write-Host "Changes: $($changes.Lines)"

$rnItems = Select-String -Path releases/RELEASE_NOTES_1.6.0.md -Pattern '^- |^### ' |
    Measure-Object -Line
$dnItems = Select-String -Path releases/DEV_NOTES_1.6.0.md -Pattern '^- |^## ' |
    Measure-Object -Line
Write-Host "Documented: RN=$($rnItems.Lines), DN=$($dnItems.Lines)"
```

If content was removed from `RELEASE_NOTES`, verify it was transferred
to `DEV_NOTES` — not just deleted.

### Step 7 — Validate Content Boundary

Scan the user-facing file for content that should be dev-only:

```powershell
# Check for internal tool names, class names, build references
$patterns = @(
    '\.java\b',           # Java file references
    '\.exe\b',            # Executable names
    '\bAnt\b',            # Build system
    '\bMaven\b',
    '\bGradle\b',
    '\bJNA\b',            # Internal dependency
    '\bSystem\.exit\b',   # Code-level detail
    '\brefactor',         # Dev-only verb
    '\benum\b',           # Code construct
    '\bconstants?\b'      # Code construct
)
$regex = ($patterns -join '|')
Select-String -Path releases/RELEASE_NOTES_*.md -Pattern $regex -CaseSensitive
# Expected: no matches (or only false positives)
```

---

## Complete Examples

### Example: RELEASE_NOTES (User-Facing)

```markdown
# PLC_Converter v1.6.0 — Release Notes

**Release Date:** 2026-03-12
**Status:** In development

## What's New

### Unified 4-Argument CLI

The command-line interface now uses a **fixed 4-argument format** for
all modes:

```
PLC_Converter <NVM_FILE|NA> <PIB_FILE|NA> <OUTPUT_DIR> <MODE>
```

Use `NA` for arguments not required by the selected mode.

**Examples:**

| Mode | Command |
|---|---|
| FM | `PLC_Converter firmware.nvm NA output FM` |
| PIB | `PLC_Converter NA config.pib output PIB` |
| ALL | `PLC_Converter firmware.nvm config.pib output ALL` |

### Release Notes Included with Product

Release notes are now included in the distribution under `releases/`.

## Breaking Changes

- **CLI argument order changed.** All modes now require exactly
  4 arguments: `<NVM_FILE|NA> <PIB_FILE|NA> <OUTPUT_DIR> <MODE>`.
  Scripts using the old 3-argument format must be updated.

## Requirements

- Java 11+
```

### Example: DEV_NOTES (Developer-Only)

```markdown
# PLC_Converter v1.6.0 — Developer Notes

## ConversionMode Enum

New `ConversionMode` enum centralises mode metadata — input
requirements (`needsNvm`, `needsPib`), display names, TUL identifiers,
and self-documenting usage strings with NA placeholders.

## Central Constants

Raw string literals consolidated into `PLCConstants`:

- File extensions: `NVM_EXT`, `PIB_EXT`, `HEX_EXT`, `DCM_EXT`
- Tool paths: `TOOLS_DIR`, `NVMSPLIT_EXE`, `SREC_CAT_EXE`
- NVM suffixes: `FM_NVM_SUFFIX` (`-00`), `MC_NVM_SUFFIX` (`-01`)
- Status values: `STATUS_SUCCESS`, `STATUS_FAILURE`, `STATUS_PARTIAL`

## TUL Logging Improvements

- TUL JAR renamed from `tul-logging-1.0.1.jar` to
  `tul_logging-1.0.1.jar` (underscore naming convention).
- `TOOL_NAME` derived from `PLCConstants.APP_NAME`.

## Release Notes Packaging — Implementation

The Ant `release` target uses `includes="RELEASE_NOTES_*.md"` —
`DEV_NOTES_*.md` files are automatically excluded.

## Internal Refactoring

- `System.exit(0)` removed from all converter classes.
- `NVMSplitter` refactored: `splitAndVerify()`, `deriveFmPath()`.
- `FileValidator` gains `validateFile()`, `checkToolExists()`.

## Key Files Changed

- `ConversionMode.java` — new enum (6 modes)
- `PLCConstants.java` — ~113 lines of constants added
- `Application.java` — rewritten for fixed 4-arg CLI
```

### Example: README Table Entry

```markdown
| [1.6.0](releases/RELEASE_NOTES_1.6.0.md) | In development | Unified 4-argument CLI, release notes included with product |
```

---

## Verification Checklist

| # | Check | Pass |
|---|---|---|
| 1 | Every change is documented in either RELEASE_NOTES or DEV_NOTES | ☐ |
| 2 | No content was removed without transferring to the other file | ☐ |
| 3 | RELEASE_NOTES contains no internal tool names | ☐ |
| 4 | RELEASE_NOTES contains no class/method/variable names | ☐ |
| 5 | RELEASE_NOTES contains no build system references | ☐ |
| 6 | RELEASE_NOTES contains no dependency version details | ☐ |
| 7 | RELEASE_NOTES uses behaviour language, not implementation language | ☐ |
| 8 | Breaking changes include user migration guidance | ☐ |
| 9 | DEV_NOTES includes exact file/class names for traceability | ☐ |
| 10 | DEV_NOTES links to investigation docs where applicable | ☐ |
| 11 | README table Notes column uses user-benefit language | ☐ |
| 12 | README table Notes column has no implementation details | ☐ |
| 13 | Status field reflects actual lifecycle state | ☐ |

---

## Anti-Patterns

| Pattern | Why It Fails |
|---|---|
| "Added ConversionMode enum" in user notes | Users don't know what an enum is |
| "Uses `srec_cat.exe` for HEX generation" in user notes | Users don't invoke internal tools |
| "Refactored NVMSplitter" in user notes | Refactoring is invisible to users |
| "JNA 5.14.0 requires Java 11" in user notes | Users need "Java 11+", not the dependency reason |
| "Ant release target uses `includes=`" in user notes | Build implementation is dev-only |
| Removing content without transferring to DEV_NOTES | Information is permanently lost |
| Mixing user and dev content in one file | Impossible to ship user notes without exposing internals |
| "Improved reliability" without DEV_NOTES detail | Users get a vague summary; developers lose all context |
| "Packed, not deployed to toolbase" in user notes | Internal workflow status; use "Packed" only |
| Listing JDK test versions in user notes | Users need the minimum; the test matrix is dev-only |
| Status column omitted from README table | Users can't determine version availability |

---

## Reference Implementation

The PLC Converter project applies this skill across four versions:

### v1.3.0

- **RELEASE_NOTES**: DCM mode, HEX mode (no `srec_cat` mention),
  ALL mode update, modes table, Java 8+ requirement
- **DEV_NOTES**: `srec_cat.exe` implementation detail, distribution
  layout, JDK test versions (8u212, 11.0.9.1)

### v1.4.0

- **RELEASE_NOTES**: "Resolved warnings in PIB converter mode",
  modes unchanged, Java 8+
- **DEV_NOTES**: JDK-version-dependent root cause, investigation doc
  link, test matrix (JDK 8, 11, 17)

### v1.5.0

- **RELEASE_NOTES**: Java 11 minimum requirement *(user-facing —
  affects their environment)*, "Improved Reliability"
- **DEV_NOTES**: JNA requires Java 11 *(the reason)*, TUL logging
  integration, distribution layout, dependency table

### v1.6.0

- **RELEASE_NOTES**: Unified 4-arg CLI with examples, release notes
  shipping, breaking change warning, modes table
- **DEV_NOTES**: ConversionMode enum, PLCConstants listing, TUL JAR
  rename, Ant packaging implementation, internal refactoring, key
  files changed
