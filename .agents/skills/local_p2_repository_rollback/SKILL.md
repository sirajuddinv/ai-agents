<!--
title: Local P2 Repository Rollback
description: Create a self-contained local p2 repository from a known-good
    OSGi bundle JAR and redirect Tycho/PDE builds to use it — bypassing
    broken nightly p2 repositories without CI server access.
category: Build & Dependency Management
-->

# Local P2 Repository Rollback Skill

> **Skill ID:** `local_p2_repository_rollback`
> **Version:** 1.0.0
> **Standard:** [Agent Skills (agentskills.io)](https://agentskills.io)

## Description

Construct a fully functional local p2 repository from one or more
known-good OSGi bundle JARs and reconfigure Maven/Tycho (or PDE
target) builds to consume it — replacing a broken upstream p2
repository. The local p2 repo is Git-committed and uses relative
`file:${project.basedir}` paths, making it work identically on
developer machines and CI/CD Jenkins agents without any external
infrastructure changes.

This skill is the **implementation counterpart** to the
[Maven Build Failure Analysis](../maven_build_failure_analysis/SKILL.md)
skill's rollback options (specifically Option B.1 / §6.2.2
Approach 1). Use the analysis skill to diagnose the root cause
and identify the rollback target; use **this** skill to execute the
rollback.

**When to use this skill:**

- A nightly p2 repository introduces a broken bundle with an
  unresolvable dependency
- The upstream component version string is unknown (no CI server
  access, no parent POM cache)
- A known-good JAR exists locally (e.g., in a product build
  directory, toolbase, or artifact cache)
- The fix must work on **both** local developer machines and CI/CD
  Jenkins without pipeline changes
- Standard version pinning is impossible because the p2 repository
  URL uses shared CI variables (e.g., `${repository_Version}`)

**When NOT to use this skill:**

- The upstream component version string is known → use direct URL
  pinning instead (simpler, no binary in Git)
- The broken dependency is in a workspace bundle → fix the source
  code directly
- The issue is a PDE target definition conflict → use PDE target
  editing instead
- The broken bundle can be excluded via `feature.xml` or
  `MANIFEST.MF` edits → prefer source-level fix

## Prerequisites

| Requirement | Minimum |
|---|---|
| Build system | Maven 3.x + Tycho 2.x or 4.x |
| Java | JDK 8+ (for `jar` tool) |
| VCS | Git 2.x+ |
| Shell | PowerShell 5.1+ or Bash 4+ |
| Optional | Eclipse SDK with `FeaturesAndBundlesPublisher` (for automated metadata generation) |

***

## 1. Environment Verification

Before starting, the agent MUST verify:

### 1.1 Java `jar` Tool

```powershell
# PowerShell — verify jar tool is available
$jarTool = "jar"  # or explicit path, e.g., "c:\toolbase\java_jdk\11.0.16.1\bin\jar.exe"
& $jarTool --version
```

```bash
# Bash
jar --version
```

The `jar` tool is required for extracting `META-INF/MANIFEST.MF`
from bundle JARs to verify their contents.

### 1.2 Known-Good JAR Location

The agent MUST confirm the source JAR exists and is accessible:

```powershell
$sourceJar = "<path-to-known-good-jar>"
Test-Path $sourceJar
(Get-Item $sourceJar).Length  # Must be > 0
```

### 1.3 Workspace Write Access

The local p2 repo will be created inside the Git workspace. The
agent MUST verify write access to the target directory.

### 1.4 Eclipse SDK (Optional — for FeaturesAndBundlesPublisher)

If an Eclipse SDK is available, the agent SHOULD use it for
automated p2 metadata generation. If not, the agent MUST generate
`content.xml` and `artifacts.xml` manually (see §3).

```powershell
# Search for Eclipse SDK with the publisher application
Get-ChildItem "<eclipse-sdk-path>/plugins" -Filter "*p2.publisher*" |
    Select-Object Name
```

***

## 2. Source JAR Validation

Before creating the local p2 repository, the agent MUST validate
the source JAR to confirm it is the correct known-good version and
does NOT contain the broken dependency.

### 2.1 Extract and Inspect MANIFEST.MF

```powershell
$tempDir = "$env:TEMP\p2_validate_$(Get-Date -Format 'yyyyMMddHHmmss')"
New-Item -ItemType Directory -Path $tempDir -Force | Out-Null
Push-Location $tempDir
& $jarTool xf $sourceJar META-INF/MANIFEST.MF
Get-Content "META-INF\MANIFEST.MF"
Pop-Location
```

### 2.2 Mandatory Verification Checklist

The agent MUST verify ALL of the following before proceeding:

| Check | What to Verify | Failure Action |
|---|---|---|
| Bundle-SymbolicName | Matches the expected bundle symbolic name | ⛔ STOP — wrong JAR |
| Bundle-Version | Contains the expected known-good qualifier timestamp | ⛔ STOP — wrong version |
| Require-Bundle | Does NOT contain the broken dependency | ⛔ STOP — this IS the broken version |
| singleton | If `singleton:=true`, only one version can be active in the runtime | ⚠️ Note — affects p2 resolution |
| Bundle-RequiredExecutionEnvironment | Compatible with the project's JDK level | ⚠️ Note — may need attention |

### 2.3 Collect JAR Metadata

The agent MUST collect the following for p2 metadata generation:

```powershell
# File size (needed for artifacts.xml)
$jarSize = (Get-Item $sourceJar).Length

# MD5 hash (needed for artifacts.xml download verification)
$jarMD5 = (Get-FileHash $sourceJar -Algorithm MD5).Hash.ToLower()

# Bundle-SymbolicName and Bundle-Version (from MANIFEST.MF)
$manifest = Get-Content "$tempDir\META-INF\MANIFEST.MF" -Raw
# Parse these from the manifest content
```

***

## 3. Local P2 Repository Creation

### 3.1 Directory Structure

The local p2 repository MUST follow this exact structure:

```
<workspace-root>/
  <files-module>/local_p2_repos/<rollback-name>/
    content.xml          ← p2 metadata (installable units)
    artifacts.xml        ← p2 artifact metadata (sizes, hashes, paths)
    plugins/
      <bundle-symbolic-name>_<version>.jar   ← the known-good JAR
```

**Naming convention:** The rollback directory name SHOULD follow the
pattern `<component>_rollback` (e.g., `ecl_ubk_valfrw_rollback`).

### 3.2 Create Directory and Copy JAR

```powershell
$workspace = "<workspace-root>"
$repoDir = "$workspace/<files-module>/local_p2_repos/<rollback-name>"
$pluginsDir = "$repoDir/plugins"

# Create directory structure
New-Item -ItemType Directory -Path $pluginsDir -Force | Out-Null

# Copy the known-good JAR
Copy-Item $sourceJar -Destination $pluginsDir

# Verify the copy
$copiedJar = Get-ChildItem $pluginsDir -Filter "*.jar"
Write-Host "Copied: $($copiedJar.Name) ($($copiedJar.Length) bytes)"
```

### 3.3 Generate P2 Metadata

There are two approaches to generating p2 metadata:

#### Approach A — Eclipse FeaturesAndBundlesPublisher (preferred)

If an Eclipse SDK with the publisher application is available:

```powershell
$eclipsec = "<eclipse-sdk-path>/eclipsec.exe"   # or eclipse on Linux
$repoUri = "file:/" + ($repoDir -replace '\\','/')

& $eclipsec -nosplash `
  -application org.eclipse.equinox.p2.publisher.FeaturesAndBundlesPublisher `
  -metadataRepository $repoUri `
  -artifactRepository $repoUri `
  -source $repoDir `
  -publishArtifacts `
  -consolelog
```

After running, verify that `content.xml` (or `content.jar`) and
`artifacts.xml` (or `artifacts.jar`) were created in `$repoDir`.

#### Approach B — Manual XML Generation (when no Eclipse SDK available)

When the Eclipse publisher is not available (or fails due to
workspace lock issues), the agent MUST generate the p2 metadata
XML files manually. The formats are well-documented and
straightforward for single-bundle repositories.

##### 3.3.1 `content.xml` — Installable Unit Metadata

The `content.xml` declares the installable unit (IU) — the p2
representation of an OSGi bundle. It MUST include:

- **`<unit>`**: The IU element with `id` (Bundle-SymbolicName),
  `version` (Bundle-Version), and `singleton` attribute
- **`<provides>`**: All capabilities the bundle provides:
  - `org.eclipse.equinox.p2.iu` — the IU itself
  - `osgi.bundle` — the OSGi bundle identity
  - `java.package` — one entry per exported package (from
    `Export-Package` in MANIFEST.MF)
  - `org.eclipse.equinox.p2.eclipse.type` = `bundle`
  - `org.eclipse.equinox.p2.localization` = `df_LT` (if localized)
- **`<requires>`**: All dependencies from `Require-Bundle` in
  MANIFEST.MF, each as a `<required>` element with `namespace`
  `osgi.bundle` and `range` matching the bundle-version constraint
- **`<artifacts>`**: Reference to the artifact in `artifacts.xml`
- **`<touchpoint>`**: Standard OSGi touchpoint
  (`org.eclipse.equinox.p2.osgi`, version `1.0.0`)
- **`<touchpointData>`**: Manifest instruction and `zipped=true`

**Template structure:**

```xml
<?xml version='1.0' encoding='UTF-8'?>
<?metadataRepository version='1.1.0'?>
<repository name='<rollback-name>'
    type='org.eclipse.equinox.internal.p2.metadata.repository.LocalMetadataRepository'
    version='1'>
  <properties size='2'>
    <property name='p2.timestamp' value='<epoch-millis>'/>
    <property name='p2.compressed' value='false'/>
  </properties>
  <units size='<number-of-bundles>'>
    <unit id='<Bundle-SymbolicName>' version='<Bundle-Version>'
          singleton='<true|false>'>
      <update id='<Bundle-SymbolicName>'
              range='[0.0.0,<Bundle-Version>)' severity='0'/>
      <properties size='...'>
        <property name='org.eclipse.equinox.p2.name'
                  value='<Bundle-Name-or-%pluginName>'/>
        <property name='org.eclipse.equinox.p2.provider'
                  value='<Bundle-Vendor>'/>
        <!-- additional properties as needed -->
      </properties>
      <provides size='...'>
        <provided namespace='org.eclipse.equinox.p2.iu'
                  name='<Bundle-SymbolicName>'
                  version='<Bundle-Version>'/>
        <provided namespace='osgi.bundle'
                  name='<Bundle-SymbolicName>'
                  version='<Bundle-Version>'/>
        <!-- One entry per Export-Package -->
        <provided namespace='java.package'
                  name='<package.name>' version='0.0.0'/>
        <!-- ... -->
        <provided namespace='org.eclipse.equinox.p2.eclipse.type'
                  name='bundle' version='1.0.0'/>
      </provides>
      <requires size='<count>'>
        <!-- One entry per Require-Bundle dependency -->
        <required namespace='osgi.bundle'
                  name='<dependency-symbolic-name>'
                  range='<version-range-or-0.0.0>'/>
        <!-- ... -->
      </requires>
      <artifacts size='1'>
        <artifact classifier='osgi.bundle'
                  id='<Bundle-SymbolicName>'
                  version='<Bundle-Version>'/>
      </artifacts>
      <touchpoint id='org.eclipse.equinox.p2.osgi' version='1.0.0'/>
      <touchpointData size='1'>
        <instructions size='2'>
          <instruction key='manifest'>
            <!-- Key MANIFEST.MF headers, &#xA; separated -->
          </instruction>
          <instruction key='zipped'>true</instruction>
        </instructions>
      </touchpointData>
    </unit>
  </units>
</repository>
```

**Critical rules for `content.xml` generation:**

1. **`Export-Package` parsing:** The agent MUST parse the
   `Export-Package` header from MANIFEST.MF and create one
   `<provided namespace='java.package'>` entry per exported
   package. Packages are comma-separated in the header; each
   may have attributes (e.g., `version=`, `uses:=`) which
   should be stripped for the `name` attribute.

2. **`Require-Bundle` parsing:** The agent MUST parse the
   `Require-Bundle` header and create one `<required>` entry
   per dependency. Strip attributes like `bundle-version=`,
   `visibility:=`, `resolution:=`. Use `range='0.0.0'` unless
   a specific `bundle-version` is specified.

3. **Singleton handling:** If MANIFEST.MF contains
   `singleton:=true`, the `<unit>` element MUST have
   `singleton='true'`. This tells p2 that only one version of
   this bundle can be active.

4. **Line continuation:** MANIFEST.MF uses 70-byte line wrapping
   with continuation lines starting with a single space. The
   agent MUST reassemble wrapped lines before parsing.

##### 3.3.2 `artifacts.xml` — Artifact Repository Metadata

The `artifacts.xml` declares the physical artifact location, size,
and checksums. It MUST include:

- **Mapping rules** for bundle, binary, and feature classifiers
- **Artifact entry** with `classifier='osgi.bundle'`, `id`, and
  `version`
- **Properties**: `artifact.size`, `download.size` (same value —
  both are the JAR file size in bytes), and `download.md5`

**Template structure:**

```xml
<?xml version='1.0' encoding='UTF-8'?>
<?artifactRepository version='1.1.0'?>
<repository name='<rollback-name>'
    type='org.eclipse.equinox.internal.p2.artifact.repository.simple.SimpleArtifactRepository'
    version='1'>
  <properties size='2'>
    <property name='p2.timestamp' value='<epoch-millis>'/>
    <property name='p2.compressed' value='false'/>
  </properties>
  <mappings size='3'>
    <rule filter='(&amp; (classifier=osgi.bundle))'
          output='${repoUrl}/plugins/${id}_${version}.jar'/>
    <rule filter='(&amp; (classifier=binary))'
          output='${repoUrl}/binary/${id}_${version}'/>
    <rule filter='(&amp; (classifier=org.eclipse.update.feature))'
          output='${repoUrl}/features/${id}_${version}.jar'/>
  </mappings>
  <artifacts size='<number-of-artifacts>'>
    <artifact classifier='osgi.bundle'
              id='<Bundle-SymbolicName>'
              version='<Bundle-Version>'>
      <properties size='3'>
        <property name='artifact.size' value='<file-size-bytes>'/>
        <property name='download.size' value='<file-size-bytes>'/>
        <property name='download.md5' value='<md5-lowercase>'/>
      </properties>
    </artifact>
  </artifacts>
</repository>
```

**Critical rules for `artifacts.xml` generation:**

1. **Mapping rules are mandatory.** Without the `<mappings>`
   section, Tycho cannot locate the JAR file in the `plugins/`
   directory. The three standard rules (bundle, binary, feature)
   MUST always be included.

2. **The `${repoUrl}` variable** in mapping rules is resolved
   by Tycho at runtime to the repository's root URL. Do NOT
   hardcode paths.

3. **MD5 hash MUST be lowercase.** PowerShell's `Get-FileHash`
   returns uppercase — convert with `.ToLower()`.

4. **File size MUST be exact.** Use `(Get-Item $jar).Length`
   or `stat -f%z` on macOS / `stat -c%s` on Linux.

***

## 4. POM Configuration

### 4.1 Identify the Repository to Replace

The agent MUST locate the broken p2 repository declaration in the
Tycho POM(s). Typically found in:

- `<project>/pom.xml` → `<repositories>` section
- Or in a parent/aggregator POM

Search for the repository ID:

```powershell
Select-String -Path "**/pom.xml" -Pattern "<id>ecl_ubk_valfrw</id>" -Recurse
```

### 4.2 Replace with Local P2 Repository URL

The POM change MUST:

1. **Preserve the original URL in an XML comment** — for easy
   revert when the upstream is fixed
2. **Use `file:${project.basedir}/../...` relative path** — this
   resolves correctly on both local machines and CI/CD Jenkins
3. **Keep the same `<id>`** — other POM elements may reference
   this repository ID

**Template POM change:**

```xml
<!-- ROLLBACK: <component> pinned to known-good <date> build -->
<!-- (see <investigation-doc-path> §<section>) -->
<!-- Original URL: <original-url> -->
<repository>
<id><original-repo-id></id>
<url>file:${project.basedir}/../<files-module>/local_p2_repos/<rollback-name></url>
<layout>p2</layout>
</repository>
```

### 4.3 Apply to ALL Tycho POMs

The agent MUST search for and update ALL POMs that reference the
broken repository. Common locations:

- Main Tycho aggregator POM (e.g., `*.tycho/pom.xml`)
- Standalone/product Tycho POM (e.g., `*.standalone.tycho/pom.xml`)
- Any other POM that declares the same `<repository>` block

```powershell
# Find all POMs referencing the broken repo
Get-ChildItem -Recurse -Filter "pom.xml" |
    Select-String -Pattern "<id><broken-repo-id></id>" |
    Select-Object Filename, LineNumber
```

### 4.4 Why `file:${project.basedir}` Works Everywhere

| Environment | `${project.basedir}` Resolves To | Result |
|---|---|---|
| Local developer machine | Absolute path to POM's directory (e.g., `C:\work\...\*.tycho`) | ✅ Correct |
| Jenkins (Linux agent) | `/var/lib/jenkins/workspace/<job>/.../*.tycho` | ✅ Correct |
| Jenkins (Windows agent) | `C:\jenkins\workspace\<job>\.../*.tycho` | ✅ Correct |
| Docker container | `/workspace/.../*.tycho` | ✅ Correct |
| GitHub Actions | `/home/runner/work/<repo>/<repo>/.../*.tycho` | ✅ Correct |

`${project.basedir}` is a **Maven built-in property** — it always
resolves to the directory containing the current `pom.xml`. The
relative `../` path then navigates to the workspace root, which
is always consistent after a `git clone`.

***

## 5. Post-Creation Verification

### 5.1 Verify P2 Repository Structure

```powershell
$repoDir = "<path-to-local-p2-repo>"

# 1. Check p2 metadata exists
$hasContent = (Test-Path "$repoDir/content.xml") -or
              (Test-Path "$repoDir/content.jar")
$hasArtifacts = (Test-Path "$repoDir/artifacts.xml") -or
                (Test-Path "$repoDir/artifacts.jar")

if ($hasContent -and $hasArtifacts) {
    Write-Host "PASS: p2 metadata present"
} else {
    Write-Host "FAIL: Missing metadata — content=$hasContent, artifacts=$hasArtifacts"
}

# 2. Check plugin JAR exists
Get-ChildItem "$repoDir/plugins" -Filter "*.jar" |
    Select-Object Name, Length

# 3. Verify MANIFEST.MF does NOT contain the broken dependency
$tempDir = "$env:TEMP/p2_verify"
New-Item -ItemType Directory -Path $tempDir -Force | Out-Null
Push-Location $tempDir
& jar xf "$repoDir/plugins/<bundle-jar>" META-INF/MANIFEST.MF
$manifest = Get-Content "META-INF/MANIFEST.MF" -Raw
if ($manifest -match "<broken-dependency-name>") {
    Write-Host "FAIL: JAR contains the broken dependency!"
} else {
    Write-Host "PASS: JAR does NOT contain the broken dependency"
}
Pop-Location
```

### 5.2 Verify POM Path Resolution

```powershell
# Simulate Maven's ${project.basedir} resolution
$tychoPomDir = "<path-to-tycho-pom-directory>"
$relativePath = "../<files-module>/local_p2_repos/<rollback-name>"
$resolvedPath = Join-Path (Resolve-Path $tychoPomDir) $relativePath

if (Test-Path $resolvedPath) {
    Write-Host "PASS: POM path resolves correctly to: $(Resolve-Path $resolvedPath)"
    Get-ChildItem (Resolve-Path $resolvedPath) | Select-Object Name
} else {
    Write-Host "FAIL: Path does not resolve: $resolvedPath"
}
```

### 5.3 Test Build

```powershell
# Quick test — build only the first module that was failing
mvn clean verify -pl <first-failing-module> 2>&1 |
    Select-String -Pattern "<broken-dependency>|<bundle-name>"

# Full build
mvn clean verify 2>&1 | Tee-Object -FilePath "build_rollback_test.log"

# Verify no references to the broken dependency remain
Select-String -Path "build_rollback_test.log" -Pattern "<broken-dependency>"
# Expected: NO matches
```

***

## 6. Git Commit Strategy

### 6.1 Single Atomic Commit

The local p2 repo creation and POM updates MUST be committed as a
**single atomic commit**. This ensures `git revert` cleanly undoes
the entire rollback.

**Files to include in one commit:**

1. `<files-module>/local_p2_repos/<rollback-name>/content.xml`
2. `<files-module>/local_p2_repos/<rollback-name>/artifacts.xml`
3. `<files-module>/local_p2_repos/<rollback-name>/plugins/<bundle>.jar`
4. `<tycho-pom>/pom.xml` (updated URL)
5. `<standalone-tycho-pom>/pom.xml` (updated URL, if applicable)

### 6.2 Commit Message Template

```
fix: rollback <component> to known-good <date> via local p2 repo

The <component> nightly (<nightly-date>) introduced a broken dependency
on <missing-bundle> in <bundle-name> <nightly-version> — a bundle
that does not exist anywhere.

Changes:
- Add local p2 repo at <files-module>/local_p2_repos/<rollback-name>/
  with:
  - plugins/<bundle-jar>
  - content.xml (p2 metadata)
  - artifacts.xml (p2 artifact metadata)
- Update <component> repo URL in <N> Tycho POM(s) to use
  file:${project.basedir}/../.../ relative path (works on both
  local dev builds and CI/CD Jenkins)

Original URL preserved in XML comments for easy revert.

Revert this commit when <component> team fixes the missing
<missing-bundle> bundle upstream.
```

### 6.3 Revert Procedure

When the upstream team fixes the broken dependency:

```bash
git revert <rollback-commit-hash>
```

This single command restores the original POM URLs and removes the
local p2 repo directory.

***

## 7. Multi-Bundle Repositories

When multiple bundles need rollback from the same component, the
same local p2 repository can contain multiple JARs:

### 7.1 Directory Structure

```
local_p2_repos/<rollback-name>/
  content.xml          ← contains multiple <unit> elements
  artifacts.xml        ← contains multiple <artifact> elements
  plugins/
    <bundle-1>_<version>.jar
    <bundle-2>_<version>.jar
    <bundle-3>_<version>.jar
```

### 7.2 Metadata Updates

- **`content.xml`**: Add one `<unit>` element per bundle inside
  `<units>`. Update `<units size='N'>` to match the count.
- **`artifacts.xml`**: Add one `<artifact>` element per bundle
  inside `<artifacts>`. Update `<artifacts size='N'>` to match.

### 7.3 Consistency Rule

All bundles in a multi-bundle rollback MUST come from the **same
known-good source** (e.g., the same product build directory) to
ensure version compatibility. Mixing bundles from different builds
may introduce subtle runtime errors.

***

## 8. Common Pitfalls

| # | Pitfall | Consequence | Prevention |
|---|---|---|---|
| 1 | Missing `content.xml`/`artifacts.xml` | Tycho error: `No repository found at file:/...` | Always generate p2 metadata — a plain directory of JARs is NOT a p2 repository |
| 2 | Wrong JAR version (broken nightly instead of known-good) | Build still fails with the same error | Always verify MANIFEST.MF before creating the repo (§2.2) |
| 3 | Absolute `file:` path in POM (e.g., `file:///c:/work/...`) | Works locally, breaks on Jenkins | Always use `file:${project.basedir}/../...` relative path |
| 4 | Missing POM update in standalone/product Tycho POM | Main build passes but product build fails | Search ALL POMs for the repository ID (§4.3) |
| 5 | Forgetting to commit the binary JAR | Build fails on other machines — local p2 repo is empty | Use `git add` on the entire `local_p2_repos/` directory |
| 6 | Uppercase MD5 in `artifacts.xml` | Some p2 implementations reject the hash | Always `.ToLower()` the MD5 hash |
| 7 | POM has wrong `<layout>` | Tycho ignores the repo or fails | Must be `<layout>p2</layout>` |
| 8 | Multiple POMs, only one updated | Partial fix — some builds pass, others fail | Grep for ALL occurrences of the repo ID |
| 9 | Committing local p2 repo and POM changes in separate commits | `git revert` cannot cleanly undo the rollback | Always use a single atomic commit |
| 10 | Leaving the rollback permanently after upstream is fixed | Stale binary in Git, divergence from upstream | Add a TODO/reminder to revert when upstream is fixed |

***

## 9. Checklist

The agent MUST verify ALL items before declaring the rollback
complete:

- [ ] Source JAR validated — MANIFEST.MF does NOT contain the
      broken dependency
- [ ] Source JAR validated — Bundle-SymbolicName and Bundle-Version
      match expectations
- [ ] `plugins/` directory contains the JAR with correct filename
      (`<symbolic-name>_<version>.jar`)
- [ ] `content.xml` exists and declares correct `<unit>` with
      matching `id` and `version`
- [ ] `content.xml` has correct `<provides>` entries (IU, bundle,
      packages)
- [ ] `content.xml` has correct `<requires>` entries (all
      `Require-Bundle` dependencies, EXCLUDING the broken one)
- [ ] `artifacts.xml` exists with correct `<artifact>` entry
- [ ] `artifacts.xml` has correct file size and MD5 hash
- [ ] `artifacts.xml` has all 3 standard mapping rules
- [ ] POM updated in main Tycho aggregator — URL uses
      `file:${project.basedir}/../...`
- [ ] POM updated in standalone Tycho (if applicable) — same URL
- [ ] Original URL preserved in XML comment above the `<repository>`
      element
- [ ] `file:${project.basedir}` path resolves correctly from the
      POM directory to the local p2 repo
- [ ] All files committed in a single atomic commit
- [ ] Commit message includes revert instructions
- [ ] Build passes locally with `mvn clean verify`

***

## 10. Prohibitions

The agent MUST NOT:

1. **Use absolute `file:` paths in POMs** — these break on CI/CD
   and other developer machines
2. **Skip p2 metadata generation** — Tycho rejects directories
   without `content.xml`/`artifacts.xml`
3. **Use the broken JAR** — always verify MANIFEST.MF first
4. **Split the rollback across multiple commits** — must be one
   atomic commit for clean `git revert`
5. **Modify the source JAR** — the JAR must be an exact byte-for-
   byte copy of the known-good original
6. **Hardcode CI-specific paths** — the solution must work
   everywhere without environment-specific configuration
7. **Leave rollback in place permanently** — document the revert
   procedure and add a TODO for cleanup
8. **Generate p2 metadata with incorrect dependency lists** — the
   `<requires>` in `content.xml` must exactly match the JAR's
   MANIFEST.MF `Require-Bundle` entries
