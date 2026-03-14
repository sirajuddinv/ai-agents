<!--
title: Eclipse Target Platform Migration
description: Systematic resolution of p2 dependency failures and compilation
    errors during Eclipse target platform version upgrades — obsolete bundle
    removal, split-package conflict resolution, and MANIFEST.MF/feature.xml
    remediation with blast-radius analysis.
category: Build & Dependency Management
-->

# Eclipse Target Platform Migration Skill

> **Skill ID:** `eclipse_target_platform_migration`
> **Version:** 1.0.0
> **Standard:** [Agent Skills (agentskills.io)](https://agentskills.io)

## Description

Perform systematic resolution of build failures that arise when
migrating an Eclipse/Tycho product build to a new Eclipse target
platform version (e.g., Eclipse 4.29 → 4.33). These failures
typically manifest as cascading p2 dependency resolution errors
and Java module system compilation conflicts.

Eclipse target platform upgrades frequently remove, rename, or
restructure OSGi bundles between releases. This skill provides
a structured methodology to:

1. **Identify** obsolete bundles that no longer exist in the new
   target platform
2. **Assess blast radius** — determine whether a bundle is only
   referenced in `feature.xml` (safe removal) or also in
   `MANIFEST.MF` / Java source (requires deeper analysis)
3. **Resolve** split-package conflicts caused by the Java Platform
   Module System (JPMS) when OSGi bundles re-export packages that
   overlap with JDK modules
4. **Execute** atomic, well-documented commits for each fix

**Maximum-detail philosophy:** Every fix MUST be preceded by a
blast-radius analysis. Even "obvious" removals require a search
across `feature.xml`, `MANIFEST.MF`, and Java source files to
confirm no transitive dependency exists.

## Related Skills

| Skill | Relationship |
|---|---|
| [`maven_build_failure_analysis`](../maven_build_failure_analysis/SKILL.md) | Complementary — provides deep investigation and rollback strategies; this skill provides targeted migration fixes |
| [`local_p2_repository_rollback`](../local_p2_repository_rollback/SKILL.md) | Alternative — when a bundle must be preserved via local p2 repo instead of removed |
| [`eclipse_pde_runtime_troubleshooting`](../eclipse_pde_runtime_troubleshooting/SKILL.md) | Complementary — handles runtime errors after migration; this skill handles build-time errors |
| [`git_atomic_commit`](../git_atomic_commit/SKILL.md) | Used after — commit each fix atomically |

## Prerequisites

| Requirement | Minimum |
|---|---|
| Build system | Maven 3.6+ with Tycho 2.x or 4.x |
| Java | JDK 11+ (JPMS awareness required) |
| VCS | Git 2.x+ |
| Shell | PowerShell 5.1+ or Bash 4+ |
| Build Type | Maven/Tycho (Eclipse PDE) product build |

## When to Apply

Apply this skill when:

- An Eclipse/Tycho build fails with `Missing requirement: ... requires
  'org.eclipse.equinox.p2.iu; <bundle> 0.0.0' but it could not be
  found` after a target platform version upgrade
- Multiple modules fail with cascading p2 resolution errors referencing
  bundles that existed in the previous Eclipse version
- Compilation fails with `The package <pkg> is accessible from more
  than one module: <unnamed>, <jdk-module>` (split-package conflict)
- A user asks to migrate a Tycho build from one Eclipse version to
  another
- A user asks to fix "missing bundle" errors after updating the target
  platform

Do NOT apply when:

- The missing bundle is from a **project-specific** p2 repository (not
  Eclipse platform) — use
  [`maven_build_failure_analysis`](../maven_build_failure_analysis/SKILL.md)
  or [`local_p2_repository_rollback`](../local_p2_repository_rollback/SKILL.md)
- The error is a runtime `ClassNotFoundException` or compilation error
  in the project's own source code (not a migration artifact)
- The build has never worked (not a migration — investigate from scratch)

---

## Step-by-Step Procedure

### Step 1 — Error Classification

Parse the build output and classify each error into one of the
migration-specific categories:

| Category | Error Pattern | Typical Cause |
|---|---|---|
| **Obsolete Bundle (feature.xml)** | `Missing requirement: <feature>.feature.group requires 'org.eclipse.equinox.p2.iu; <bundle>'` | Bundle removed from Eclipse platform; listed in `feature.xml` |
| **Obsolete Bundle (MANIFEST.MF)** | `Missing requirement: <bundle> requires 'osgi.bundle; <dependency>'` | Bundle removed from Eclipse platform; declared in `Require-Bundle` |
| **Split-Package Conflict** | `The package <pkg> is accessible from more than one module: <unnamed>, <jdk-module>` | OSGi bundle re-exports a package that the JDK also provides via JPMS |
| **Version Range Mismatch** | `Cannot satisfy dependency: <bundle> depends on <dep> [<range>]` | Bundle exists but version changed outside declared range |

#### 1.1 Known Obsolete Bundle Categories

These bundle families are commonly removed across Eclipse version
upgrades:

| Bundle Family | Removed Because | Example Bundles |
|---|---|---|
| **W3C DOM extensions** | Merged into JDK or dropped by Eclipse | `org.w3c.dom.events`, `org.w3c.dom.smil`, `org.w3c.dom.svg`, `org.w3c.dom.svg.extension` |
| **W3C CSS** | Merged into JDK or dropped by Eclipse | `org.w3c.css.sac` |
| **Nashorn/JSDT** | Nashorn removed in Java 15 (JEP 372) | `org.eclipse.wst.jsdt.nashorn.extension` |
| **Java EE (javax.\*)** | Removed from JDK in Java 11 (JEP 320) | `javax.activation`, `javax.xml.bind` (jaxb-api) |
| **Parser generators** | Dropped from platform | `java_cup.runtime` |
| **PDE internal** | Restructured or merged | `org.eclipse.pde.ds.lib` |
| **Artop AUTOSAR** | Version-specific sub-modules replaced | `org.artop.aal.autosar452` |

---

### Step 2 — Blast-Radius Analysis (Mandatory)

Before removing or modifying any bundle reference, the agent MUST
perform a blast-radius analysis to determine all locations where
the bundle is referenced.

#### 2.1 Search Scope

For each missing bundle, search across **three layers**:

```powershell
# Layer 1: feature.xml — plugin inclusion
Get-ChildItem -Recurse -Filter "feature.xml" |
    Select-String -Pattern "<bundle-symbolic-name>" |
    Select-Object Filename, LineNumber, Line |
    Format-Table -AutoSize -Wrap

# Layer 2: MANIFEST.MF — Require-Bundle and Import-Package
Get-ChildItem -Recurse -Filter "MANIFEST.MF" |
    Select-String -Pattern "<bundle-symbolic-name>" |
    Select-Object Filename, LineNumber, Line |
    Format-Table -AutoSize -Wrap

# Layer 3: Java source — import statements
Get-ChildItem -Recurse -Filter "*.java" |
    Select-String -Pattern "import.*<package-prefix>" |
    Select-Object Filename, LineNumber, Line |
    Format-Table -AutoSize -Wrap
```

#### 2.2 Blast-Radius Classification

| Layer Hit | Risk Level | Action |
|---|---|---|
| Only `feature.xml` | 🟢 **Low** — safe to remove | Remove the `<plugin>` entry |
| `feature.xml` + `MANIFEST.MF` (Require-Bundle) | 🟡 **Medium** — check Java source | Remove from both if no Java imports |
| `feature.xml` + `MANIFEST.MF` + Java source | 🔴 **High** — requires migration | Find replacement bundle or refactor source |

#### 2.3 Documenting Negative Results

**Every search that returns zero results is a critical finding** and
MUST be explicitly documented. A negative result on Layer 3 (Java
source) confirms that the bundle can be safely removed from Layers
1 and 2.

---

### Step 3 — Obsolete Bundle Removal (feature.xml)

When the blast-radius analysis confirms a bundle is **only** referenced
in `feature.xml`:

#### 3.1 Locate the Plugin Entry

Find the exact `<plugin>` block in `feature.xml`:

```xml
<plugin
      id="<bundle-symbolic-name>"
      download-size="0"
      install-size="0"
      version="0.0.0"
      fragment="true"/>
```

#### 3.2 Remove the Entry

Remove the entire `<plugin>` element including any surrounding blank
lines to maintain clean formatting.

#### 3.3 Commit Convention

Each removed bundle SHOULD be a separate atomic commit unless
multiple bundles are part of the same logical family (e.g., all
W3C DOM bundles removed together):

```
fix(<feature-name>): remove obsolete <bundle-symbolic-name> plugin

The <bundle-symbolic-name> bundle is no longer available in the
Eclipse <version> target platform, causing an unresolvable p2
dependency during the Tycho build.

No workspace bundle has a Require-Bundle or Import-Package
dependency on this plugin — it was only listed in feature.xml.
```

---

### Step 4 — Obsolete Bundle Removal (MANIFEST.MF)

When a bundle is referenced in `MANIFEST.MF` but has **no Java
source imports**:

#### 4.1 Remove from Require-Bundle

Remove the entry from the `Require-Bundle` header. Pay attention
to OSGi MANIFEST.MF continuation line syntax (leading space):

```
Require-Bundle: org.eclipse.emf.ecore,
 <bundle-to-remove>,
 org.eclipse.core.runtime
```

becomes:

```
Require-Bundle: org.eclipse.emf.ecore,
 org.eclipse.core.runtime
```

**Critical:** Ensure the comma placement is correct after removal.
The last entry in `Require-Bundle` MUST NOT have a trailing comma.

#### 4.2 Commit Convention

```
fix(<bundle-name>): remove obsolete <dependency> dependency

The <dependency> bundle is no longer available in the target
platform. No Java source in <bundle-name> imports from this
bundle — [explain what provides equivalent functionality].
```

---

### Step 5 — Split-Package Conflict Resolution

Split-package conflicts occur when an OSGi bundle exports a package
that the JDK also provides via the Java Platform Module System (JPMS).

#### 5.1 Error Signature

```
The package <pkg> is accessible from more than one module:
    <unnamed>, <jdk-module>
```

Common examples:

| Package | JDK Module | OSGi Bundle Causing Conflict |
|---|---|---|
| `javax.xml.namespace` | `java.xml` | `jaxb-api` (via `Require-Bundle`) |
| `javax.xml.stream` | `java.xml` | `stax-api` |
| `javax.annotation` | `java.compiler` | `javax.annotation-api` |

#### 5.2 Root Cause

`Require-Bundle` wires ALL exported packages from the required
bundle. If the bundle exports packages that overlap with JDK
modules (e.g., `jaxb-api` exports `javax.xml.namespace` alongside
`javax.xml.bind`), the compiler sees the package from two sources.

#### 5.3 Resolution Strategy — Require-Bundle → Import-Package

Move the dependency from `Require-Bundle` to `Import-Package`,
importing ONLY the specific packages that the source code actually
uses:

**Before (causes conflict):**

```
Require-Bundle: jaxb-api;bundle-version="2.3.1"
```

**After (conflict resolved):**

```
Import-Package: javax.xml.bind,
 javax.xml.bind.annotation
```

#### 5.4 Identifying Required Packages

Scan the Java source to find all imported packages from the
conflicting bundle:

```powershell
# Find all javax.xml.bind imports in the bundle's source
Get-ChildItem -Recurse -Filter "*.java" -Path "<bundle>/src" |
    Select-String -Pattern "import javax\.xml\.bind" |
    ForEach-Object { ($_.Line -replace "import\s+", "" -replace "\.\w+;$", "") } |
    Sort-Object -Unique
```

The unique package names become the `Import-Package` entries.

#### 5.5 Verification

After the change, the overlapping package (e.g.,
`javax.xml.namespace`) resolves from the JDK's module system
without conflict, while the bundle-specific packages (e.g.,
`javax.xml.bind`) resolve from the OSGi bundle via
`Import-Package`.

#### 5.6 Commit Convention

```
fix(<bundle-name>): resolve <package> split-package conflict

Require-Bundle: <osgi-bundle> pulls in all exported packages
including <overlapping-package>, which conflicts with the JDK's
<jdk-module> module causing "accessible from more than one module"
compilation errors.

Move <osgi-bundle> from Require-Bundle to Import-Package, importing
only <package-1> and <package-2>. The <overlapping-class> class
resolves cleanly from the JDK's <jdk-module> module without conflict.
```

---

### Step 6 — Batch Analysis (Proactive)

Tycho's p2 resolver stops at the **first** unresolvable dependency
per module. This means the build must be re-run after each fix to
discover the next missing bundle — a slow, iterative process.

#### 6.1 Proactive Scan

When multiple obsolete bundles are suspected (common during major
Eclipse version jumps), proactively scan the entire `feature.xml`
for potentially obsolete entries:

```powershell
# Extract all plugin IDs from feature.xml
Select-String -Path "feature.xml" -Pattern 'id="([^"]+)"' |
    ForEach-Object { $_.Matches[0].Groups[1].Value } |
    Sort-Object -Unique
```

Cross-reference this list against the known obsolete bundle
categories (Step 1, §1.1) to identify multiple candidates at once.

#### 6.2 Maven -fae Flag

Use Maven's `--fail-at-end` (`-fae`) flag to collect errors across
multiple modules in a single build run instead of stopping at the
first failure:

```powershell
mvn clean verify -fae
```

**Limitation:** `-fae` reports errors across different reactor
modules but does NOT report multiple missing bundles within a
single module's p2 resolution. Each module still stops at its
first unresolvable dependency.

#### 6.3 Batch Commit Strategy

When multiple bundles from the same family are removed (e.g., all
W3C DOM bundles), they MAY be committed together in a single
atomic commit if they share the same root cause:

```
fix(<feature-name>): remove obsolete W3C DOM bundles

The following W3C DOM bundles are no longer available in the
Eclipse <version> target platform:
- org.w3c.dom.events
- org.w3c.dom.smil
- org.w3c.dom.svg
- org.w3c.dom.svg.extension

These packages are now provided by the JDK's java.xml module.
No workspace bundle has a Require-Bundle or Import-Package
dependency on any of these plugins.
```

However, if bundles have **different root causes** (e.g., one is
a W3C DOM bundle and another is a Nashorn extension), they MUST
be committed separately per the atomic commit principle.

---

### Step 7 — Post-Fix Verification

After applying fixes, verify the build progresses past the
resolved errors:

#### 7.1 Targeted Resume

Use Maven's resume flag to skip already-built modules:

```powershell
mvn clean verify -rf :<first-failing-module>
```

#### 7.2 Regression Check

After all migration fixes are applied, run a full clean build to
verify no regressions:

```powershell
mvn clean verify
```

#### 7.3 Feature Completeness

Verify the `feature.xml` still includes all **required** plugins by
checking that no workspace bundle's `MANIFEST.MF` dependencies are
missing from the feature's plugin list.

---

## Scope Coverage

| Category | Convention |
|---|---|
| Obsolete bundle in `feature.xml` | Remove `<plugin>` entry after blast-radius confirmation |
| Obsolete bundle in `MANIFEST.MF` | Remove `Require-Bundle` entry after Java source check |
| Split-package conflict | Move from `Require-Bundle` to `Import-Package` with specific packages |
| Version range mismatch | Update version range or remove constraint |
| Batch obsolete bundles | Proactive scan + family-grouped commits |

---

## Prohibited Behaviors

The agent is **BLOCKED** from:

- **Removing a bundle without blast-radius analysis** — Never assume
  a bundle is unused; always search all three layers
- **Removing a bundle referenced in Java source** — If Java imports
  exist, the source must be migrated, not just the metadata
- **Mixing different root causes in one commit** — Each distinct
  migration issue gets its own atomic commit
- **Silently skipping negative search results** — Zero-result
  searches MUST be documented as evidence of safe removal
- **Editing Java source to work around a metadata issue** — Fix the
  metadata (MANIFEST.MF, feature.xml) first; source changes are a
  last resort
- **Using `Require-Bundle` for bundles with known JPMS overlap** —
  Always prefer `Import-Package` for bundles that export JDK-overlapping
  packages

---

## Common Pitfalls

| Pitfall | Solution |
|---|---|
| Removed bundle from `feature.xml` but not `MANIFEST.MF` | Always search both `feature.xml` AND `MANIFEST.MF` in blast-radius analysis |
| Split-package conflict persists after removing `Require-Bundle` | Check for transitive `Require-Bundle` in dependent bundles that re-export the conflicting package |
| MANIFEST.MF comma syntax broken after removal | The last entry in `Require-Bundle` MUST NOT have a trailing comma; the first entry MUST NOT have a leading comma |
| Batch-committed unrelated removals | Group only by shared root cause (e.g., "W3C DOM family"), not by file location |
| Tycho reports only one missing bundle per run | Use `-fae` for cross-module visibility; accept per-module single-error limitation |
| Removed a bundle that another workspace bundle transitively depends on | Extend blast-radius search to include `Import-Package` references across ALL workspace bundles, not just `Require-Bundle` |
| `Import-Package` resolution fails because bundle is not in target platform | The exporting bundle must still exist in the target platform; `Import-Package` only changes wiring granularity, not availability |
| MANIFEST.MF trailing newline removed | OSGi requires a trailing newline at end of MANIFEST.MF; always preserve it |
