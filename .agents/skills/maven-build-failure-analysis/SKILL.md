---
name: maven-build-failure-analysis
description: General framework for diagnosing Maven / Tycho build failures — parse the failing reactor output, reconstruct the OSGi/p2 dependency chain, extract and compare MANIFEST.MF headers across a known-good and a broken bundle, decode OSGi qualifier build timestamps, detect p2 metadata, and design a rollback strategy — with a deterministic Python helper for the MANIFEST extraction/comparison core.
category: Build & Dependency Management
---

# Maven Build Failure Analysis Skill (v1)

A vendor-neutral framework for diagnosing **Maven** and **Tycho** (Eclipse PDE/OSGi) build failures —
especially the `Missing requirement: ... requires 'osgi.bundle; <bsn> ...' but it could not be found`
class of error that dominates Tycho reactors. The protocol parses the failing build output,
reconstructs the dependency chain, compares the MANIFEST.MF of a known-good vs a broken bundle,
decodes OSGi qualifier timestamps to build a timeline, classifies p2 vs plain-Eclipse layouts, and
designs a rollback strategy.

This is a **base skill**. It owns the general Maven/Tycho/OSGi reasoning. Organization-specific
investigations (component stores, shared artifact filesystems, internal registries) compose it by
adding their own discovery layer. See **Composition by Higher-Level Skills**.

***

## 1. When to Apply

Apply this skill when:

- A Maven or Tycho build fails and the cause is a missing/changed dependency rather than a source bug.
- You need to compare a known-good bundle against a broken one to find an added/removed dependency.
- You need to decode OSGi qualifier timestamps to establish which build introduced a regression.
- You need to assess whether a JAR / product directory can serve as a rollback source.

Do **NOT** apply when:

- The failure is a compilation/source error (fix the source).
- The failure is purely environmental (network, auth) — diagnose that first.

***

## 2. Environment & Dependencies

| Requirement | Minimum |
| :--- | :--- |
| Python | 3.12+ (for the MANIFEST comparison helper) |
| Java `jar` tool | JDK 8+ (only if extracting MANIFEST.MF manually) |
| Maven / Tycho | The project's own build toolchain |

```bash
python --version
jar --version || echo "jar not found - only needed for manual MANIFEST extraction"
```

***

## 3. The Helper Script

The deterministic core — extract OSGi headers from two bundle JARs, compare their `Require-Bundle` /
`Import-Package` / `Export-Package` lists, and decode the `Bundle-Version` qualifier — lives in
[scripts/analyze_maven_build_failure.py](scripts/analyze_maven_build_failure.py) (Tier 1 / Python per
[Scripting Language Selection Rules §3](../../../ai-agent-rules/scripting-language-selection-rules.md)).

```bash
# Compare two bundle JARs (known-good vs broken)
python scripts/analyze_maven_build_failure.py --good old.jar --bad new.jar

# Compare two already-extracted manifests
python scripts/analyze_maven_build_failure.py --good a/MANIFEST.MF --bad b/MANIFEST.MF --manifest

# Inspect a single bundle (headers + decoded qualifier)
python scripts/analyze_maven_build_failure.py --good one.jar
```

***

## 4. Procedure

### Step 1 — Parse the Failure

Read the failing reactor output and isolate the **first** unsatisfied requirement (later ones are
usually cascades). Capture: the consuming bundle, the missing `Bundle-SymbolicName` / package, and
the required version range.

### Step 2 — Reconstruct the Dependency Chain

Walk from the consuming bundle outward (`Require-Bundle` / `Import-Package`) until you reach the
missing artifact. Record every intermediate bundle — the regression may live in an intermediate, not
the leaf.

### Step 3 — Extract & Compare MANIFEST.MF

Run the helper against a known-good and a broken copy of the suspect bundle. It reports the exact
`Require-Bundle` / `Import-Package` entries **added** or **removed** — a newly added hard dependency
that exists nowhere is the classic root cause.

> Always review the **full** header lists the helper prints, not only the delta — the surrounding
> dependency landscape provides the context that explains the failure.

### Step 4 — Build the Timeline (qualifier decode)

OSGi `Bundle-Version` qualifiers encode the build timestamp (`yyyyMMddHHmm`). The helper decodes them
so you can order builds and pinpoint when a dependency was introduced.

### Step 5 — Classify the Layout (p2 vs plain Eclipse)

A directory of plugin JARs is **not** automatically a Tycho-consumable p2 repository. Verify p2
metadata before treating any directory as a repo:

| Question | Check |
| :--- | :--- |
| Is it a p2 repository? | `content.xml`/`artifacts.xml` **or** `content.jar`/`artifacts.jar` present |
| Is it a plain Eclipse install? | launcher (`eclipse.exe`/`eclipse.ini` or a product `.exe`/`.ini`) + `eclipse/` dir |
| Can it be a PDE target directory? | `plugins/` with valid JARs (works as `<location type="Directory">`) |
| Can it be a Tycho p2 repo? | **Only** if p2 metadata exists |

### Step 6 — Design the Rollback

| Question | Yes | No |
| :--- | :--- | :--- |
| Does a known-good JAR exist? | → completeness check | → no standalone rollback |
| Is the JAR a complete OSGi bundle? (MANIFEST.MF + classes + `plugin.xml`/`OSGI-INF`) | → can build a local p2 repo | → cannot use for rollback |
| Is Eclipse `FeaturesAndBundlesPublisher` available? | → publish a proper p2 repo (preferred) | → add as PDE target directory (fallback) |
| Does the source have p2 metadata? | → reference as p2 repo directly | → publish a local p2 repo first |

Local p2 publish (preferred over a raw directory target):

```bash
eclipse -application org.eclipse.equinox.p2.publisher.FeaturesAndBundlesPublisher \
  -metadataRepository file:/<local_repo> \
  -artifactRepository file:/<local_repo> \
  -source <local_repo> -publishArtifacts
```

***

## 5. Related Remediation Skills

| Skill | Relationship |
| :--- | :--- |
| `maven-pom-audit` | Complementary — audits POM structure |
| `osgi-require-bundle-to-import-package` | Downstream — when the failure is an upstream `Bundle-SymbolicName` rename, migrate the consumer's `Require-Bundle` to `Import-Package` |
| `eclipse-pde-jdk-migration` §6 | Alternative IDE-only remediation for the same BSN-rename class of failure |

***

## 6. Composition by Higher-Level Skills

Organization-specific investigations add their own artifact-discovery layer on top of this base:

| Composer | Repo | Domain binding it adds |
| :--- | :--- | :--- |
| `toolbase_build_investigation` | `bosch_ai_agents` (org-private) | Scanning a shared component-store filesystem (the "toolbase") and its product installations for bundle versions |

A composer in a different repository MUST reference this base by **prose path** (locate by name in the
public `ai-agents` repo), never a cross-repository relative link — per the Standalone-Clone Test.

***

## 7. Prohibited Behaviors

- **Do not** treat a plain directory of JARs as a Tycho p2 repository without verifying p2 metadata.
- **Do not** compare only the leaf missing bundle — compare the full dependency chain.
- **Do not** report a bare "not found" — explain *why* an artifact is absent (renamed BSN, newer
  hard dependency, never published, etc.).
- **Do not** extract JARs in place into a read-only source tree — always extract to a temp directory.
