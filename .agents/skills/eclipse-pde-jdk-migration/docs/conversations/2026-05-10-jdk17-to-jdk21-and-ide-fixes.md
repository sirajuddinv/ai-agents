# JDK 17 → 21 Reapplication & IDE-Only Side Issues

**Date**: 2026-05-10
**Scope**: Re-apply the `eclipse-pde-jdk-migration` skill to a second
workspace (`<workspace-root-21>`) already targeting Eclipse Orion 14 +
JDK 21, then fix three side issues that surfaced only in the IDE
(never in CI/Tycho).

---

## Phase A — Cross-Version Reapplication (Skill Validation)

Ran `Survey-JrePins.ps1 -TargetEE JavaSE-21` against the new workspace.
Inventory:

| Surface | Count | Action |
|---|---|---|
| `.classpath` pinned to `JavaSE-17` | 1 | unpin |
| `.launch` pinned to `JavaSE-17` | 13 | repoint to `JavaSE-21` |
| `MANIFEST.MF` `JavaSE-17` | 1 | leave (forward-compatible) |
| `MANIFEST.MF` `JavaSE-1.8` | 40 | leave |
| PermGen residuals | 0 | n/a |

Applied per skill Phase 3.1 + 3.3. No `--add-opens` changes (the
Phase 4 5-flag set is unchanged between JDK 17 and JDK 21).

Total edits: 14 files. Re-run survey reported all clean.

**New skill row added to decision matrix** (Phase 2):
"`MANIFEST.MF` already on a *newer* EE than `<OLD>` → leave."

---

## Side Issue 1 — Empty Source Folder Paradox

```text
Project '<plugin-with-empty-src>' is missing required source folder: 'src'
```

…but creating `src` via Eclipse → "already exists". The folder was on
disk but empty. Git does not track empty directories, so the import
landed in a state Eclipse's JDT model couldn't reconcile.

Fix:

- `New-Item <project>/src/.gitkeep` so Git carries the folder.
- F5 → Project → Clean.

Promoted to skill **Phase 7.1**.

---

## Side Issue 2 — Bundle Symbolic-Name Mismatch

```text
Bundle 'org.apache.commons.commons-io' cannot be resolved
  MANIFEST.MF (<consumer-plugin-A>, line 22)
```

Diagnosis:

- 2 manifests declare the Maven-style name `org.apache.commons.commons-io`
- The local Orion target ships only the legacy Orbit name
  `org.apache.commons.io_2.x.y.jar`
- CI/Tycho uses a *different* target platform that does ship the new
  name, so editing `MANIFEST.MF` would break CI

Constraint: any fix must be local to the IDE only — no manifest, no
`pom.xml`, no shared `.target` schema change beyond an additive
`<location>`.

Reference precedent in repo: commit `<internal-precedent-commit>` added a Maven location
to the same `<active>.target` for JNA. Reused that pattern with a bnd
`<instructions>` override to force the synthesized OSGi
`Bundle-SymbolicName`:

```xml
<location includeDependencyScope="compile" includeSource="true"
    missingManifest="generate" type="Maven">
    <dependencies>
        <dependency>
            <groupId>commons-io</groupId>
            <artifactId>commons-io</artifactId>
            <version>2.22.0</version>
            <type>jar</type>
        </dependency>
    </dependencies>
    <instructions><![CDATA[
Bundle-Name:           Apache Commons IO (Maven-style alias for Orion)
Bundle-SymbolicName:   org.apache.commons.commons-io;singleton:=true
Bundle-Version:        ${version_cleanup;${mvnVersion}}
Import-Package:        *;resolution:=optional
Export-Package:        *;version="${version_cleanup;${mvnVersion}}";-noimport:=true
]]></instructions>
</location>
```

The default generated symbolic name would be `commons-io.commons-io` —
the bnd override forces it to `org.apache.commons.commons-io`,
satisfying every consumer's `Require-Bundle` clause.

Promoted to skill **Phase 6** (with full subsections on detection,
the hard constraint, the fix, and the reload protocol).

---

## Side Issue 3 — m2e Cannot See the Corporate Proxy

After applying Side Issue 2, target reload failed:

```text
Could not transfer artifact commons-io:commons-io:jar:2.22.0
from/to central (https://repo.maven.apache.org/maven2):
No such host is known (repo.maven.apache.org)
```

`Test-NetConnection repo.maven.apache.org -Port 443` confirmed DNS
itself was failing — yet the OS `HTTP_PROXY` / `HTTPS_PROXY` env vars
were set to `http://<corp-proxy-host>:<corp-proxy-port>`.

Root cause: **m2e (Maven for Eclipse) does not read OS env proxy
variables**. Maven only consults `~/.m2/settings.xml`. The file did
not exist on this machine.

Fix: created `~/.m2/settings.xml` with `<proxies>` for both `http`
and `https` protocols, including a `<nonProxyHosts>` clause for
internal hosts. Restarted Eclipse so m2e re-read settings at startup.

Verification before Eclipse restart:

```powershell
Test-NetConnection <corp-proxy-host> -Port <corp-proxy-port> -InformationLevel Quiet  # True
Invoke-WebRequest -Proxy 'http://<corp-proxy-host>:<corp-proxy-port>' `
    -Uri 'https://repo.maven.apache.org/maven2/commons-io/commons-io/2.22.0/commons-io-2.22.0.pom' `
    -UseBasicParsing -TimeoutSec 15
# HTTP 200, 20275 bytes
```

After restart + Reload Target Platform, the Maven location reported
"2 plug-ins available" (jar + sources) and both `MANIFEST.MF` errors
cleared.

Promoted to skill **Phase 6.5** (m2e proxy gotcha) and **6.6** (stale
`.lastUpdated` failure markers — also encountered: prior failed
attempts at versions 2.16.1 / 2.18.0 / 2.22.0 had left
`*.jar.lastUpdated` files in the local repo that suppressed retries
until deleted).

---

## Portability Considerations Raised

The user explicitly required every fix to be **portable** and
**CI-safe**:

- `MANIFEST.MF` edits → forbidden (CI consumes manifests)
- `pom.xml` edits → forbidden (CI consumes POMs)
- `*.target` edits → allowed (CI uses a separate target / not at all)
- `~/.m2/settings.xml` → allowed (per-user, not in repo, standard
- Side-loading jars into `~/.m2/repository` → rejected as
  standard corporate developer setup)
  non-portable (per-developer manual step; depended on a specific
  toolbase jar path)

Result: every fix is either workspace-wide via the `.target` file
(committable, CI-ignored) or per-user via `~/.m2/settings.xml`
(standard, expected on any corporate dev machine).

---

## Skill Updates Triggered by This Session

| Section | Change |
|---|---|
| Front-matter `description` | Expanded to mention IDE-side scope |
| Phase 2 decision matrix | New row for higher-than-`<OLD>` MANIFEST EE |
| **Phase 6 (NEW)** | Target-platform symbolic-name aliasing |
| **Phase 7 (NEW)** | IDE state hygiene (empty src, forward-compat EEs, bundled JRE) |
| Phase 6 → renamed Phase 8 | Atomic Commit Arrangement |
| Prohibited Behaviors | Three new prohibitions (manifest-rewrite, m2 side-load, manual empty src) |
| Related Conversations | This file added |
