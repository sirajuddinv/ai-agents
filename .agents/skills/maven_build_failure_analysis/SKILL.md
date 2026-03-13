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

**Maximum-detail philosophy:** Every investigation document MUST
contain the absolute maximum level of detail. This means:

- **Full error messages** — paste the exact `[ERROR]` output for
  EVERY affected module, not just the first one
- **Full MANIFEST.MF content** — include the complete `Require-Bundle`
  list (all entries), not just the diff
- **Line-level references** — every MANIFEST.MF dependency, feature.xml
  plugin entry, and POM repository declaration must cite the exact
  file and line number (e.g., `MANIFEST.MF L10`)
- **Negative results documented** — every search that returns zero
  results is a critical finding and must be explicitly recorded
- **Evidence-based disambiguation** — when a bundle name could be
  confused with a similarly-named artifact, the document must include
  a dedicated disambiguation section with evidence
- **Exhaustive version identification** — every local avenue for
  finding previous versions must be attempted and documented, even
  when all results are negative
- **Cross-analysis tables** — rollback options must include side-by-side
  comparison of ALL candidates, not just the recommended one
- **Complete diagnostic commands** — every diagnostic step must include
  ready-to-run commands with actual paths, not just conceptual
  descriptions

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

#### 1.1 Error Extraction Template — Per-Module Detail

For EVERY affected module (not just the first), capture the full error
with exact build output. Even when modules share the same root cause,
each module's error reveals distinct dependency paths:

```markdown
### 1.N `<module-name>` (module M/total)

\`\`\`
[ERROR] Cannot resolve project dependencies:
[ERROR]   Software being installed: <module-name> <version>
[ERROR]   Missing requirement: <bundle> <version>
            requires '<dependency>' but it could not be found
[ERROR]   Cannot satisfy dependency: <intermediate-bundle> <version>
            depends on: <dependency>
[ERROR]   Cannot satisfy dependency: <module-name> <version>
            depends on: <requirement>
\`\`\`
```

**Why per-module errors matter:** Different modules may declare
different version constraints (e.g., `bundle-version="3.2.0"` vs
`(none)`) or reach the broken dependency through different paths
(Require-Bundle vs feature.xml plugin inclusion). The per-module
error output reveals these differences.

> ⚠️ **MANDATORY:** Do NOT summarize errors as "3 modules fail with
> the same error." Paste the EXACT `[ERROR]` output for every module.
> Maven stops at the first unresolvable module per reactor pass, but
> EVERY module with the same dependency chain is potentially affected
> and must be listed.

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
Every level MUST include:
- Bundle symbolic name
- Version (including qualifier timestamp)
- Source repository
- The specific `Require-Bundle` / `Import-Package` declaration with
  **exact file and line number** (e.g., `MANIFEST.MF L10`)

**Reference-quality example:**

```
Level 0 — WORKSPACE BUNDLES (what we are building)
┌──────────────────────────────────────────────────┐
│  com.example.module.config                       │  MANIFEST.MF L10: Require-Bundle: com.example.validation;bundle-version="3.2.0"
│  com.example.module.feature                      │  feature.xml L99: <plugin id="com.example.framework" .../>
└──────────────────────────┬───────────────────────┘
                           │ depends on
                           ▼
Level 1 — EXTERNAL BUNDLE (from repo_validation p2 repo)
┌──────────────────────────────────────────────────┐
│  com.example.validation                          │  version 3.15.0.202603111556
│                                                  │  Require-Bundle: com.example.framework 1.0.0
└──────────────────────────┬───────────────────────┘
                           │ depends on
                           ▼
Level 2 — EXTERNAL BUNDLE (from repo_framework p2 repo)
┌──────────────────────────────────────────────────┐
│  com.example.framework                           │  version 1.0.0.202603121421
│                                                  │  Require-Bundle: com.example.missing.service 0.0.0
└──────────────────────────┬───────────────────────┘
                           │ depends on
                           ▼
Level 3 — ??? (NOT FOUND)
┌──────────────────────────────────────────────────┐
│  com.example.missing.service                     │  ❌ NOT in any configured p2 repository
│                                                  │  ❌ NOT in this workspace
│                                                  │  ❌ NOT in target platform
└──────────────────────────────────────────────────┘
```

#### 2.5 Complete Affected Bundles Table

List ALL workspace bundles that participate in the dependency chain,
not just those with explicit errors. Include the exact MANIFEST.MF
location and version constraint:

| Workspace Bundle | MANIFEST.MF Location | Version Constraint |
|---|---|---|
| `com.example.config` | `META-INF/MANIFEST.MF` L10 | `bundle-version="3.2.0"` |
| `com.example.engine` | `META-INF/MANIFEST.MF` L18 | `bundle-version="3.2.0"` |
| `com.example.standalone` | `META-INF/MANIFEST.MF` L22 | *(none)* |

> ⚠️ **MANDATORY:** Include EVERY workspace bundle with the dependency,
> even if Maven didn't reach it during the build. Maven stops at the
> first unresolvable module — there may be 5–10 more affected modules
> that were never reported.

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

#### 3.5 Bundle Identity Disambiguation

When a missing artifact has a name similar to an existing artifact
(e.g., `com.bosch.emf.validation.service` vs
`org.eclipse.emf.validation`), the investigation document MUST include
a **dedicated disambiguation section** with the following:

1. **What it is NOT** — explicitly name the similar artifact and
   explain why it is different (different prefix, different symbolic
   name, different provider)
2. **What it IS** — describe the missing artifact's likely purpose
   based on its naming convention (e.g., `com.bosch.` prefix =
   internal bundle, `.service` suffix = OSGi service wrapper)
3. **Evidence** — list concrete evidence:
   - Workspace references (`.launch` files, MANIFEST.MF, feature.xml)
   - What does NOT reference it (no MANIFEST.MF, no feature.xml,
     no pom.xml in the workspace)
   - When it was introduced (qualifier timestamp of the bundle
     that added the dependency)
   - Full scan results (toolbase, Maven cache, all repos)
4. **Where it should come from** — candidate repositories with
   likelihood assessment:

   | Repository | Likely? | Reasoning |
   |---|---|---|
   | `repo_a` | **Most likely** | Provides the bundle that requires it |
   | `repo_b` | Possible | Sometimes used for cross-cutting bundles |
   | A new/missing repo | Possible | If recently factored out |

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

#### 5.3 Full Content Comparison Template

The comparison MUST include the **complete** MANIFEST.MF key headers
— not just the changed lines. The reader must be able to see the
entire dependency list to understand the full context:

```markdown
**Old version — X.Y.Z.QUALIFIER (FULL DATE) ✅ WORKS:**

\`\`\`
Bundle-SymbolicName: com.example.framework;singleton:=true
Bundle-Version: X.Y.Z.QUALIFIER
Bundle-Activator: com.example.framework.Activator
Bundle-RequiredExecutionEnvironment: JavaSE-1.8
Bundle-Vendor: Example Corp
Require-Bundle: com.example.core,
 com.example.core.logging,
 org.eclipse.emf.mapping,
 org.eclipse.sphinx.emf.validation,
 com.example.mdf,
 com.example.core.util,
 com.example.core.project.config,
 com.example.core.project.validation
\`\`\`

→ **8 dependencies, all resolvable. No `com.example.missing.service`.**

**New version — X.Y.Z.QUALIFIER (FULL DATE) ❌ BROKEN:**

\`\`\`
Require-Bundle: com.example.core,
 com.example.core.logging,
 org.eclipse.emf.mapping,
 org.eclipse.sphinx.emf.validation,
 com.example.mdf,
 com.example.core.util,
 com.example.core.project.config,
 com.example.core.project.validation,
 com.example.missing.service    ← NEW DEPENDENCY (not available anywhere)
\`\`\`

→ **Added `com.example.missing.service` as a hard `Require-Bundle`
dependency. This bundle does not exist in any known repository.**
```

> ⚠️ **MANDATORY:** Include the FULL `Require-Bundle` list for both
> old and new versions. A diff-only view hides context — the reader
> needs to see all 8+ dependencies to understand what was there before
> and what was added. Also include `Bundle-SymbolicName`,
> `Bundle-Version`, `Bundle-Vendor`, and
> `Bundle-RequiredExecutionEnvironment` to confirm bundle identity.

#### 5.4 Multi-Bundle Chain Comparison

When the dependency chain has multiple levels, perform MANIFEST.MF
comparison for EVERY bundle in the chain, not just the one that
introduced the breaking change. This confirms whether the intermediate
bundles also changed:

| Bundle | Old Version | New Version | Changed? | Breaking? |
|---|---|---|---|---|
| `com.example.validation` | 3.11.0.QUALIFIER | 3.15.0.QUALIFIER | ✅ Yes — major version bump | ❌ No — still depends on same framework |
| `com.example.framework` | 1.0.0.QUALIFIER_OLD | 1.0.0.QUALIFIER_NEW | ✅ Yes — same version, new qualifier | ✅ Yes — adds missing.service dep |

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

Document the chronological sequence of events for EVERY bundle in
the dependency chain, not just the one that broke:

```
YYYY-MM-DD  com.example.validation       3.11.0.QUALIFIER  ← known-good
YYYY-MM-DD  com.example.framework        1.0.0.QUALIFIER   ← known-good (NO missing.service dep)
    ↓ ... (N months) ...
YYYY-MM-DD  com.example.validation       3.15.0.QUALIFIER  ← nightly rebuild
YYYY-MM-DD  com.example.framework        1.0.0.QUALIFIER   ← nightly rebuild (ADDS missing.service dep)
YYYY-MM-DD  build                        FAILS ❌
```

#### 6.3 Known-Good Ecosystem Table

Document ALL bundles in the dependency chain as found in the known-good
reference build. This serves as the authoritative "what was working":

| Bundle | Version in Known-Good | Status |
|---|---|---|
| `com.example.validation` | 3.11.0.QUALIFIER | ✅ Works |
| `com.example.framework` | 1.0.0.QUALIFIER | ✅ Works |
| `org.eclipse.emf.validation` | 1.8.0.QUALIFIER | ✅ Present |
| `com.example.missing.service` | — | ❌ NOT present |

> The missing bundle was NEVER part of the working ecosystem. This
> confirms it is a newly introduced dependency, not a regression.

#### 6.4 Exhaustive Version Identification

When the version needed for rollback cannot be immediately determined,
the investigation MUST exhaust ALL local avenues and document each
one explicitly:

| Investigation Avenue | What Was Checked | Result | Can Identify Version? |
|---|---|---|---|
| Maven local cache | `~\.m2\repository\...` | No artifacts | ❌ No |
| Parent POM hierarchy | `ecl_int_releng` all versions | Not cached, not downloadable | ❌ No |
| PDE `.target` files | All workspace `.target` files | 4 historical versions found | ⚠️ Strings known, ZIPs not accessible |
| Git history | `git log --all -p -- */pom.xml` | Version variables, not resolved values | ⚠️ Variable names known |
| CI pipeline parameters | `${repository_Version}`, `${base_url}` | Not defined locally | ❌ No |
| Known-good product | `product/3.17.1` | Bundle version known | ✅ Bundle version, not repo version |
| Repository manager | Nexus/Artifactory | Not accessible | ❌ No |

> ⚠️ **MANDATORY:** The table must show EVERY avenue investigated,
> including those that returned negative results. Negative results
> narrow the rollback options and are essential for the reader.

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

#### 7.7 Rollback Cross-Analysis Table

Before recommending a rollback target, ALL candidates MUST be
evaluated in a single comparison table:

| Rollback Target | What Changes | Risk | Effort | Verdict |
|---|---|---|---|---|
| **Component A** (p2 repo) | Pins repo to older version | 🟢 Low | 🟡 Medium | ✅ **Recommended** |
| Bundle B (within Component A) | Same effect — bundle is inside the component | 🟢 Low | ⛔ Not directly rollback-able | Equivalent to Component A rollback |
| Bundle C (intermediate dep) | Use older version | 🔴 High — may miss needed fixes | 🟡 Medium | ❌ Unnecessary — old version still resolves broken nightly |

For each **rejected** candidate, include a detailed explanation of
WHY it was rejected. Example:

> **Why rolling back Bundle C alone does NOT work:**
> The old `Bundle C` 3.11.0 still declares `Require-Bundle: Bundle B;
> bundle-version="1.0.0"`. Since the p2 repo serves a single version
> of Bundle B (the latest nightly), Tycho will still resolve the
> broken version. The error persists.

This cross-analysis prevents the reader from asking "why didn't you
just roll back X instead?" — every candidate is pre-evaluated.

#### 7.8 Rollback Decision Matrix (Priority)

After the cross-analysis, document the recommended action priority:

| Priority | Action | Owner |
|---|---|---|
| 🔴 **Immediate** | [Contact upstream team — ask about the new dependency] | [Your team → Upstream team] |
| 🟠 **Short-term** | [Roll back the component if bundle doesn't exist yet] | [Your team (POM change)] |
| 🟡 **Medium-term** | [Add the missing repo or request inclusion] | [Cross-team coordination] |

#### 7.9 Shared Variable Considerations

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

#### 8.2 Document Structure — Mandatory Sections

The investigation document MUST contain ALL of the following sections.
Every section MUST be populated with maximum detail. Empty or
skeleton sections are not acceptable.

| # | Section | Content | Detail Level Required |
|---|---|---|---|
| 1 | **Error Messages** | Exact `[ERROR]` output for EVERY affected module | Full error output per module (§1.1, §1.2, §1.3...) — not summarized |
| 2 | **Dependency Chain Analysis** | ASCII box diagram + affected bundles table | Every level must cite MANIFEST.MF/feature.xml lines; table lists ALL 9+ affected bundles, not just the 3 Maven reported |
| 3 | **Bundle/Artifact Identity** | Disambiguation (what it is NOT), evidence, candidate sources | Subsections: §3.1 What it is NOT, §3.2 Evidence list, §3.3 Where it should come from (table), §3.4 Search results (including negatives), §3.5 What actually exists in each component (plugin list tables) |
| 4 | **Repository Inventory** | All configured p2/Maven repos with URL patterns | Numbered table of all repos; note which use shared variables |
| 5 | **Root Cause** | Full MANIFEST.MF content comparison, version timeline, known-good ecosystem, version identification investigation | §5.1 Full MANIFEST.MF old vs new for EVERY chain bundle, §5.2 Version timeline (all chain bundles), §5.3 Known-good ecosystem table, §5.4 Exhaustive version identification (CI params, parent POM, target files, Maven cache, git history) |
| 6 | **Fix Options** | Rollback cross-analysis + all options A/B/C/D | §6.0 Cross-analysis table of ALL candidates with rejection reasons, §6.1 Each option with procedure/files/verification, §6.2 Priority matrix |
| 7 | **Diagnostic Steps** | Ready-to-run commands for every investigation step | Every command must include actual paths, actual tool locations, actual bundle names — not placeholders. PowerShell AND bash variants |
| 8 | **Impact Assessment** | Table of ALL affected modules | Both confirmed (✅ Yes) and likely (⚠️ Likely) with packaging type and build step |
| 9 | **Related Errors** | Other errors in the same build | Table with: Error / Root Cause / Related to this issue? |
| 10 | **Key File References** | Workspace files + external references | §10.1 Workspace files with purpose and line numbers, §10.2 External references (toolbase, Maven cache, product builds) with full paths |

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
- **Summarizing error messages** — Never write "3 modules fail with
  the same error." Paste the EXACT `[ERROR]` output for every module.
- **Providing skeleton/template documentation** — Every section of
  the investigation document must be fully populated with actual
  findings. Placeholder text like "[TBD]" or "[to be investigated]"
  is forbidden.
- **Showing MANIFEST.MF diffs instead of full content** — Always
  show the complete `Require-Bundle` list for both old and new
  versions, not just the changed lines.
- **Omitting negative search results** — Every search that returns
  zero results MUST be documented. "Not found" is a critical finding.
- **Citing files without line numbers** — Every reference to a
  MANIFEST.MF entry, feature.xml plugin, or POM repository must
  include the exact line number.

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
| Wrote "same error as above" instead of pasting full output | Every module's error must be pasted in full — different modules reveal different dependency paths and version constraints |
| Showed only the MANIFEST.MF diff, not the full content | The reader needs the complete Require-Bundle list to understand the old ecosystem. Show all 8+ entries, not just the added one |
| Listed only 3 affected modules (what Maven reported) | Maven stops at the first failure. Scan all MANIFEST.MF files — there may be 9+ affected modules |
| Wrote diagnostic commands with placeholder paths | Every command must use actual paths from the investigation. Replace `<path>` with the real path before documenting |

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
- [ ] Every error message includes full `[ERROR]` output per module
- [ ] MANIFEST.MF comparisons show full content, not just diffs
- [ ] All file references include exact line numbers
- [ ] All negative search results documented explicitly
- [ ] Rollback cross-analysis covers ALL candidates with rejection reasons
- [ ] Diagnostic commands use actual paths, not placeholders
- [ ] Version identification exhausts all local avenues with results table
- [ ] Bundle identity disambiguation section included (if applicable)
