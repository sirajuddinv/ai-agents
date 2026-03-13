<!--
title: Split User vs Dev Docs
description: Separate user-facing README from developer-only documentation — ensuring the shipped product exposes no build internals, tool details, or internal architecture.
category: Documentation & Packaging
-->

# Split User vs Dev Docs Skill

> **Skill ID:** `split_user_vs_dev_docs`
> **Version:** 1.0.0
> **Standard:** [Agent Skills (agentskills.io)](https://agentskills.io)

## Description

Audit a project's `README.md` to identify content that is developer-only
(build instructions, project structure, internal tool details, CI/CD
setup) and separate it from user-facing content (quick start, modes,
requirements, features). The developer content moves to `AGENTS.md`
and internal doc files; the `README.md` becomes a clean, shippable
end-user document.

This matters because `README.md` typically ships inside the release
distribution (zip, tarball, installer). Exposing build internals,
internal tool names, or project structure to end users is unprofessional,
confusing, and potentially a security concern.

## Prerequisites

| Requirement | Minimum |
|---|---|
| Files | `README.md` exists in project root |
| VCS | Git (for tracking moves and edits) |
| Context | Understanding of the project's release/distribution mechanism |

## When to Apply

Apply this skill when:

- `README.md` ships inside a release zip or installer
- `README.md` contains "Building from Source" or "Project Structure"
  sections alongside end-user content
- Internal tool names (e.g., `nvmsplit.exe`, CI pipeline names) appear
  in `README.md`
- Developer setup instructions (IDE config, logging frameworks, test
  data locations) appear in `README.md`
- The project has both end users and developers as audiences but only
  one README serving both

Do NOT apply when:

- The project is a library consumed only by developers (README IS the
  developer doc)
- The project does not ship `README.md` to end users
- `README.md` is already clean and `AGENTS.md` already holds dev content
- The project explicitly wants a single comprehensive README

---

## Step-by-Step Procedure

### Step 1 — Identify the Distribution Boundary

Determine how the product is delivered to end users and which files
ship in the distribution:

```powershell
# Check the build/packaging script for files copied to release
Select-String -Path packaging/*.xml, Makefile, *.gradle -Pattern "README|copy|include" -Recurse
```

If `README.md` is copied into the release artifact, it MUST contain
only user-facing content.

### Step 2 — Classify Every README Section

Read the current `README.md` and classify each H2 section:

| Classification | Belongs In | Examples |
|---|---|---|
| **User-facing** | `README.md` | Quick Start, Modes/Usage, Requirements, Features, License, Maintainer |
| **Developer-only** | `AGENTS.md` | Building from Source, Project Structure, Contributing, Architecture |
| **Internal tooling** | `AGENTS.md` or `docs/` | Logging framework setup, NVM splitter internals, CI/CD config |
| **Release history** | `README.md` (if shipped) or `releases/` | Release Notes, Changelog |

#### Classification Rules

Content is **user-facing** if an end user running the shipped product
would need or benefit from it.

Content is **developer-only** if it requires source code access, build
tools, or internal knowledge to be useful.

**Grey areas:**

- **Release Notes** — user-facing if they describe features and fixes
  the user cares about. Ship them.
- **Configuration** — user-facing if the user configures the tool at
  runtime. Developer-only if it's build-time or IDE configuration.
- **Troubleshooting** — user-facing if it covers runtime errors.
  Developer-only if it covers build errors.

### Step 3 — Strip Developer Content from README

Remove each developer-only section from `README.md`. Do NOT delete
the content — capture it for transfer to `AGENTS.md`.

**Sections to remove (typical):**

1. **Building from Source** — prerequisites, compile commands, IDE setup
2. **Project Structure** — directory tree, package descriptions
3. **Internal Tool Details** — names of internal executables, their
   purpose, how they work under the hood
4. **Documentation Links** — links to internal design docs, UML
   diagrams, investigation notes
5. **Logging/Telemetry Setup** — internal logging framework config
6. **Contributing** — dev workflow, PR process, code style

**Also audit remaining sections for leaked internals:**

```powershell
# Search for internal tool names that should not appear in user README
Select-String -Path README.md -Pattern "nvmsplit|srec_cat|\.classpath|\.project|tul_logging"
```

Remove any references to:
- Internal executable names not visible to end users
- IDE-specific files (`.classpath`, `.project`, `.settings/`)
- Internal logging/telemetry framework names
- Build tool invocations (`ant`, `mvn`, `gradle` commands)
- Internal package/class names

### Step 4 — Ensure README Has All Required User Sections

After stripping, verify the README contains these mandatory sections:

| # | Section | Content |
|---|---|---|
| 1 | `# Product Name` | H1 title |
| 2 | Description | 2–3 sentence overview |
| 3 | `## Quick Start` | The primary usage command from the user's perspective |
| 4 | `## Modes` or `## Usage` | Table or list of all modes with descriptions |
| 5 | `## Requirements` | Runtime requirements only (e.g., Java 8+) |
| 6 | `## Features` | Bullet list of user-visible capabilities |
| 7 | `## Release Notes` | Links to release note files (if shipped) |
| 8 | `## License` | License name |
| 9 | `## Maintainer` | Name and contact |

**Quick Start must reflect the end-user invocation**, not the developer
"run from source" command. If the tool is distributed via a corporate
toolbase:

```markdown
## Quick Start

```bat
C:\toolbase\PLC_Converter\PLC_Converter.cmd <ARG1> <ARG2> <OUTPUT_DIR> <MODE>
```

### Step 5 — Transfer Developer Content to AGENTS.md

Add the removed sections to `AGENTS.md` under appropriate headings.
`AGENTS.md` is the developer/AI-agent guide and is NOT shipped in the
release.

Typical `AGENTS.md` structure after transfer:

```markdown
# AGENTS.md

## Conventions
- Naming conventions, coding standards

## Internal Notes
- Internal tool details (e.g., NVM splitter purpose)

## Building from Source
### Prerequisites
### Eclipse
### Ant — build JAR
### Command Line (compile and run)

## Project Structure
(annotated directory tree)

## Documentation
| Document | Description |
|---|---|
| docs/SETUP.md | Internal setup guide |
| docs/UML.png | Class diagram |
```

### Step 6 — Update Build Scripts

If the build/packaging script copies `README.md` to the release, verify
it does NOT also copy `AGENTS.md` or `docs/`:

```powershell
Select-String -Path packaging/*.xml -Pattern "AGENTS|docs/"
# Expected: no matches
```

### Step 7 — Verify the Split

#### 7a — README Contains No Developer Content

```powershell
# These patterns should NOT appear in README.md
$devPatterns = @(
    "Building from Source", "Project Structure",
    "javac", "ant ", "mvn ", "gradle ",
    ".classpath", ".project", ".settings",
    "src/com/", "bin/", "dist/"
)
foreach ($p in $devPatterns) {
    $found = Select-String -Path README.md -Pattern $p -Quiet
    if ($found) { Write-Warning "README.md contains dev content: $p" }
}
```

#### 7b — AGENTS.md Contains All Developer Content

Verify every section removed from README exists in AGENTS.md:

```powershell
$devSections = @(
    "Building from Source", "Project Structure",
    "Prerequisites", "Documentation"
)
foreach ($s in $devSections) {
    $found = Select-String -Path AGENTS.md -Pattern $s -Quiet
    if (-not $found) { Write-Warning "AGENTS.md missing section: $s" }
}
```

#### 7c — Release Artifact Contains Only User Content

Build the release and inspect:

```powershell
# After building the release zip
Expand-Archive releases/Product_1.0.0.zip -DestinationPath temp_check
Get-ChildItem temp_check -Recurse -Filter "*.md" | Select-Object FullName
# Expected: only README.md and RELEASE_NOTES_*.md — no AGENTS.md
```

---

## Verification Checklist

| # | Check | Pass |
|---|---|---|
| 1 | README.md contains only user-facing sections | ☐ |
| 2 | No internal tool names in README.md | ☐ |
| 3 | No build commands in README.md | ☐ |
| 4 | No IDE-specific file references in README.md | ☐ |
| 5 | Quick Start shows end-user invocation path | ☐ |
| 6 | AGENTS.md has Building from Source section | ☐ |
| 7 | AGENTS.md has Project Structure section | ☐ |
| 8 | AGENTS.md has Documentation links | ☐ |
| 9 | Build script does NOT copy AGENTS.md to release | ☐ |
| 10 | Release zip contains README.md but not AGENTS.md | ☐ |

---

## Anti-Patterns

| Pattern | Why It Fails |
|---|---|
| Single README for all audiences | End users see build internals; developers wade through usage docs |
| Moving user content to AGENTS.md | End users get an empty README; AGENTS.md is not shipped |
| Keeping "Building from Source" in README "for completeness" | Ships internal details; end users cannot build from source anyway |
| Removing developer content without transferring it | Knowledge is lost; next developer starts from scratch |
| Referencing `docs/` files from README | If `docs/` is not shipped, the links are broken for end users |

---

## Reference Implementation

The PLC Converter project applied this skill to split a combined README
into user-facing and developer-only documents:

**Removed from README.md:**
- NVM Splitter internal details
- Building from Source (prerequisites, Eclipse, Ant, CLI commands)
- Project Structure (full directory tree)
- Documentation links (TUL_SETUP.md, UML diagram, investigation notes)
- TUL Configuration section (internal logging framework)

**Kept in README.md:**
- Quick Start (unified 4-arg CLI with NA)
- Modes table (user-visible mode names and descriptions)
- Requirements (Java 8+)
- Features (user-visible capabilities)
- Release Notes (links to shipped release note files)
- License and Maintainer

**Transferred to AGENTS.md:**
- Internal Notes (NVM Split purpose)
- Building from Source (full section with prerequisites table)
- Project Structure (annotated directory tree)
- Documentation (table linking to internal docs)
