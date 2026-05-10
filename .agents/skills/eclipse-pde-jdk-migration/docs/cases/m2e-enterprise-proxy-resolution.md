# Case Study — m2e Enterprise Proxy Resolution

> **Triggers Phase**: [SKILL.md §6.5 — m2e Proxy Gotcha](../SKILL.md#65-m2e-proxy-gotcha-corporate-environments) + [§6.6 — Stale `.lastUpdated` Markers](../SKILL.md#66-stale-lastupdated-failure-markers)
>
> **Date observed**: 2026-05-10 on a corporate-network developer machine

This case study captures the exact sequence by which **m2e (Maven for
Eclipse) silently fails to use the corporate HTTP proxy** even when
the OS, browsers, and command-line tools all use it correctly — and
the per-user fix that resolves it permanently.

---

## 1. Symptom

In the Eclipse Target Definition editor, after adding a Maven
`<location>` (per [Phase 6](../SKILL.md#phase-6--target-platform-symbolic-name-aliasing-ide-only)):

```text
commons-io:commons-io (2.22.0) 0 plug-ins available
    Could not transfer artifact commons-io:commons-io:jar:2.22.0
    from/to central (https://repo.maven.apache.org/maven2):
    No such host is known (repo.maven.apache.org)
```

Same root cause shows up in many other m2e contexts:

- Importing a Maven project with non-cached dependencies
- Right-click → Maven → Update Project (downloads any missing artifact)
- Tycho-driven `mvn` runs invoked from inside Eclipse via Run As → Maven Build
- m2e quick-fix "Discover m2e connector" downloads

---

## 2. Confirming the Network Reality

Before diagnosing m2e, prove the OS itself can reach Maven Central
**through** the proxy and **cannot** reach it directly:

```powershell
# Direct lookup — expected to fail in corporate networks
Test-NetConnection repo.maven.apache.org -Port 443
# WARNING: Name resolution of repo.maven.apache.org failed

# Proxy reachability — expected to succeed
Test-NetConnection <corp-proxy-host> -Port <corp-proxy-port> -InformationLevel Quiet
# True

# End-to-end fetch via proxy — expected HTTP 200
Invoke-WebRequest `
    -Proxy 'http://<corp-proxy-host>:<corp-proxy-port>' `
    -Uri 'https://repo.maven.apache.org/maven2/commons-io/commons-io/maven-metadata.xml' `
    -UseBasicParsing -TimeoutSec 15 |
    Select-Object StatusCode, @{n='Bytes';e={$_.Content.Length}}
# StatusCode Bytes
# ---------- -----
#        200  ~1300
```

Then confirm the OS-level proxy *is* configured in env vars:

```powershell
@('HTTP_PROXY','HTTPS_PROXY','http_proxy','https_proxy','NO_PROXY','no_proxy') |
    ForEach-Object { "$_ = $([Environment]::GetEnvironmentVariable($_))" }
# …
# HTTP_PROXY  = http://<corp-proxy-host>:<corp-proxy-port>
# HTTPS_PROXY = http://<corp-proxy-host>:<corp-proxy-port>
```

---

## 3. Root Cause

**m2e does not read OS environment variables for proxy configuration.**
This is by design and contrary to common expectation. Maven (the engine
m2e wraps) consults its own configuration hierarchy *only*:

| Source | Read by Maven? |
|---|---|
| `~/.m2/settings.xml` `<proxies>` section | ✅ Yes — primary source |
| `${maven.home}/conf/settings.xml` | ✅ Yes — system fallback |
| `-Dhttp.proxyHost=… -Dhttp.proxyPort=…` JVM properties | ✅ Yes — only if explicitly added to `eclipse.ini` / `mvn` opts |
| OS env `HTTP_PROXY` / `HTTPS_PROXY` | ❌ **No** |
| Windows IE / system proxy settings (WinINET) | ❌ No |
| Eclipse → Preferences → Network Connections | ⚠️ Used by Eclipse's own HTTP client (e.g., p2 update sites) but **not** by m2e |

So a developer can have:

- `curl` working through proxy (uses env vars)
- `git clone` working through proxy (configured separately in `~/.gitconfig` or env)
- p2 update sites working in Eclipse (uses Eclipse Network Connections)
- Browser working through proxy (uses WinINET / system settings)

…and m2e *still* fails with `No such host is known` because none of
the above feed Maven.

---

## 4. Why the Eclipse Network Preferences Don't Help

A common — and incorrect — first attempt is:

> Window → Preferences → General → Network Connections → Active Provider:
> Native (or Manual) → set proxy host/port

This **does** fix Eclipse's built-in HTTP client (used by the p2
mechanism that downloads features and updates), but **m2e bypasses
Eclipse's HTTP layer entirely** and uses Aether (Maven's own resolver).
Aether reads `~/.m2/settings.xml` and nothing else.

Verify by inspecting Eclipse's preferences while m2e still fails: the
Network Connections setting will be correct, yet target reload still
errors with the same DNS message.

---

## 5. The Fix — `~/.m2/settings.xml`

Create the file at the user's actual home (NOT a guessed path — verify
with `$env:USERPROFILE` first):

```powershell
# Always confirm before creating
$env:USERPROFILE
# <USERPROFILE>

New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.m2" | Out-Null
```

Then the file:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<settings xmlns="http://maven.apache.org/SETTINGS/1.0.0"
          xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
          xsi:schemaLocation="http://maven.apache.org/SETTINGS/1.0.0
                              https://maven.apache.org/xsd/settings-1.0.0.xsd">

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

### Anatomy

| Element | Why it's here |
|---|---|
| Two `<proxy>` entries (one per protocol) | Maven matches by `<protocol>` exactly; an HTTP-only proxy entry will not be applied to an `https://` URL even if the host:port is the same |
| `<active>true</active>` | Both proxies must be explicitly activated; default is `false` |
| `<nonProxyHosts>` with `\|` separator | Pipe-separated, glob-style. Bypasses internal corporate hosts (Artifactory mirrors, internal Nexus) so they are reached directly, not via the external proxy |
| File path = `~/.m2/settings.xml` (per-user, never committed) | Each developer has their own machine-specific proxy; never goes into VCS |

---

## 6. Activation — Eclipse Restart Required

**m2e reads `settings.xml` once at startup.** Modifying the file
while Eclipse is running has zero effect until restart. Sequence:

1. Save `~/.m2/settings.xml`.
2. **File → Restart** (or fully exit and relaunch).
3. After restart: open the failing `.target` → **Reload Target Platform**.
4. Watch the resolution status bar — it should fetch through the proxy
   and report a positive plug-in count.

A common failure pattern is: developer creates `settings.xml`, clicks
Reload immediately, sees the same error, concludes the fix didn't
work, and rolls back. **Always restart Eclipse after creating or
editing `settings.xml`.**

---

## 7. Stale `.lastUpdated` Failure Markers

Maven caches *failures* as well as successes. If m2e attempted a
download before `settings.xml` existed, the local repo will contain:

```text
~/.m2/repository/<group-path>/<artifact>/<version>/
    commons-io-2.22.0.jar.lastUpdated
    commons-io-2.22.0-sources.jar.lastUpdated
    m2e-lastUpdated.properties
```

By default, Maven will not retry a failed download for **24 hours**.
After fixing the proxy, retries are silently suppressed until those
markers age out — making it look like the proxy fix didn't work.

Purge them workspace-wide:

```powershell
Get-ChildItem "$env:USERPROFILE\.m2\repository" -Recurse -Filter '*.lastUpdated' |
    Remove-Item -Force
Get-ChildItem "$env:USERPROFILE\.m2\repository" -Recurse -Filter 'm2e-lastUpdated.properties' |
    Remove-Item -Force
```

For a targeted purge of a single artifact:

```powershell
$dir = "$env:USERPROFILE\.m2\repository\commons-io\commons-io\2.22.0"
if (Test-Path $dir) { Get-ChildItem $dir -Filter '*.lastUpdated' | Remove-Item -Force }
```

After purging, *Reload Target Platform* will actually attempt the
download again.

---

## 8. Verification Sequence (End-to-End)

| # | Check | Command / action | Expected |
|---|---|---|---|
| 1 | Direct DNS fails | `Test-NetConnection repo.maven.apache.org -Port 443` | `WARNING: Name resolution … failed` |
| 2 | Proxy host reachable | `Test-NetConnection <corp-proxy-host> -Port <corp-proxy-port> -InformationLevel Quiet` | `True` |
| 3 | Maven Central reachable through proxy | `Invoke-WebRequest -Proxy 'http://<corp-proxy-host>:<corp-proxy-port>' -Uri 'https://repo.maven.apache.org/maven2/commons-io/commons-io/maven-metadata.xml' -UseBasicParsing` | `StatusCode 200` |
| 4 | `settings.xml` at correct home | `Get-Item "$env:USERPROFILE\.m2\settings.xml"` | non-empty file |
| 5 | Stale failure markers purged | `Get-ChildItem "$env:USERPROFILE\.m2\repository" -Recurse -Filter '*.lastUpdated'` | no output |
| 6 | Eclipse restarted after step 4 | manual | confirmed |
| 7 | Target reload succeeds | Target editor → Reload Target Platform | "(N plug-ins available)" on Maven location |

If steps 1–5 pass but step 7 still fails: forget step 6. Restart Eclipse.

---

## 9. Authentication-Required Proxies

If the corporate proxy requires credentials (it doesn't at the example organization for
the standard `<corp-proxy-host>:<corp-proxy-port>`, but does at some sites),
add `<username>` and `<password>` to each `<proxy>` block:

```xml
<proxy>
  <id>corp-https</id>
  <active>true</active>
  <protocol>https</protocol>
  <host>proxy.example.com</host>
  <port>8080</port>
  <username>DOMAIN\user</username>
  <password>{encrypted-or-plain-password}</password>
  <nonProxyHosts>…</nonProxyHosts>
</proxy>
```

For password security, use Maven's master-password encryption
(`mvn --encrypt-password`) and store the encrypted form. Plain
passwords work but are visible to anyone with file-system access to
the user home. Never commit any form of the password.

---

## 10. Common Adjacent Symptoms (Same Root Cause)

If `settings.xml` is missing, broken, or not yet active, these
*other* errors will be observed across Eclipse / Maven workflows.
All resolve by the same `settings.xml` + restart fix:

| Workflow | Error message |
|---|---|
| Maven CLI inside Eclipse Run Configuration | `Could not transfer artifact …` |
| m2e project import on a fresh workspace | `Project build error: Non-resolvable parent POM` |
| Tycho run from Eclipse (not CI) | `Cannot resolve target definition` |
| m2e Lifecycle Mapping connector discovery | `Could not download <connector>.zip` |
| Bnd PDE Maven `<location>` (this skill's Phase 6) | `0 plug-ins available — No such host is known` |

---

## 11. Portability & Onboarding

This fix is **per-user** and **per-machine**. It is intentionally not
committed to the repository:

- Different developers have different proxy hosts (corporate vs.
  home network vs. VPN vs. cloud build agent)
- Some machines have no proxy at all (CI, cloud workspaces)
- Credential-bearing proxy entries must never enter VCS

The portable, repo-wide fix (the bnd `<instructions>` Maven location
in Phase 6) **assumes** that every developer's m2e can reach Maven
Central one way or another. This case study documents the per-user
work each developer does once on their own machine to satisfy that
assumption.

A reasonable onboarding artifact is a paragraph in the workspace
`README.md` saying:

> If you are on a corporate network with a proxy and Eclipse cannot
> resolve Maven dependencies, see
> `.agents/skills/eclipse-pde-jdk-migration/docs/cases/m2e-enterprise-proxy-resolution.md`.

…rather than pre-creating `settings.xml` for everyone.

---

## 12. Long-Term Resolution

This case study describes a workaround for a layering inconsistency in
Eclipse's HTTP-client zoo (Eclipse Network Connections vs. Aether vs.
JVM proxy properties). It is unlikely to be fixed upstream because:

- m2e intentionally delegates all networking to Maven proper to
  preserve identical behaviour between IDE builds and CLI builds
- Maven has historically rejected reading OS env vars for proxy
  configuration to maintain reproducibility across platforms
- The standard Maven answer has always been `~/.m2/settings.xml`

The right structural fix at an organisational level is to **provision
`~/.m2/settings.xml` automatically** as part of the developer-machine
setup (e.g., via the corporate workstation imaging script or the
toolbase install kit). Until that exists, this case study is the
manual procedure.
