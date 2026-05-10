---
name: eclipse-pde-jdk-migration
description: Eclipse PDE/Tycho workspace migration across JDK major versions — surveys JRE pins in `.classpath`/`MANIFEST.MF`/`*.launch`/`pom.xml`, drops obsolete PermGen flags, and injects JDK 9+ `--add-opens` flags to unblock JAXB/EMF/Sphinx reflection.
category: Build & Dependency Management
---

# Eclipse PDE JDK Migration Skill

> **Skill ID:** `eclipse-pde-jdk-migration`
> **Version:** 1.0.0
> **Standard:** [Agent Skills (agentskills.io)](https://agentskills.io)

## Description

Migrate an Eclipse PDE/Tycho/OSGi workspace across a JDK major version
boundary (e.g., 8 → 11, 11 → 17, 17 → 21) without rewriting the source
code's Java language compliance.

The skill formalises the four-surface model that every PDE workspace
exposes — and that beginners conflate:

| Surface | What it controls | Migration verb |
|---|---|---|
| `.settings/org.eclipse.jdt.core.prefs` `compliance/source/target` | The Java language level the JDT compiler accepts | **KEEP** unless source bump is requested |
| `MANIFEST.MF` `Bundle-RequiredExecutionEnvironment` | The minimum JRE the OSGi runtime advertises | **KEEP**; a higher JDK satisfies a lower EE |
| `.classpath` `JRE_CONTAINER` (pinned vs. unpinned) | The JDK Eclipse uses to compile/run **this plug-in** | **UNPIN** so workspace default applies |
| `*.launch` `JRE_CONTAINER` + `VM_ARGUMENTS` | The JDK and JVM args used at run/debug time | **REPOINT** to new EE; **scrub** dead JVM args; **inject** `--add-opens` |

This separation is the SSOT — most failed migrations break because they
bump compliance unnecessarily, or pin the classpath to the new EE
(coupling future maintenance to a specific JDK), or forget JDK 9+
strong-encapsulation flags and only discover the JAXB / EMF / Sphinx /
Xtend `InaccessibleObjectException` at runtime.

## Prerequisites

| Requirement | Minimum |
|---|---|
| Eclipse | 4.20+ (any version that supports the target JDK as a JRE) |
| Tycho | 2.7+ for JDK 17, 4.0+ for JDK 21 |
| Target JDK | Installed and discoverable (path known) |
| PowerShell | 5.1+ on Windows or 7+ cross-platform |
| VCS | Git (skill assumes commits will be arranged via [`git-atomic-commit-construction`](../git-atomic-commit-construction/SKILL.md)) |

## Environment & Dependencies

Before running, the agent MUST:

1. Confirm the **target JDK is installed** and capture its path:

    ```powershell
    & '<jdk-install>\bin\java.exe' -version
    ```

2. Confirm Eclipse can register a new JRE (Window → Preferences → Java →
   Installed JREs is reachable on the user's IDE).
3. Confirm `git status` is clean in the workspace repo so migration
   edits can be staged atomically.
4. Bootstrap the shared PowerShell utilities submodule (recursive form
   per [Recursive Submodule Mandate](../../../ai-agent-rules/ai-rule-standardization-rules.md)):

    ```powershell
    git submodule update --init --recursive ai-agent-rules/powershell-scripts
    ```

## When to Apply

Apply this skill when:

- An Eclipse PDE / Tycho workspace must move to a new JDK major version
- The user reports `Unrecognized VM option 'MaxPermSize'` or
  `Unrecognized VM option 'PermSize'` after a JDK bump
- The user reports `java.lang.reflect.InaccessibleObjectException` or
  `module java.base does not "opens X" to unnamed module` from JAXB,
  EMF, Sphinx, Xpand, Xtend, or BeanShell after a JDK bump
- Launch configurations point to JDK installations that no longer exist
  on disk (`1.8.0_92_64`, `11.0.16.1`, etc.)
- A workspace boots on the IDE's bundled JDK but plug-ins fail to compile
  because their `.classpath` is pinned to a removed JRE

Do NOT apply when:

- The build system is plain Maven, Gradle, or sbt without Tycho/PDE
  (no `MANIFEST.MF` / `.classpath` / `.launch` surface to manage)
- The user explicitly asks for a **language-level** bump (Java 8 → 17
  source) — that requires source-code remediation (`var`, sealed types,
  removed `sun.*` API) which is out of scope here
- The JDK change is a minor/patch bump within the same major version
  (no surface change required)

---

## Phase 1 — Reference Survey (Read-Only)

Discover every place the workspace pins a JDK.

### Step 1.1 — Run the bundled survey script

```powershell
pwsh-preview -File .agents/skills/eclipse-pde-jdk-migration/scripts/Survey-JrePins.ps1 `
    -WorkspaceRoot '<workspace-root>'
```

Falls back to `pwsh` if `pwsh-preview` is unavailable. The script
produces a categorised report of:

- `.classpath` files where `JRE_CONTAINER` is pinned to a specific EE
  (`JavaSE-1.8`, `JavaSE-11`) versus unpinned (workspace default)
- `MANIFEST.MF` files and their `Bundle-RequiredExecutionEnvironment`
  value
- `*.launch` files with hard-coded VM ids (`1.8.0_92_64`,
  `11.0.16.1`, etc.) versus EE-based references (`JavaSE-17`)
- `pom.xml` files containing PermGen flags (`-XX:PermSize`,
  `-XX:MaxPermSize`) or an `<executionEnvironment>` property

The script is **read-only** — it never mutates files. It exits 0 on
success regardless of findings (a survey of zero issues is still a
successful survey).

### Step 1.2 — Manual cross-check (if script unavailable)

The four canonical regex queries the script encapsulates:

```powershell
# .classpath — pinned vs. unpinned JRE_CONTAINER
Select-String -Path '**\.classpath' -Pattern 'JRE_CONTAINER' -AllMatches

# MANIFEST.MF — Bundle-RequiredExecutionEnvironment
Select-String -Path '**\META-INF\MANIFEST.MF' -Pattern 'Bundle-RequiredExecutionEnvironment'

# *.launch — JRE_CONTAINER (EE or pinned VM id)
Select-String -Path '**\*.launch' -Pattern 'JRE_CONTAINER'

# pom.xml — PermGen flags
Select-String -Path '**\pom.xml' -Pattern 'PermSize'
```

---

## Phase 2 — Migration Decision Matrix

Apply the SSOT table below per surface. **Do NOT bump compliance unless
the user explicitly requested a source-language migration.**

| Finding | Default action | Rationale |
|---|---|---|
| `.classpath` JRE_CONTAINER pinned to old EE (e.g., `JavaSE-1.8`) | **Unpin** to plain `JRE_CONTAINER` | Lets workspace-default JRE apply; consistent with unpinned siblings |
| `.classpath` JRE_CONTAINER unpinned | **Leave** | Already correct; will pick up new workspace default JDK |
| `MANIFEST.MF` `Bundle-RequiredExecutionEnvironment: JavaSE-1.8` | **Leave** | A higher JDK satisfies a lower EE; bumping forces all consumers to upgrade |
| `org.eclipse.jdt.core.prefs` `compliance/source/target = 1.8` | **Leave** | JDK 17 compiles `-source 1.8` cleanly; bumping is a language migration |
| `*.launch` JRE_CONTAINER pinned to specific VM id | **Repoint** to `JavaSE-<NEW>` EE | EE pin survives JRE renames; specific id pins break when JREs are uninstalled |
| `*.launch` `VM_ARGUMENTS` containing `-XX:MaxPermSize` / `-XX:PermSize` | **Strip** | PermGen removed in Java 8u; JDK 9+ aborts on `-XX:MaxPermSize` |
| `*.launch` `VM_ARGUMENTS` lacking `--add-opens` (target JDK ≥ 9) | **Inject** standard set | Required for JAXB/EMF/Sphinx/Xtend reflection (see Phase 4) |
| `pom.xml` `<argLine>` with PermGen | **Strip** | Same reason as `.launch` |
| Tycho `<executionEnvironment>` property | **Defer** to releng parent | This skill does not edit CI/CD-managed parent POMs |

---

## Phase 3 — Surgical Edits

The agent applies the matrix surface-by-surface. **Never bulk-replace VM
arguments** — every launch may carry user-customised properties (heap
size, system properties, JFR flags) that must be preserved.

### 3.1 Unpin classpath JRE containers

For each pinned `.classpath`:

```diff
- <classpathentry kind="con" path="org.eclipse.jdt.launching.JRE_CONTAINER/org.eclipse.jdt.internal.debug.ui.launcher.StandardVMType/JavaSE-1.8"/>
+ <classpathentry kind="con" path="org.eclipse.jdt.launching.JRE_CONTAINER"/>
```

### 3.2 Drop PermGen from launches and Tycho POMs

```diff
- value="-Xms512m -Xmx3G -XX:MaxPermSize=512m -Xss1024k …"
+ value="-Xms512m -Xmx3G -Xss1024k …"
```

```diff
- <argLine>${tycho.testArgLine} -Xms512m -Xmx2048m -XX:PermSize=256m -XX:MaxPermSize=512m</argLine>
+ <argLine>${tycho.testArgLine} -Xms512m -Xmx2048m</argLine>
```

### 3.3 Re-EE launches

```diff
- <stringAttribute key="org.eclipse.jdt.launching.JRE_CONTAINER" value="org.eclipse.jdt.launching.JRE_CONTAINER/org.eclipse.jdt.internal.debug.ui.launcher.StandardVMType/11.0.16.1"/>
+ <stringAttribute key="org.eclipse.jdt.launching.JRE_CONTAINER" value="org.eclipse.jdt.launching.JRE_CONTAINER/org.eclipse.jdt.internal.debug.ui.launcher.StandardVMType/JavaSE-17"/>
```

### 3.4 Inject `--add-opens` (target JDK ≥ 9)

Prepend the standard set to every launch's `VM_ARGUMENTS`:

```text
--add-opens=java.base/java.lang=ALL-UNNAMED
--add-opens=java.base/java.lang.reflect=ALL-UNNAMED
--add-opens=java.base/java.io=ALL-UNNAMED
--add-opens=java.base/java.util=ALL-UNNAMED
--add-opens=java.base/java.net=ALL-UNNAMED
```

**Coupling note**: §3.2, §3.3, and §3.4 all touch the same launch file.
Per the buildable-state priority of
[`git-atomic-commit-construction`](../git-atomic-commit-construction/SKILL.md),
all three edits per launch MUST be coalesced into one commit per launch
group — splitting them leaves intermediate launches broken in two of
three states.

---

## Phase 4 — JDK 9+ Reflection Unblock Reference

When a launch crashes with
`module java.base does not "opens X" to unnamed module`, locate the
package in the table and append the matching `--add-opens` to that
launch's `VM_ARGUMENTS`.

| Symptom in stack trace | Required flag |
|---|---|
| `JAXBContext.newInstance` → `Injector.<clinit>` → `ClassLoader.defineClass` | `--add-opens=java.base/java.lang=ALL-UNNAMED` |
| EMF/Sphinx reflection on private fields | `--add-opens=java.base/java.lang.reflect=ALL-UNNAMED` |
| Eclipse log/file IO reflection | `--add-opens=java.base/java.io=ALL-UNNAMED` |
| Guava / collections reflection | `--add-opens=java.base/java.util=ALL-UNNAMED` |
| URL handler reflection | `--add-opens=java.base/java.net=ALL-UNNAMED` |
| `cannot access class sun.nio.ch.DirectBuffer` | `--add-opens=java.base/sun.nio.ch=ALL-UNNAMED` |
| `does not "opens java.nio"` | `--add-opens=java.base/java.nio=ALL-UNNAMED` |
| `does not "opens java.text"` (DateFormat) | `--add-opens=java.base/java.text=ALL-UNNAMED` |
| `does not "opens java.util.regex"` | `--add-opens=java.base/java.util.regex=ALL-UNNAMED` |
| Xtend / Xtext on-the-fly compile via `com.sun.tools.javac` | `--add-opens=jdk.compiler/com.sun.tools.javac.api=ALL-UNNAMED` (also `.code`, `.tree`, `.util`, `.processing`, `.model`, `.parser`, `.comp`, `.main`, `.file`) |
| `does not "opens sun.security.x509"` | `--add-opens=java.base/sun.security.x509=ALL-UNNAMED` |
| `IllegalAccessError` on `jdk.internal.misc` | `--add-exports=java.base/jdk.internal.misc=ALL-UNNAMED` |

---

## Phase 5 — Verification

1. **Eclipse Installed JREs**: Window → Preferences → Java → Installed
   JREs → Add Standard VM → point to `<jdk-install>` → tick as default.
2. **Execution Environments**: Java → Installed JREs → Execution
   Environments → tick the new JDK against `JavaSE-<NEW>` AND against
   the `MANIFEST.MF`-declared `JavaSE-1.8` (so the EE pin still
   resolves).
3. **Project → Clean… → All projects**.
4. **Spot-check** any plug-in: Build Path → Libraries → JRE System
   Library should now read `[<new-jdk-name>]`.
5. **Run** the most representative `*.launch` configuration. Watch for:
    - `Unrecognized VM option` — Phase 3.2 missed a flag
    - `InaccessibleObjectException` — Phase 4 needs another `--add-opens`
    - Successful boot — log header should print `java.version=<NEW>`
6. **Tycho command-line build** (if applicable):

    ```powershell
    $env:JAVA_HOME = '<jdk-install>'
    $env:PATH = "$env:JAVA_HOME\bin;$env:PATH"
    mvn -v   # confirm
    mvn clean verify
    ```

---

## Phase 6 — Atomic Commit Arrangement

Defer commit construction to
[`git-atomic-commit-construction`](../git-atomic-commit-construction/SKILL.md).
The canonical three-commit split for a typical migration is:

| # | Type / scope / subject | Files | Rationale |
|---|---|---|---|
| 1 | `chore(jdt): unpin classpath JRE container from JavaSE-<OLD>` | every modified `.classpath` | Pure unpin; independently buildable |
| 2 | `build(tycho): drop obsolete PermGen JVM options for JDK <NEW>` | every modified Tycho `pom.xml` | CLI-build cleanup; independent |
| 3 | `chore(launch): migrate Eclipse launches to JDK <NEW> runtime` | every modified `*.launch` | Coupled three-way edit per launch (§3.2 + §3.3 + §3.4); coalesced per buildable-state priority |

`MANIFEST.MF` and `org.eclipse.jdt.core.prefs` MUST remain untouched
unless the user explicitly approves a language-level bump.

---

## Composition by Higher-Level Skills

*(none yet — this is a leaf skill; future composers may chain it with
target-platform refresh or product-config audits)*

---

## Prohibited Behaviors

- **DO NOT** bump `compliance/source/target` in
  `org.eclipse.jdt.core.prefs` unless the user explicitly requests a
  Java language-level migration. JDK 17 compiles `-source 1.8` cleanly.
- **DO NOT** edit `MANIFEST.MF` `Bundle-RequiredExecutionEnvironment`
  blindly. Every consumer of the bundle must support the new EE.
- **DO NOT** blanket-replace `VM_ARGUMENTS` strings. Read each launch
  individually; preserve user-added system properties, heap settings,
  JFR flags, and module-path entries.
- **DO NOT** edit Tycho releng parent POMs from this skill. Parent
  `<executionEnvironment>` lives outside the workspace and is
  CI/CD-managed.
- **DO NOT** add `--add-opens` for packages the workspace does not
  actually exercise. Bloat hides which flags are load-bearing.
- **DO NOT** auto-commit. Commit arrangement is delegated to
  [`git-atomic-commit-construction`](../git-atomic-commit-construction/SKILL.md)
  per the Sequential Objective Protocol.

---

## Related Skills

- [`git-atomic-commit-construction`](../git-atomic-commit-construction/SKILL.md) — three-commit split for the migration
- [`maven-pom-audit`](../maven-pom-audit/SKILL.md) — broader Maven POM auditing if Tycho parents come into scope
- [`system-wide-tool-management`](../system-wide-tool-management/SKILL.md) — installing the target JDK system-wide

---

## Related Conversations & Traceability

- [`docs/conversations/2026-05-10-jdk11-to-jdk17-migration.md`](docs/conversations/2026-05-10-jdk11-to-jdk17-migration.md)
  — full session log of the JDK 11 → 17 migration that birthed this
  skill, including the JAXB `Injector` stack trace that motivated the
  Phase 4 reference table.
