<!--
title: Maven Build Failure Analysis
description: Systematic diagnosis of Maven/Tycho build failures — dependency
    chain analysis, p2 repository inventory, artifact version discovery,
    and multi-level rollback strategies (version, bundle, dependency,
    feature, and component).
category: Build & Dependency Management
-->

# Maven Build Failure Analysis Skill

> **Skill ID:** `maven_build_failure_analysis`
> **Version:** 1.0.0
> **Standard:** [Agent Skills (agentskills.io)](https://agentskills.io)

## Description

Perform end-to-end diagnosis of Maven and Maven/Tycho (Eclipse PDE)
build failures caused by missing dependencies, unresolvable bundles,
or broken transitive dependency chains. This skill covers the full
investigation lifecycle: error parsing, dependency chain reconstruction,
repository inventory, artifact version discovery, root cause
identification, and structured rollback strategies at multiple
granularity levels.

The skill produces a comprehensive markdown investigation document
that captures every finding — error messages, dependency diagrams,
MANIFEST.MF comparisons, version timelines, rollback options with
trade-off analysis, and diagnostic commands — so the investigation
is fully reproducible and shareable with other teams.

**Scope boundary:** This skill covers general Maven/Tycho build
failure analysis and repository-based investigation. For
organization-specific artifact stores (e.g., toolbase directories),
use a complementary investigation skill layered on top.

## Related Skills

| Skill | Relationship |
|---|---|
| [`maven_pom_audit`](../maven_pom_audit/SKILL.md) | Complementary — audits POM structure; this skill diagnoses build failures |
| [`eclipse_pde_runtime_troubleshooting`](../eclipse_pde_runtime_troubleshooting/SKILL.md) | Complementary — handles runtime errors; this skill handles build-time errors |
| [`git_atomic_commit`](../git_atomic_commit/SKILL.md) | Used after — commit investigation documents |

## Prerequisites

| Requirement | Minimum |
|---|---|
| Maven | 3.6+ |
| Java | 8+ (for `jar` tool, `mvn` execution) |
| Shell | PowerShell 5.1+ or Bash 4+ |
| VCS | Git 2.x+ (for version history) |
| Build Type | Maven or Maven/Tycho (Eclipse PDE) |

## When to Apply

Apply this skill when:

- A Maven or Tycho build fails with `Cannot resolve project dependencies`
- Error messages contain `Missing requirement`, `Cannot satisfy dependency`,
  or `could not be found`
- A transitive dependency chain is broken (bundle A → B → C, where C
  is missing)
- A nightly/CI build that previously worked now fails without code changes
- A user asks to investigate why a dependency cannot be resolved
- A user asks to find available versions of a component or artifact
- A user asks to roll back a dependency, feature, or component

Do NOT apply when:

- The error is a compile error in the project's own source code (fix the code)
- The error is a runtime `ClassNotFoundException` or `NoClassDefFoundError`
  (use [`eclipse_pde_runtime_troubleshooting`](../eclipse_pde_runtime_troubleshooting/SKILL.md))
- The error is a POM syntax/structure issue (use
  [`maven_pom_audit`](../maven_pom_audit/SKILL.md))
- The build succeeds but produces incorrect output (different diagnosis)

---

## Step-by-Step Procedure

### Step 1 — Error Extraction & Classification

Parse the build output and extract all distinct errors. Classify each
error into one of the following categories:

| Category | Pattern | Example |
|---|---|---|
| **Missing Bundle** | `Missing requirement: <bundle> requires '<dependency>' but it could not be found` | Missing OSGi bundle in p2 repository |
| **Missing Package** | `Missing requirement: <bundle> requires 'java.package; <pkg>'` | Missing Java package export |
| **Version Conflict** | `Cannot satisfy dependency: <bundle> depends on <dep> [<range>] but found <version>` | Version range mismatch |
| **Missing Feature** | `Missing requirement: <feature>.feature.group requires '<dependency>'` | Feature includes unavailable plugin |
| **Repository Unreachable** | `Could not read p2 repository` / `Connection refused` / `404 Not Found` | p2 repository URL is invalid or down |
| **Parameter Warning** | `Unknown parameter '<name>'` | Deprecated Maven/Tycho parameter (non-blocking) |

#### 1.1 Error Extraction Template

For each distinct error, capture:

```markdown
### Error N — [Short Description]

**Module:** `<module-name>` (step M/N)
**Packaging:** `<eclipse-plugin|eclipse-feature|jar|...>`
**Error:**
\`\`\`
[paste exact error message]
\`\`\`
**Category:** [Missing Bundle | Missing Package | Version Conflict | ...]
**Blocking:** Yes / No (warning only)
```

#### 1.2 Deduplication

Multiple modules often fail with the same root cause. Group errors
by their **shared missing dependency** — do not treat each module's
error as independent.

---

### Step 2 — Dependency Chain Reconstruction

For each distinct missing dependency, reconstruct the full transitive
chain from the workspace bundle down to the missing artifact.

#### 2.1 Chain Levels

```
Level 0 — WORKSPACE BUNDLES (what we are building)
    │ depends on (Require-Bundle / Import-Package)
    ▼
Level 1 — DIRECT EXTERNAL DEPENDENCY (from a configured repository)
    │ depends on
    ▼
Level 2 — TRANSITIVE DEPENDENCY (from same or different repository)
    │ depends on
    ▼
Level N — MISSING ARTIFACT (not found in any configured source)
```

#### 2.2 Source of Dependency Information

| Build Type | Where to Find Dependencies |
|---|---|
| Maven (standard) | `pom.xml` → `<dependencies>` section |
| Tycho (eclipse-plugin) | `META-INF/MANIFEST.MF` → `Require-Bundle`, `Import-Package` |
| Tycho (eclipse-feature) | `feature.xml` → `<plugin>`, `<includes>`, `<requires>` |
| Tycho (eclipse-repository) | `category.xml` → `<feature>` entries |

#### 2.3 Scanning Workspace for Affected Bundles

Find ALL workspace bundles that depend on the problematic artifact:

```powershell
# Search MANIFEST.MF files for Require-Bundle references
Get-ChildItem -Recurse -Filter "MANIFEST.MF" |
    Select-String -Pattern "<bundle.symbolic.name>" |
    Select-Object Filename, LineNumber, Line |
    Format-Table -AutoSize -Wrap

# Search feature.xml files for plugin references
Get-ChildItem -Recurse -Filter "feature.xml" |
    Select-String -Pattern "<bundle.symbolic.name>" |
    Select-Object Filename, LineNumber, Line |
    Format-Table -AutoSize -Wrap
```

```bash
# Search MANIFEST.MF files
grep -rn "<bundle.symbolic.name>" --include="MANIFEST.MF" .

# Search feature.xml files
grep -rn "<bundle.symbolic.name>" --include="feature.xml" .
```

#### 2.4 Dependency Chain Diagram (ASCII)

Document the chain as an ASCII diagram in the investigation document.
Every level must include:
- Bundle symbolic name
- Version (including qualifier)
- Source repository
- The specific `Require-Bundle` / `Import-Package` declaration

---

### Step 3 — Repository Inventory

Catalog every dependency source configured in the build.

#### 3.1 Maven Repositories

Extract from `pom.xml` and `settings.xml`:

```powershell
# List all <repository> entries in the POM hierarchy
Select-String -Path pom.xml -Pattern "<repository>" -Context 0,5

# List repositories in settings.xml
Select-String -Path "$env:USERPROFILE\.m2\settings.xml" -Pattern "<repository>" -Context 0,5
```

#### 3.2 Tycho P2 Repositories

Extract from the Tycho aggregator POM:

```powershell
# List all p2 repositories configured in the Tycho POM
Select-String -Path "*/pom.xml" -Pattern "<layout>p2</layout>" -Context 5,0
```

For each p2 repository, document:

| # | Repository ID | URL Pattern | Parameterized? |
|---|---|---|---|
| 1 | `<id>` | `<url>` | Yes — uses `${variable}` / No — hardcoded |

#### 3.3 Repository Variable Resolution

If repository URLs use Maven properties (e.g., `${repository_Version}`),
determine where these are defined:

| Property Source | How to Check |
|---|---|
| Parent POM | `mvn help:effective-pom -Doutput=effective-pom.xml` |
| `settings.xml` | `Get-Content "$env:USERPROFILE\.m2\settings.xml"` |
| CI pipeline parameters | Check CI configuration (Jenkins, Azure DevOps, etc.) |
| Command-line `-D` flags | Check CI build scripts / Makefiles |

#### 3.4 Search for Missing Artifact in All Repositories

For each missing artifact, systematically search:

```powershell
# Maven local cache
Get-ChildItem "$env:USERPROFILE\.m2\repository" -Recurse -Filter "*<artifact-name>*" -ErrorAction SilentlyContinue |
    Select-Object FullName

# p2 repository contents (if ZIP archive is accessible)
$jarTool = "path\to\jar.exe"
& $jarTool tf "<repo-archive>.zip" | Select-String "<artifact-name>"
```

---

### Step 4 — Artifact Version Discovery

When a dependency was previously working, identify what version was
last known-good and what changed.

#### 4.1 Version Discovery Sources

Search for version information in this priority order:

| Priority | Source | What It Provides |
|---|---|---|
| 1 | **Build output** (current + previous CI logs) | Exact resolved version used in last working build |
| 2 | **Maven local cache** (`~/.m2/repository`) | Previously resolved versions |
| 3 | **Parent POM hierarchy** | Default version properties |
| 4 | **PDE `.target` files** | Historical version references |
| 5 | **Git history** | Previous POM/target configurations |
| 6 | **Repository manager** (Nexus, Artifactory) | All published versions |
| 7 | **Known-good product builds** | Bundle versions from a working product |

#### 4.2 Git History for Version Changes

```powershell
# Find when the dependency version last changed
git log --all -p -- "*/MANIFEST.MF" | Select-String -Pattern "<bundle.symbolic.name>" -Context 3

# Find when the POM repository URL changed
git log --all -p -- "*/pom.xml" | Select-String -Pattern "<repository-id>" -Context 5
```

```bash
git log --all -p -- "*/MANIFEST.MF" | grep -A3 -B3 "<bundle.symbolic.name>"
git log --all -p -- "*/pom.xml" | grep -A5 -B5 "<repository-id>"
```

#### 4.3 PDE Target Definition History

```powershell
# Find all .target files
Get-ChildItem -Recurse -Filter "*.target" | Select-Object FullName

# Search for component version references
Get-ChildItem -Recurse -Filter "*.target" |
    Select-String -Pattern "<component-name>" |
    Select-Object Filename, LineNumber, Line | Format-Table -AutoSize -Wrap
```

#### 4.4 Maven Local Cache Inspection

```powershell
# Check if any versions are cached locally
Get-ChildItem "$env:USERPROFILE\.m2\repository" -Recurse -Filter "*<artifact-name>*" -ErrorAction SilentlyContinue |
    Select-Object FullName

# For Tycho/p2 bundles — check the p2 local cache
Get-ChildItem "$env:USERPROFILE\.m2\repository\.cache\tycho" -Recurse -Filter "*<bundle-name>*" -ErrorAction SilentlyContinue |
    Select-Object FullName
```

---

### Step 5 — MANIFEST.MF Comparison (Tycho/OSGi builds)

For OSGi dependency issues, extract and compare the MANIFEST.MF of
the problematic bundle across versions to identify what changed.

#### 5.1 Extract MANIFEST.MF from a JAR

```powershell
$jarTool = "path\to\jar.exe"
$tempDir = "c:\temp\manifest_compare"
New-Item -ItemType Directory -Path $tempDir -Force | Out-Null
Push-Location $tempDir

# Extract from a known-good JAR
& $jarTool xf "<path-to-known-good.jar>" META-INF/MANIFEST.MF
Get-Content "META-INF\MANIFEST.MF"

Pop-Location
```

#### 5.2 Key Fields to Compare

| MANIFEST.MF Field | What to Check |
|---|---|
| `Bundle-Version` | Version qualifier (timestamp) — confirms build date |
| `Require-Bundle` | New entries = new dependencies that may be missing |
| `Import-Package` | New entries = new package requirements |
| `Export-Package` | Removed entries = consumers may break |
| `Bundle-RequiredExecutionEnvironment` | Changed JRE requirement |
| `Bundle-ActivationPolicy` | Changed from `lazy` to eager or vice versa |

#### 5.3 Diff Template

```markdown
**Old version — X.Y.Z.QUALIFIER (DATE) ✅ WORKS:**
Require-Bundle:
 - dep.a
 - dep.b
 - dep.c

**New version — X.Y.Z.QUALIFIER (DATE) ❌ BROKEN:**
Require-Bundle:
 - dep.a
 - dep.b
 - dep.c
 - dep.d    ← NEW DEPENDENCY (not available)
```

---

### Step 6 — Root Cause Identification

Synthesize findings from Steps 1–5 into a root cause statement:

#### 6.1 Root Cause Template

```markdown
## Root Cause

The [component/bundle] was rebuilt on [DATE] (timestamp [QUALIFIER]).
The new version [VERSION] [added/changed/removed] a dependency on
[ARTIFACT], which is not available because:

1. [ARTIFACT] is not published in [REPOSITORY], OR
2. [ARTIFACT] is published in a different repository not configured
   in this build, OR
3. [ARTIFACT] was supposed to be included but the publish step
   failed/was skipped, OR
4. [ARTIFACT] is a newly created bundle that has not yet been
   deployed.
```

#### 6.2 Version Timeline

Document the chronological sequence of events:

```
YYYY-MM-DD  artifact.name    version.old     ← known-good
    ↓ ... (time gap) ...
YYYY-MM-DD  artifact.name    version.new     ← introduces breaking change
YYYY-MM-DD  build            FAILS ❌
```

---

### Step 7 — Rollback Strategy Analysis

Evaluate rollback options at multiple granularity levels. Every
rollback option must be assessed for **risk**, **effort**, **scope**,
and **side effects**.

#### 7.0 Rollback Granularity Levels

```
┌─────────────────────────────────────────────────┐
│  Level 5 — FULL BUILD ROLLBACK                  │
│  Roll back the entire build configuration       │
│  (all repos, all versions) to a known-good      │
│  snapshot date.                                  │
├─────────────────────────────────────────────────┤
│  Level 4 — TOP COMPONENT ROLLBACK               │
│  Roll back the top-level component repository   │
│  (e.g., pin a p2 repo to an older version).     │
│  Affects all bundles within that component.      │
├─────────────────────────────────────────────────┤
│  Level 3 — INNER COMPONENT ROLLBACK             │
│  Roll back a specific bundle WITHIN a component │
│  by overriding it with a known-good JAR from a  │
│  local p2 repo or target platform directory.    │
├─────────────────────────────────────────────────┤
│  Level 2 — DEPENDENCY ROLLBACK                  │
│  Roll back a specific dependency declaration    │
│  in MANIFEST.MF or pom.xml to use an older      │
│  version range.                                 │
├─────────────────────────────────────────────────┤
│  Level 1 — FEATURE ROLLBACK                     │
│  Remove a specific plugin from feature.xml or   │
│  mark it optional to unblock the build.         │
├─────────────────────────────────────────────────┤
│  Level 0 — BUNDLE EXCLUSION                     │
│  Exclude the broken bundle from the build       │
│  entirely (module exclusion in POM or feature    │
│  removal). Last resort — breaks functionality.  │
└─────────────────────────────────────────────────┘
```

#### 7.1 Rollback Option Template

For each viable rollback option, document:

```markdown
### Option [Letter] — [Description] ([Level N] — [Level Name])

**Scope:** [What changes / what stays the same]
**Risk:** 🟢 Low / 🟡 Medium / 🔴 High — [explanation]
**Effort:** 🟢 Low / 🟡 Medium / 🔴 High — [explanation]
**Side Effects:** [List known side effects or "None expected"]
**Requires:** [CI access / team coordination / local only]
**Reversibility:** [Easy to revert / Difficult to revert]

**Procedure:**
1. [Exact steps]
2. [Exact steps]

**Files to Modify:**
- `path/to/file` (line N–M)

**Verification:**
\`\`\`powershell
# Command to verify the rollback worked
\`\`\`
```

#### 7.2 Top Component Rollback (Level 4)

Pin a p2 repository or Maven dependency to an older component version:

```xml
<!-- BEFORE (uses shared nightly version): -->
<repository>
    <id>component_name</id>
    <url>${base_url}/component_name/${shared_version}/component_name-${shared_version}.zip!/</url>
    <layout>p2</layout>
</repository>

<!-- AFTER (pinned to known-good version): -->
<repository>
    <id>component_name</id>
    <url>${base_url}/component_name/KNOWN_GOOD_VERSION/component_name-KNOWN_GOOD_VERSION.zip!/</url>
    <layout>p2</layout>
</repository>
```

> ⚠️ **Decoupling:** If all repositories share a version variable
> (e.g., `${repository_Version}`), the rollback target must be
> decoupled from the shared variable. Hardcode the known-good version
> string for the specific repository only.

#### 7.3 Inner Component Rollback (Level 3)

Override a specific bundle within a component by creating a local
p2 repository from a known-good JAR:

```powershell
# Create a local p2 repo from a known-good JAR
$sourceJar = "path\to\known-good-bundle.jar"
$localRepo = "path\to\local_p2_repos\component_rollback"
$bundlesDir = "$localRepo\plugins"

New-Item -ItemType Directory -Path $bundlesDir -Force | Out-Null
Copy-Item $sourceJar -Destination $bundlesDir

# Generate p2 metadata using Eclipse FeaturesAndBundlesPublisher
eclipse -application org.eclipse.equinox.p2.publisher.FeaturesAndBundlesPublisher `
  -metadataRepository "file:/$localRepo" `
  -artifactRepository "file:/$localRepo" `
  -source $localRepo `
  -publishArtifacts
```

Then reference the local repo in the POM:

```xml
<repository>
    <id>component_rollback</id>
    <url>file:///path/to/local_p2_repos/component_rollback</url>
    <layout>p2</layout>
</repository>
```

#### 7.4 Dependency Rollback (Level 2)

Modify the `Require-Bundle` version range in `META-INF/MANIFEST.MF`
to exclude the broken version:

```
# BEFORE — accepts any version >= 1.0.0:
Require-Bundle: com.example.broken.bundle;bundle-version="1.0.0"

# AFTER — restricts to versions < 2.0.0 (excludes nightly):
Require-Bundle: com.example.broken.bundle;bundle-version="[1.0.0,2.0.0)"
```

> ⚠️ **Tycho resolution:** Tycho resolves from p2 repositories, not
> Maven. Version ranges in MANIFEST.MF constrain which p2 version is
> selected, but if only one version exists in the repo, Tycho picks
> it regardless of the range.

#### 7.5 Feature Rollback (Level 1)

Remove or make optional a specific plugin in `feature.xml`:

```xml
<!-- Option A — Remove the plugin entirely: -->
<!-- <plugin id="com.example.broken.plugin" .../> -->

<!-- Option B — Make it optional (uninstall allowed): -->
<plugin
    id="com.example.broken.plugin"
    download-size="0"
    install-size="0"
    version="0.0.0"
    unpack="false"
    fragment="false"/>
<!-- Add: optional="true" if supported -->
```

> ⚠️ **Functionality impact:** Removing a plugin from a feature means
> it will not be installed in the product. Verify that no runtime code
> depends on it.

#### 7.6 Bundle Exclusion (Level 0)

Exclude a broken module from the build entirely:

```xml
<!-- In the aggregator pom.xml, comment out the module: -->
<modules>
    <module>com.example.working.plugin</module>
    <!-- <module>com.example.broken.plugin</module> -->
</modules>
```

> ⚠️ **Last resort:** This completely removes the module from the
> build. Other modules that depend on it will also fail. Only use
> when the module is non-essential for the current build goal.

#### 7.7 Rollback Decision Matrix

Document a priority table for the specific build failure:

| Priority | Action | Level | Owner | Risk |
|---|---|---|---|---|
| 🔴 **Immediate** | [First action — e.g., contact team] | — | [Team] | — |
| 🟠 **Short-term** | [Rollback action] | [Level N] | [Team] | [Risk] |
| 🟡 **Medium-term** | [Permanent fix] | — | [Team] | [Risk] |

#### 7.8 Shared Variable Considerations

When multiple repositories share a version variable (common in Tycho
builds), evaluate these considerations before rollback:

| Consideration | Question |
|---|---|
| **Variable scope** | How many repos use the same `${version}` variable? |
| **Decoupling impact** | Does hardcoding one repo's version break the build contract? |
| **CI pipeline** | Does the CI system inject the variable? Will a hardcoded value survive CI? |
| **Other consumers** | Do other projects consume the same component at the shared version? |

---

### Step 8 — Documentation

All findings MUST be documented in a structured markdown file placed
in an appropriate location within the project.

#### 8.1 Document Location

```
<project-root>/
  <files-or-docs-module>/
    migration_issues/          ← or build_issues/
      <descriptive_name>.md
```

Use underscore naming for the file (per project convention) and a
name that describes the specific error, not a generic name.

#### 8.2 Document Structure

The investigation document must contain these sections:

| # | Section | Content |
|---|---|---|
| 1 | **Error Messages** | Exact error output grouped by module |
| 2 | **Dependency Chain Analysis** | ASCII diagram + affected bundles table |
| 3 | **Bundle/Artifact Identity** | What is the missing artifact, what it is NOT, evidence |
| 4 | **Repository Inventory** | All configured repositories + search results |
| 5 | **Root Cause** | MANIFEST.MF comparison, version timeline, ecosystem analysis |
| 6 | **Fix Options** | Rollback analysis + options A/B/C/D with trade-offs |
| 7 | **Diagnostic Steps** | Reproducible commands for verification |
| 8 | **Impact Assessment** | Table of all affected modules |
| 9 | **Related Errors** | Other errors in the same build (related or not) |
| 10 | **Key File References** | Workspace files + external references with line numbers |

#### 8.3 Metadata Table

Every investigation document starts with a metadata table:

```markdown
| Field              | Value |
|--------------------|-------|
| **Date Reported**  | YYYY-MM-DD |
| **Build System**   | Maven / Tycho X.Y.Z |
| **Component**      | `<component-name>` |
| **Migration**      | [context, e.g., Eclipse 4.33 / Orion 12] |
| **Severity**       | 🔴 Critical / 🟡 Warning / 🟢 Info |
| **Status**         | Open / In Progress / Resolved |
| **Last Updated**   | YYYY-MM-DD |
| **Known-Good Ref** | [reference to last working build] |
```

---

### Step 9 — Impact Assessment

Document all modules affected by the build failure:

| Module | Packaging | Build Step | Blocked? |
|--------|-----------|------------|----------|
| `module.name` | eclipse-plugin | N/M | ✅ Yes / ⚠️ Likely / ❌ No |

Include both **confirmed** blocked modules (those with explicit errors)
and **likely** blocked modules (those with the same dependency chain
that were not reached because Maven stopped earlier).

---

### Step 10 — Verification

After applying a fix or rollback:

1. **Clean build:** `mvn clean verify`
2. **Check for residual errors:** All previously failing modules must pass
3. **Check for regressions:** No new errors introduced by the rollback
4. **Update the investigation document:** Mark status as `Resolved`,
   document which fix was applied

```powershell
# Full clean build
mvn clean verify 2>&1 | Tee-Object -FilePath build_output.log

# Check for remaining errors
Select-String -Path build_output.log -Pattern "\[ERROR\]" | Format-Table -AutoSize
```

---

## Prohibited Behaviors

The agent is **BLOCKED** from:

- **Modifying workspace bundle dependencies to remove the broken
  transitive dependency** — The dependency exists for a reason. The
  fix is to provide the missing artifact, not remove the requirement.
- **Auto-applying rollbacks without user approval** — Always present
  the rollback analysis and wait for explicit authorization.
- **Guessing artifact versions** — Use only verified version strings
  from build logs, Maven cache, git history, or known-good builds.
- **Assuming a single fix is correct** — Always present multiple
  rollback options with trade-off analysis. Let the user decide.
- **Mixing investigation with code changes** — The investigation
  document is committed separately from any POM/MANIFEST.MF fixes.
- **Ignoring shared version variables** — When rolling back a single
  repository that shares a version variable with others, the impact
  on other repositories must be assessed.
- **Deleting repository entries from POM** — Replace or pin, never
  delete. The repository exists for a reason.
- **Running `mvn deploy` during investigation** — Investigation only.
  Never trigger deployment.

---

## Common Pitfalls

| Pitfall | Solution |
|---|---|
| Treating each module's error as independent | Deduplicate — multiple modules often fail from the same root cause |
| Rolling back the wrong component | Trace the full dependency chain first. The breaking change may be 2–3 levels deep |
| Rolling back a dependency that still resolves the broken version | In Tycho/p2, version ranges in MANIFEST.MF don't help if only one version exists in the repo. Roll back the REPO, not the consumer |
| Assuming the Maven local cache has all versions | p2 repositories are NOT cached in `~/.m2`. Only Maven artifacts are |
| Hardcoding a version without decoupling from shared variable | Other repos may break if the shared variable is also changed |
| Blaming code changes for a nightly dependency break | Check if the dependency's qualifier (timestamp) changed between builds |
| Not documenting negative results | "Not found" is a critical finding. Document every search that returned no results |
| Creating the investigation doc in the wrong location | Use the project's existing docs/files module, not the root directory |
| Investigating only the first error | Maven stops at the first unresolvable module. There may be multiple distinct root causes |
| Forgetting to update both Tycho POMs | Tycho projects often have a main and standalone aggregator POM — both need the same fix |

---

## Checklist

Before reporting the investigation as complete, verify:

- [ ] All distinct errors extracted and classified
- [ ] Dependency chain fully reconstructed (ASCII diagram)
- [ ] All configured repositories inventoried
- [ ] Missing artifact searched in all available sources
- [ ] MANIFEST.MF / pom.xml compared between old and new versions
- [ ] Root cause identified with version timeline
- [ ] Rollback options documented at appropriate granularity levels
- [ ] Impact assessment includes all affected modules (confirmed + likely)
- [ ] Diagnostic commands provided for each investigation step
- [ ] Investigation document committed to the project repository
- [ ] Related (but independent) errors noted separately
