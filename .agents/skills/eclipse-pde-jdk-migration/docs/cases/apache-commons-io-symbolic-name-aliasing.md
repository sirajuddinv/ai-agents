# Case Study — Apache Commons IO Symbolic-Name Aliasing

> **Triggers Phase**: [SKILL.md §6 — Target-Platform Symbolic-Name Aliasing](../SKILL.md#phase-6--target-platform-symbolic-name-aliasing-ide-only)
>
> **Date observed**: 2026-05-10 on `<workspace-root-21>` (JDK 21 / Eclipse Orion 14)

This case study captures a complete, reproducible instance of the
Eclipse Orbit symbolic-name renaming problem so future agents can
recognise it instantly and apply the fix without re-deriving it.

---

## 1. Symptom

In the Eclipse Problems view (no compile errors, no Maven errors,
target-resolution-only):

```text
Description                                                     Resource      Path                               Location  Type
Bundle 'org.apache.commons.commons-io' cannot be resolved       MANIFEST.MF   /<consumer-plugin-A>/META-INF      line 22   Plug-in Problem
Bundle 'org.apache.commons.commons-io' cannot be resolved       MANIFEST.MF   /<consumer-plugin-B>/META-INF      line 17   Plug-in Problem
```

The CI/Tycho/Maven build does **not** report these errors — they are
IDE-only.

---

## 2. Background — Why Two Names Exist

Eclipse Orbit historically generated OSGi bundle symbolic names by
hand, producing names like `org.apache.commons.io`. Starting with
Orbit R2024-09, Orbit shifted to **Maven-coordinate-derived** names:

| Era | Symbolic name produced by Orbit |
|---|---|
| Orbit ≤ R2024-06 | `org.apache.commons.io` |
| Orbit ≥ R2024-09 | `org.apache.commons.commons-io` (i.e., `<groupId>.<artifactId>`) |

Both Orbit jars carry **byte-identical** Apache class files; only the
`Bundle-SymbolicName` MANIFEST attribute differs.

A workspace whose `MANIFEST.MF` files were generated against the new
Orbit will declare `Require-Bundle: org.apache.commons.commons-io`. A
workspace's local target platform that was assembled from an older
will only ship `org.apache.commons.io_*.jar` — the resolution fails.
Orbit (or a an internally-hosted Orbit mirror that has not yet refreshed)

---

## 3. Discovery Commands

Confirm the diagnosis before applying a fix:

```powershell
# 1. Find every workspace MANIFEST that references commons-io (any spelling)
Get-ChildItem -Path '<workspace-root>' -Recurse -Filter MANIFEST.MF |
    Select-String -Pattern 'commons[\.-]io' |
    ForEach-Object { "$($_.Path):$($_.LineNumber): $($_.Line.Trim())" }

# 2. Inspect the active target file to find the directories it scans
Get-ChildItem '<workspace-root>' -Recurse -Include *.target |
    ForEach-Object { Write-Host "==> $($_.Name)"; Get-Content $_.FullName }

# 3. Check what each scanned directory actually ships
@('<dir-1>', '<dir-2>', '<dir-3>') | ForEach-Object {
    Write-Host "==> $_"
    Get-ChildItem -LiteralPath $_ -Filter '*commons*io*' -ErrorAction SilentlyContinue |
        Select-Object -ExpandProperty Name
}
```

Expected disagreement: manifests demand `org.apache.commons.commons-io`,
target ships only `org.apache.commons.io_2.x.y.jar`.

---

## 4. Constraint Map (Why the Obvious Fix Is Wrong)

| Candidate fix | Verdict | Why |
|---|---|---|
| Rename `MANIFEST.MF` `Require-Bundle` to legacy name | ❌ FORBIDDEN | CI/Tycho consumes manifests; CI's target platform may ship the new name and would break |
| Rename `MANIFEST.MF` to legacy name + edit CI target too | ❌ Out of scope | Skill explicitly forbids touching CI/Tycho-managed files |
| Drop a shim JAR into Eclipse `dropins/` | ⚠️ Not portable | Per-machine manual install step |
| Side-load a jar into `~/.m2/repository` | ❌ Not portable | Per-developer manual one-off; depends on toolbase paths |
| **Add a Maven `<location>` with bnd `<instructions>` override** | ✅ CHOSEN | Workspace-wide via committed `.target`; Maven Central is universally reachable; CI ignores this `.target` |
| Add a Directory `<location>` pointing into `<toolbase>\…` | ⚠️ Not portable | Hard-codes per-machine toolbase paths into committed `.target` |

---

## 5. Applied Fix — `.target` Diff

Workspace file (symbolic): `<target-platform-host-plugin>/<active>.target`

```diff
 <?xml version="1.0" encoding="UTF-8" standalone="no"?>
 <?pde version="3.8"?>
 <target>
     <locations>
         <location path="<toolbase>\<product-host>\eclipse\plugins" type="Directory"/>
         <location path="<toolbase>\<product-cdt>\eclipse\plugins" type="Directory"/>
         <location path="<toolbase>\<product-orbit>\eclipse\plugins" type="Directory"/>
+        <location includeDependencyScope="compile" includeSource="true"
+            missingManifest="generate" type="Maven">
+            <dependencies>
+                <dependency>
+                    <groupId>commons-io</groupId>
+                    <artifactId>commons-io</artifactId>
+                    <version>2.22.0</version>
+                    <type>jar</type>
+                </dependency>
+            </dependencies>
+            <instructions><![CDATA[
+Bundle-Name:           Apache Commons IO (Maven-style alias for Orion)
+Bundle-SymbolicName:   org.apache.commons.commons-io;singleton:=true
+Bundle-Version:        ${version_cleanup;${mvnVersion}}
+Import-Package:        *;resolution:=optional
+Export-Package:        *;version="${version_cleanup;${mvnVersion}}";-noimport:=true
+]]></instructions>
+        </location>
     </locations>
 </target>
```

### Anatomy of the bnd `<instructions>` block

| Directive | Purpose |
|---|---|
| `Bundle-Name` | Human-readable label visible in Plug-ins view |
| `Bundle-SymbolicName: <forced-name>;singleton:=true` | Overrides the default `<groupId>.<artifactId>` (which would have been `commons-io.commons-io`). `singleton:=true` matches the typical OSGi declaration for utility libs |
| `Bundle-Version: ${version_cleanup;${mvnVersion}}` | Converts Maven version (`2.22.0`) to OSGi version (`2.22.0`) — the macro strips qualifiers like `-SNAPSHOT` |
| `Import-Package: *;resolution:=optional` | Synthesised wrapper bundle does NOT demand transitive deps the target may lack |
| `Export-Package: *;version="…";-noimport:=true` | Re-exports every Apache package; `-noimport:=true` prevents the bundle from importing what it just exported |

---

## 6. Companion Fix — `~/.m2/settings.xml` for Corporate Proxy

The Maven location is useless if m2e cannot reach Maven Central. In a
a corporate environment the OS sets `HTTP_PROXY` /
`HTTPS_PROXY=http://<corp-proxy-host>:<corp-proxy-port>`, but **m2e ignores OS
proxy env vars**. Without `~/.m2/settings.xml` Eclipse fails with:

```text
Could not transfer artifact commons-io:commons-io:jar:2.22.0
from/to central (https://repo.maven.apache.org/maven2):
No such host is known (repo.maven.apache.org)
```

User-scoped fix (per machine, never committed):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<settings xmlns="http://maven.apache.org/SETTINGS/1.0.0">
  <proxies>
    <proxy>
      <id>corp-https</id>
      <active>true</active>
      <protocol>https</protocol>
      <host><corp-proxy-host></host>
      <port>8080</port>
      <nonProxyHosts>127.0.0.1|localhost|*.<corp-domain>|*.<corp-cloud-domain></nonProxyHosts>
    </proxy>
    <proxy>
      <id>corp-http</id>
      <active>true</active>
      <protocol>http</protocol>
      <host><corp-proxy-host></host>
      <port>8080</port>
      <nonProxyHosts>127.0.0.1|localhost|*.<corp-domain>|*.<corp-cloud-domain></nonProxyHosts>
    </proxy>
  </proxies>
</settings>
```

**Eclipse must be restarted** for m2e to re-read `settings.xml`.

If prior failed Maven attempts left stale `*.lastUpdated` markers in
the local repo, purge them so retry actually fires:

```powershell
Get-ChildItem "$env:USERPROFILE\.m2\repository" -Recurse -Filter '*.lastUpdated' |
    Remove-Item -Force
```

---

## 7. Activation Procedure (in Eclipse)

1. Open the modified `.target` file in the Target Definition editor.
2. Click **Reload Target Platform** (top-right toolbar).
3. Wait for *Resolving Target Definition* — the Maven location should
   report `(2 plug-ins available)` (the jar + its source bundle).
4. Click **Set as Active Target Platform** if not already active.
5. Project → Clean… → All projects.
6. Re-check the Problems view: both `org.apache.commons.commons-io`
   errors should be gone.

---

## 8. Verification Checklist

| Check | Command / action | Expected |
|---|---|---|
| Proxy reachable | `Test-NetConnection <corp-proxy-host> -Port <corp-proxy-port> -InformationLevel Quiet` | `True` |
| Maven Central reachable through proxy | `Invoke-WebRequest -Proxy 'http://<corp-proxy-host>:<corp-proxy-port>' -Uri 'https://repo.maven.apache.org/maven2/commons-io/commons-io/maven-metadata.xml' -UseBasicParsing` | `StatusCode 200` |
| Settings file in correct home | `Get-Item "$env:USERPROFILE\.m2\settings.xml"` | non-empty file |
| Target resolves | Target editor toolbar | "Resolved" + "(2 plug-ins available)" on the Maven location |
| Manifests resolve | Problems view | Zero `cannot be resolved` errors for commons-io |

---

## 9. Adapting to Other Bundles

The exact same recipe handles every Orbit symbolic-name rename. Just
replace the GAV and the `Bundle-SymbolicName` override:

| Failing manifest demand | Maven GAV | bnd `Bundle-SymbolicName` override |
|---|---|---|
| `org.apache.commons.commons-io` | `commons-io:commons-io:<latest>` | `org.apache.commons.commons-io;singleton:=true` |
| `org.apache.commons.commons-collections4` | `org.apache.commons:commons-collections4:<latest>` | `org.apache.commons.commons-collections4;singleton:=true` |
| `com.google.guava.guava` | `com.google.guava:guava:<latest>` | `com.google.guava.guava;singleton:=true` |
| `org.slf4j.slf4j-api` | `org.slf4j:slf4j-api:<latest>` | `org.slf4j.slf4j-api;singleton:=true` |
| `org.apache.commons.commons-lang3` | `org.apache.commons:commons-lang3:<latest>` | `org.apache.commons.commons-lang3;singleton:=true` |

The `Import-Package: *;resolution:=optional` and
`Export-Package: *;…;-noimport:=true` directives are universally safe
boilerplate.

---

## 10. Long-Term Resolution

This fix is a **bridge**. The structural fix is one of:

1. **an internally-hosted Orbit mirror upgrade** — once the corporate Orbit
   ships `org.apache.commons.commons-io`, the Maven location can be
   removed from the `.target`.
2. **Manifest realignment** — once CI's target platform also ships the
   new name on every supported branch, `MANIFEST.MF` files can be
   normalised in one direction (a pure infra commit, never bundled
   with feature work).

Until then, the Maven location is the safe, portable, CI-neutral
bridge.
