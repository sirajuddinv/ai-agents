<!--
title: Reference Workspace Comparison
description: Systematic cross-validation of build/metadata fixes by comparing
    a working repository against one or more known-good reference workspaces
    that predate the migration — covering feature.xml, MANIFEST.MF, and Java
    source layers with per-artifact delta reports.
category: Build & Dependency Management
-->

# Reference Workspace Comparison Skill

> **Skill ID:** `reference_workspace_comparison`
> **Version:** 1.0.0
> **Standard:** [Agent Skills (agentskills.io)](https://agentskills.io)

## Description

Perform systematic cross-validation of build metadata changes
(e.g., bundle version pins, dependency declarations, plugin
entries) by comparing a **working repository** against one or more
**reference workspaces** that represent a known-good state from a
previous platform version.

This skill is essential during Eclipse/Tycho target platform
migrations, where fixes applied to `feature.xml`, `MANIFEST.MF`,
or Java source must be validated against the original
configuration that worked on the older platform. The comparison
answers two critical questions:

1. **Was the fix correct?** — Does the working repo's new state
   diverge from the reference only in the expected, intentional
   ways?
2. **Are there remaining gaps?** — Does the reference reveal
   additional artifacts (bundles, imports, version constraints)
   that the working repo has not yet addressed?

**Key design principle:** Reference workspaces are read-only
evidence. They are never modified. All fixes are applied
exclusively to the working repository.

### Typical Use Cases

- Validating `feature.xml` plugin entry changes after removing
  or consolidating obsolete bundles
- Confirming `MANIFEST.MF` `Require-Bundle` / `Import-Package`
  entries match the reference before and after migration fixes
- Detecting version-constraint mismatches (e.g., a reference uses
  `bundle-version="4.3.0"` but the new platform only ships 3.x)
- Cross-checking Java source imports to ensure no bundle removal
  breaks compilation

## Related Skills

| Skill | Relationship |
|---|---|
| [`eclipse_target_platform_migration`](../eclipse_target_platform_migration/SKILL.md) | Primary consumer — migration fixes are validated by this comparison skill |
| [`maven_build_failure_analysis`](../maven_build_failure_analysis/SKILL.md) | Complementary — provides error parsing; this skill validates the fix |
| [`local_p2_repository_rollback`](../local_p2_repository_rollback/SKILL.md) | Alternative — when comparison reveals a bundle must be preserved rather than removed |
| [`git_atomic_commit`](../git_atomic_commit/SKILL.md) | Used after — commit validated fixes atomically |

## Prerequisites

| Requirement | Minimum |
|---|---|
| Shell | PowerShell 5.1+ or Bash 4+ |
| VCS | Git 2.x+ (working repo must be under Git) |
| Reference workspaces | ≥ 1 directory tree with the same project structure (need not be Git repos — IBM ALM / Jazz SCM exports are valid) |
| Build system | Maven/Tycho (Eclipse PDE) — for context, not execution |

## When to Apply

Apply this skill when:

- A migration fix has been applied to `feature.xml`, `MANIFEST.MF`,
  or Java source and needs validation against a pre-migration
  baseline
- Multiple reference workspaces exist (e.g., different project
  variants or historical snapshots) and the agent must confirm
  consistency across all of them
- The reference workspaces are **not Git repositories** (e.g.,
  IBM ALM / Jazz SCM exports, filesystem snapshots) and cannot be
  compared via `git diff`
- A user asks to "check the fix against the old workspace" or
  "compare with the working version"

Do NOT apply when:

- Both codebases are Git repositories on the same remote — use
  `git diff <branch>..<branch>` instead
- The comparison is a general folder-level duplication check with
  no build-metadata focus — use the
  [folder-comparison](../../.agent/skills/folder-comparison/SKILL.md)
  skill instead
- The reference workspace does not contain the same project
  structure (different product, different feature set)

---

## Step-by-Step Procedure

### Step 1 — Inventory the Reference Workspaces

Before any comparison, the agent MUST build a complete inventory
of available reference workspaces and their structure.

#### 1.1 Enumerate Workspaces

List all reference workspace directories and identify which ones
contain the target project (e.g., the feature project, the bundle
project):

```powershell
# PowerShell — list reference workspace subdirectories
Get-ChildItem -Path "<reference-root>" -Directory |
    ForEach-Object { $_.Name }
```

#### 1.2 Locate Target Artifacts

For each reference workspace, locate the specific artifacts that
correspond to the working repo's changed files:

```powershell
# PowerShell — find feature.xml files across all references
Get-ChildItem -Path "<reference-root>" -Recurse `
    -Filter "feature.xml" |
    Select-Object FullName |
    Format-Table -AutoSize -Wrap
```

#### 1.3 Document Coverage Matrix

Build a coverage matrix showing which reference workspaces
contain which target projects:

| Reference Workspace | Has Feature X? | Has Bundle Y? | Notes |
|---|---|---|---|
| workspace_a | ✅ | ✅ | Main reference |
| workspace_b | ✅ | ❌ | Partial — missing test bundles |

**Mandatory:** If a reference workspace is missing a target
project, this MUST be documented. The absence itself is a
finding.

---

### Step 2 — Three-Layer Artifact Comparison

For each artifact under investigation (e.g., a specific bundle
like `org.antlr.runtime`), perform the comparison across the
same three layers used in blast-radius analysis.

#### 2.1 Layer 1 — feature.xml Comparison

Search for the artifact in `feature.xml` files across both
the working repo and all reference workspaces:

```powershell
# Working repo
Select-String -Path "<working-repo>/**/feature.xml" `
    -Pattern "<artifact-name>" -Recurse |
    Select-Object Filename, LineNumber, Line |
    Format-Table -AutoSize -Wrap

# All reference workspaces
Get-ChildItem -Path "<reference-root>" -Recurse `
    -Filter "feature.xml" |
    Select-String -Pattern "<artifact-name>" |
    Select-Object Filename, LineNumber, Line |
    Format-Table -AutoSize -Wrap
```

Compare:

- **Plugin entry presence** — Is the `<plugin>` element present
  in both?
- **Version pin** — Does the reference use a specific version
  (e.g., `4.3.0.v201502022030`) vs. the working repo's
  `version="0.0.0"`?
- **Entry count** — Does the reference have multiple entries for
  the same plugin ID (common for ANTLR, JUnit, etc.)?
- **Attributes** — `unpack`, `fragment`, `os` filters

#### 2.2 Layer 2 — MANIFEST.MF Comparison

Search for the artifact in `MANIFEST.MF` files:

```powershell
# Working repo
Get-ChildItem -Path "<working-repo>" -Recurse `
    -Filter "MANIFEST.MF" |
    Select-String -Pattern "<artifact-name>" |
    Select-Object Filename, LineNumber, Line |
    Format-Table -AutoSize -Wrap

# All reference workspaces
Get-ChildItem -Path "<reference-root>" -Recurse `
    -Filter "MANIFEST.MF" |
    Select-String -Pattern "<artifact-name>" |
    Select-Object Filename, LineNumber, Line |
    Format-Table -AutoSize -Wrap
```

Compare:

- **Require-Bundle** — Same bundle, same version constraint?
- **Import-Package** — Any differences in package-level imports?
- **Bundle presence** — Does the reference have the bundle in
  additional MANIFEST.MF files that the working repo does not?

#### 2.3 Layer 3 — Java Source Comparison

Search for package imports from the artifact:

```powershell
# Working repo
Get-ChildItem -Path "<working-repo>" -Recurse `
    -Filter "*.java" |
    Select-String -Pattern "import.*<package-prefix>" |
    Select-Object Filename, LineNumber, Line |
    Format-Table -AutoSize -Wrap

# All reference workspaces
Get-ChildItem -Path "<reference-root>" -Recurse `
    -Filter "*.java" |
    Select-String -Pattern "import.*<package-prefix>" |
    Select-Object Filename, LineNumber, Line |
    Format-Table -AutoSize -Wrap
```

Compare:

- **Same import set?** — Are the Java imports identical?
- **Additional consumers?** — Does any reference workspace show
  imports in bundles that the working repo does not?

---

### Step 3 — Delta Classification

For each artifact, classify the comparison result into one of
these categories:

| Category | Meaning | Action |
|---|---|---|
| **✅ Identical** | Working repo matches all references | No action needed — fix is validated |
| **⬅ Intentional Divergence** | Working repo differs from references, but the difference is the migration fix itself | Document as expected — the fix is correct |
| **⚠️ Unintentional Divergence** | Working repo differs from references in ways not explained by the migration | Investigate — possible regression or missed fix |
| **🔴 Reference-Only** | Artifact exists in references but not in working repo | Investigate — may indicate an accidental deletion |
| **🔵 Working-Only** | Artifact exists in working repo but not in references | Investigate — may be a new addition or error |

#### 3.1 Documenting Deltas

Each delta MUST be documented in a structured table:

| Artifact | Layer | Working Repo | Reference (all N) | Category | Notes |
|---|---|---|---|---|---|
| `org.antlr.runtime` | feature.xml | 1× `version="0.0.0"` | 2× pinned versions | ⬅ Intentional | Migration fix consolidated entries |
| `org.antlr.runtime` | MANIFEST.MF (generator) | `org.antlr.runtime,` | `org.antlr.runtime,` | ✅ Identical | No change needed |

#### 3.2 Cross-Reference Consistency

When multiple reference workspaces exist, the agent MUST check
whether the references themselves are consistent:

- If all N references agree → strong baseline confidence
- If references disagree → document the variant(s) and determine
  which represents the canonical baseline

---

### Step 4 — Version Constraint Risk Assessment

When the migration changes version resolution (e.g., pinned →
floating, or platform ships a different version), the agent MUST
assess downstream risk.

#### 4.1 Identify Version-Constrained Consumers

Search all `MANIFEST.MF` files in the working repo for
`bundle-version` constraints on the migrated artifact:

```powershell
Get-ChildItem -Path "<working-repo>" -Recurse `
    -Filter "MANIFEST.MF" |
    Select-String -Pattern "<artifact-name>.*bundle-version" |
    Select-Object Filename, LineNumber, Line |
    Format-Table -AutoSize -Wrap
```

#### 4.2 Determine Risk Level

| Constraint | Platform Ships | Risk |
|---|---|---|
| `bundle-version="4.3.0"` (≥ 4.3.0) | 4.x | 🟢 Safe |
| `bundle-version="4.3.0"` (≥ 4.3.0) | 3.x only | 🔴 Will fail |
| No version constraint | Any | 🟢 Safe |

#### 4.3 Report Downstream Risks

Any identified risk MUST be reported to the user with:

- The exact MANIFEST.MF file and line number
- The constraint that may break
- The expected vs. available version in the new platform
- Recommended fix (relax constraint, remove constraint, or use
  local p2 rollback)

---

### Step 5 — Batch Comparison (Multi-Artifact)

When multiple artifacts need comparison (common during major
platform migrations), use batch processing for efficiency.

#### 5.1 Extract All Plugin IDs from feature.xml

```powershell
# Extract plugin IDs from working repo's feature.xml
Select-String -Path "<feature.xml>" `
    -Pattern 'id="([^"]+)"' |
    ForEach-Object { $_.Matches[0].Groups[1].Value } |
    Sort-Object -Unique
```

#### 5.2 Cross-Reference Against References

For each plugin ID, check presence in all reference workspaces:

```powershell
$pluginIds = @("org.antlr.runtime", "org.w3c.css.sac", ...)

foreach ($id in $pluginIds) {
    $refHits = Get-ChildItem -Path "<reference-root>" `
        -Recurse -Filter "feature.xml" |
        Select-String -Pattern $id

    [PSCustomObject]@{
        PluginId  = $id
        RefCount  = $refHits.Count
        RefFiles  = ($refHits | ForEach-Object {
            $_.Filename
        }) -join ", "
    }
} | Format-Table -AutoSize -Wrap
```

#### 5.3 Identify Orphans

Plugins present in the working repo but absent from **all**
references may be accidental additions. Plugins present in
references but absent from the working repo may indicate
premature removal.

---

### Step 6 — Reporting

The agent MUST present a final comparison report with:

#### 6.1 Summary Table

| # | Artifact | Layers Compared | Result | Risk |
|---|---|---|---|---|
| 1 | `org.antlr.runtime` | feature.xml, MANIFEST.MF, Java | ⬅ Intentional divergence in feature.xml; ✅ identical elsewhere | ⚠️ Downstream version constraint |
| 2 | `org.w3c.css.sac` | feature.xml | ✅ Identical | 🟢 None |

#### 6.2 Reference Workspace Coverage

| Reference | Artifacts Covered | Notes |
|---|---|---|
| 06saturn | 10/10 | Full coverage |
| dgs_ice | 10/10 | Full coverage |
| ics_alm_fresh | 7/10 | Missing timedcom bundles |

#### 6.3 Actionable Findings

List any findings that require user action:

- **Unintentional divergences** — with recommended fixes
- **Downstream risks** — with specific MANIFEST.MF lines
- **Reference inconsistencies** — with explanation of which
  reference to trust

---

## Scope Coverage

| Category | Convention |
|---|---|
| feature.xml plugin entries | Compare presence, version pins, attributes, entry count |
| MANIFEST.MF Require-Bundle | Compare bundle name, version constraint, position |
| MANIFEST.MF Import-Package | Compare package list and version ranges |
| Java source imports | Compare import statements for artifact packages |
| Version constraint risk | Assess downstream MANIFEST.MF constraints against new platform |
| Multi-workspace consistency | Verify all references agree before using as baseline |

---

## Prohibited Behaviors

The agent is **BLOCKED** from:

- **Modifying reference workspaces** — References are read-only
  evidence; all fixes go to the working repository only
- **Assuming reference correctness without verification** — If
  references disagree with each other, the agent MUST flag the
  inconsistency rather than silently picking one
- **Skipping layers in comparison** — All three layers
  (feature.xml, MANIFEST.MF, Java source) MUST be checked even
  if the change appears limited to one layer
- **Reporting only matches** — Negative results (artifact NOT
  found in a reference) are critical findings and MUST be
  explicitly documented
- **Comparing without an inventory** — The coverage matrix
  (Step 1.3) MUST be built before any artifact comparison begins
- **Mixing comparison with fix execution** — This skill produces
  a validated comparison report; fixes are applied by the
  [`eclipse_target_platform_migration`](../eclipse_target_platform_migration/SKILL.md)
  skill or manually by the user

---

## Common Pitfalls

| Pitfall | Solution |
|---|---|
| Reference workspace excluded by `.gitignore` or IDE search settings | Use `includeIgnoredFiles` flag or direct filesystem commands (`Get-ChildItem`) |
| Reference workspaces are IBM ALM / Jazz SCM exports, not Git repos | This is expected — use filesystem search, not `git diff` |
| Multiple references have different versions of the same artifact | Document the variance; ask the user which is canonical |
| Reference has additional bundles not in the working repo | May be project-variant-specific (e.g., Ford vs. Saturn); cross-reference with the project's feature list |
| Working repo has post-migration additions absent from references | Expected for new platform bundles; classify as 🔵 Working-Only |
| Search misses due to MANIFEST.MF continuation lines (leading space) | Search for the bundle symbolic name without anchoring to line start |
| Version constraint uses OSGi range syntax `[1.0,2.0)` | Parse both floor and ceiling; compare against actual platform version |
