<!--
title: Ship Release Notes
description: Package user-facing release notes into the distribution artifact, keep developer notes in the repo, and link both from README and AGENTS.md — ensuring end users see version history without build internals.
category: Documentation & Packaging
-->

# Ship Release Notes Skill

> **Skill ID:** `ship_release_notes`
> **Version:** 2.0.0
> **Standard:** [Agent Skills (agentskills.io)](https://agentskills.io)

## Description

Configure a project's build system to include **user-facing** release
note files (`RELEASE_NOTES_*.md`) in the distribution artifact while
keeping **developer-only** notes (`DEV_NOTES_*.md`) in the repository.
Add a Release Notes section to `README.md` (shipped) that links to the
user-facing files, and optionally link the developer notes from
`AGENTS.md` (not shipped).

Release notes are one of the few developer-authored documents that
cross the user/developer boundary — they are written by developers
but consumed by end users.  This skill ensures they are:

1. **Split** into user-facing (`RELEASE_NOTES_*.md`) and developer-only
   (`DEV_NOTES_*.md`) files, living side by side in `releases/`.
2. **Packaged** — only `RELEASE_NOTES_*.md` files are copied into the
   distribution artifact by the build system.
3. **Linked** — `README.md` links to user-facing files;
   `AGENTS.md` links to developer notes.
4. **Gitignore-safe** — both file types are tracked even if the
   `releases/` directory is partially ignored for build output.

### Companion Skills

| Skill | Relationship |
|---|---|
| `generate_release_notes` | Covers **authoring** release notes — content rules, user/dev boundary, templates.  Apply that skill first to write the notes, then this skill to ship them. |
| `split_user_vs_dev_docs` | Same user/dev boundary principle applied to `README.md` and `AGENTS.md`. |

## Prerequisites

| Requirement | Minimum |
|---|---|
| Build System | Ant, Maven, Gradle, Make, or equivalent |
| VCS | Git |
| Existing | `releases/` directory with `RELEASE_NOTES_*.md` files |
| Existing | `README.md` in project root |
| Recommended | `AGENTS.md` in project root (for dev note links) |

## When to Apply

Apply this skill when:

- The project has release notes in `releases/` but they are not
  included in the distribution artifact
- End users ask "what changed in this version?" and have no way to
  find out from the shipped product
- `README.md` has no Release Notes section
- The build script copies `README.md` to the release but not the
  release notes
- `.gitignore` rules for `releases/` accidentally exclude the
  release note files
- `DEV_NOTES_*.md` files exist but are accidentally shipped
  to end users

Do NOT apply when:

- Release notes are managed externally (e.g., GitHub Releases, Jira)
- The project uses an auto-generated changelog
  (e.g., `conventional-changelog`)
- The distribution mechanism has its own release notes display
  (e.g., app store listing)

---

## Step-by-Step Procedure

### Step 1 — Establish the Dual-File Convention

Every version gets **two** files in `releases/`:

```
releases/
├── RELEASE_NOTES_1.3.0.md     ← shipped to end users
├── DEV_NOTES_1.3.0.md         ← stays in repo only
├── RELEASE_NOTES_1.4.0.md
├── DEV_NOTES_1.4.0.md
├── RELEASE_NOTES_1.5.0.md
├── DEV_NOTES_1.5.0.md
└── PLC_Converter_1.5.0.zip    (build output — gitignored)
```

#### Naming Convention

```
RELEASE_NOTES_{MAJOR}.{MINOR}.{PATCH}.md   ← user-facing, shipped
DEV_NOTES_{MAJOR}.{MINOR}.{PATCH}.md       ← developer-only, repo
```

- Uppercase prefix — consistent, grep-able, sorts together.
- Version number matches the release version exactly.
- The `RELEASE_NOTES_` vs `DEV_NOTES_` prefix is the **sole
  mechanism** that controls what ships — the build glob
  `includes="RELEASE_NOTES_*.md"` naturally excludes `DEV_NOTES_*`.

### Step 2 — Configure Gitignore for Releases

The `releases/` directory contains tracked files (notes) and
gitignored files (build output zips, exploded directories).

```gitignore
# Ignore exploded release directories and zip files (build output)
releases/*/

# Track release notes and developer notes
!releases/RELEASE_NOTES_*.md
!releases/DEV_NOTES_*.md
```

Verify both types are tracked:

```powershell
git ls-files releases/
# Expected: RELEASE_NOTES_*.md and DEV_NOTES_*.md files listed
```

If files are missing from `git ls-files`, force-add them:

```powershell
git add -f releases/RELEASE_NOTES_*.md releases/DEV_NOTES_*.md
```

### Step 3 — Update the Build Script

Modify the build/packaging script to copy **only user-facing** release
notes into the distribution artifact.

#### Ant (build.xml / PLCworkspace.xml)

```xml
<!-- Inside the release target, after copying other files -->
<mkdir dir="${release.dir}/releases"/>
<copy todir="${release.dir}/releases">
    <fileset dir="${dir.releases}" includes="RELEASE_NOTES_*.md"/>
</copy>
```

#### Maven (maven-assembly-plugin)

```xml
<fileSet>
    <directory>${project.basedir}/releases</directory>
    <outputDirectory>releases</outputDirectory>
    <includes>
        <include>RELEASE_NOTES_*.md</include>
    </includes>
</fileSet>
```

#### Gradle (distribution plugin)

```groovy
distributions {
    main {
        contents {
            from('releases') {
                include 'RELEASE_NOTES_*.md'
                into 'releases'
            }
        }
    }
}
```

#### Makefile

```makefile
release:
	mkdir -p $(RELEASE_DIR)/releases
	cp releases/RELEASE_NOTES_*.md $(RELEASE_DIR)/releases/
```

**Key principle:** The glob `RELEASE_NOTES_*.md` automatically includes
new release notes and automatically excludes `DEV_NOTES_*.md` — no
build script edits needed for either.

### Step 4 — Add Release Notes Section to README

Add a Release Notes section to `README.md` (shipped) with a table
that includes **Status** and user-facing **Notes** columns.

```markdown
## Release Notes

| Version | Status | Notes |
|---|---|---|
| [1.6.0](releases/RELEASE_NOTES_1.6.0.md) | In development | Unified 4-argument CLI, release notes included with product |
| [1.5.0](releases/RELEASE_NOTES_1.5.0.md) | Packed | Minimum Java version raised to 11 |
| [1.4.0](releases/RELEASE_NOTES_1.4.0.md) | Packed | PIB mode stability |
| [1.3.0](releases/RELEASE_NOTES_1.3.0.md) | Deployed (toolbase) | DCM generator, HEX generation |
```

#### README Table Rules

- **Newest first** — latest version at the top of the table.
- **Relative links** — use `releases/RELEASE_NOTES_*.md`, not absolute
  paths.  Links work in both the repository and the shipped release.
- **Status column** — lifecycle state visible to end users
  (e.g., "In development", "Packed", "Deployed").
- **Notes column** — one-line user-facing summary.  No internal tool
  names, no implementation details, no build system references.
- **No DEV_NOTES links** — `README.md` must never link to
  `DEV_NOTES_*.md`.  Those links would break in the shipped product.
- **Manual maintenance** — update the table when creating a new
  release.  This is intentional — it forces a conscious decision.

### Step 5 — Link Developer Notes from AGENTS.md (Optional)

If the project has `AGENTS.md`, add a reference so developers can
find the developer notes:

```markdown
## Release Notes Convention

- `releases/RELEASE_NOTES_*.md` — user-facing, shipped in release
- `releases/DEV_NOTES_*.md` — developer-only, not shipped
```

This ensures developer notes are discoverable without polluting
the shipped product.

### Step 6 — Verify the Release Artifact

Build the release and inspect the result:

```powershell
# Build the release
ant -f packaging/PLCworkspace.xml release

# List the release contents
Expand-Archive releases/Product_1.6.0.zip -DestinationPath temp_check
Get-ChildItem temp_check -Recurse -Filter "*.md" | Select-Object FullName
```

Expected output:

```
temp_check/Product_1.6.0/README.md
temp_check/Product_1.6.0/releases/RELEASE_NOTES_1.3.0.md
temp_check/Product_1.6.0/releases/RELEASE_NOTES_1.4.0.md
temp_check/Product_1.6.0/releases/RELEASE_NOTES_1.5.0.md
temp_check/Product_1.6.0/releases/RELEASE_NOTES_1.6.0.md
```

Verify:

1. ✅ `README.md` is present at the release root.
2. ✅ `releases/` contains all `RELEASE_NOTES_*.md` files.
3. ❌ `releases/` does NOT contain any `DEV_NOTES_*.md` files.
4. ❌ `AGENTS.md` is NOT present in the release.
5. ✅ Links in `README.md` resolve correctly within the release.

### Step 7 — Test Link Resolution

Open the shipped `README.md` in a Markdown viewer and verify each
release note link resolves:

```powershell
# Verify link targets exist
$readmeDir = "temp_check/Product_1.6.0"
Select-String -Path "$readmeDir/README.md" -Pattern 'releases/RELEASE_NOTES_[^)]+' -AllMatches |
    ForEach-Object { $_.Matches.Value } |
    ForEach-Object {
        $target = Join-Path $readmeDir $_
        if (-not (Test-Path $target)) {
            Write-Warning "Broken link: $_"
        }
    }
```

Also verify no DEV_NOTES leaked into the release:

```powershell
# Must return nothing
Get-ChildItem $readmeDir -Recurse -Filter "DEV_NOTES_*"
```

---

## Verification Checklist

| # | Check | Pass |
|---|---|---|
| 1 | Release notes follow `RELEASE_NOTES_{VERSION}.md` naming | ☐ |
| 2 | Developer notes follow `DEV_NOTES_{VERSION}.md` naming | ☐ |
| 3 | Both file types are tracked by git (not gitignored) | ☐ |
| 4 | Build script copies `RELEASE_NOTES_*.md` to release artifact | ☐ |
| 5 | Build script uses glob (not hardcoded filenames) | ☐ |
| 6 | `DEV_NOTES_*.md` files are NOT in the release artifact | ☐ |
| 7 | `AGENTS.md` is NOT in the release artifact | ☐ |
| 8 | `README.md` has Release Notes table with Status column | ☐ |
| 9 | README table links use relative paths | ☐ |
| 10 | README table is ordered newest-first | ☐ |
| 11 | README table Notes column has no internal tool names | ☐ |
| 12 | README does NOT link to `DEV_NOTES_*.md` | ☐ |
| 13 | Links in shipped `README.md` resolve within the release | ☐ |
| 14 | Release artifact contains `releases/` with note files | ☐ |

---

## Anti-Patterns

| Pattern | Why It Fails |
|---|---|
| Hardcoding release note filenames in build script | New releases require build script edits; easy to forget |
| Putting release notes in project root | Clutters root; no separation between tracked notes and build output |
| `.gitignore` blanket-ignoring `releases/` | Release notes become untracked; lost on clone |
| Embedding full release notes in README | README grows unbounded; version history buries usage docs |
| Linking to release notes from README without shipping them | Broken links in the distributed product |
| Changelog auto-generation without review | Commit messages are developer-facing; release notes need user-facing language |
| Shipping `DEV_NOTES_*.md` in the release | Exposes internal tool names, implementation details, and build internals to end users |
| Linking `DEV_NOTES_*.md` from `README.md` | Links break in the shipped product (DEV_NOTES are not included) |
| Mixing user and dev content in one file | Forces a binary ship/don't-ship decision — either users see internals or developers lose context |
| README Notes column with implementation details | "Central constants", "ConversionMode enum" mean nothing to end users |
| Omitting Status column from README table | Users lose visibility into which versions are deployed, packed, or in development |

---

## Reference Implementation

The PLC Converter project applies this skill:

- **User-facing**: `releases/RELEASE_NOTES_1.3.0.md` through
  `RELEASE_NOTES_1.6.0.md` — shipped in release
- **Developer-only**: `releases/DEV_NOTES_1.3.0.md` through
  `DEV_NOTES_1.6.0.md` — repo only
- **Build script**: `packaging/PLCworkspace.xml` —
  `includes="RELEASE_NOTES_*.md"` naturally excludes `DEV_NOTES_*`
- **README.md**: Release Notes table with Version, Status, Notes columns
  (newest-first, relative links, user-facing summaries only)
- **AGENTS.md**: Documents the dual-file convention for developers
- **Gitignore**: `releases/*/` ignores exploded dirs;
  `!releases/RELEASE_NOTES_*.md` and `!releases/DEV_NOTES_*.md`
  track note files

### Release layout (shipped)

```
PLC_Converter_1.6.0/
├── README.md
├── releases/
│   ├── RELEASE_NOTES_1.3.0.md
│   ├── RELEASE_NOTES_1.4.0.md
│   ├── RELEASE_NOTES_1.5.0.md
│   └── RELEASE_NOTES_1.6.0.md
├── jars/
├── tools/
└── PLC_Converter.cmd
```

### Repository layout (not shipped)

```
releases/
├── RELEASE_NOTES_1.3.0.md     ← shipped
├── DEV_NOTES_1.3.0.md         ← NOT shipped
├── RELEASE_NOTES_1.4.0.md     ← shipped
├── DEV_NOTES_1.4.0.md         ← NOT shipped
├── RELEASE_NOTES_1.5.0.md     ← shipped
├── DEV_NOTES_1.5.0.md         ← NOT shipped
├── RELEASE_NOTES_1.6.0.md     ← shipped
└── DEV_NOTES_1.6.0.md         ← NOT shipped
```
