# Session — JDK 11 → 17 migration of an Eclipse PDE / Tycho workspace

> **Date:** 2026-05-10
> **Skill birthed:** [`eclipse-pde-jdk-migration`](../../SKILL.md)

This log captures the migration narrative that motivated every section
of the skill. All paths, plug-in names, JDK install locations, and
organisation identifiers have been neutralised to placeholders per the
Redaction & Portability protocol.

---

## 1. Starting state

- Eclipse 4.36-based customised IDE running on the IDE's bundled JDK 21
- Multi-module PDE / Tycho workspace (≈ 47 plug-ins) targeting Java 1.8
  source/compliance
- Most plug-ins build under JDK 11; six are hard-locked to JDK 8 via
  pinned `.classpath` `JavaSE-1.8` execution environment
- Goal: run everything (compile + product launches + Tycho test
  executions) on JDK 17 without changing the source language level

## 2. The four-surface model (the SSOT insight)

The migration is not a single change — every PDE workspace exposes four
independent surfaces that conflate "which JDK". The skill formalises
the table; here is the field discovery that produced it:

| Surface | Discovered state | Decision |
|---|---|---|
| `org.eclipse.jdt.core.prefs` `compliance/source/target` | 1.8 (a few legacy 1.6/1.7) | KEEP |
| `MANIFEST.MF` `Bundle-RequiredExecutionEnvironment` | `JavaSE-1.8` (a few `JavaSE-1.6`/`1.7`) | KEEP — JDK 17 satisfies |
| `.classpath` `JRE_CONTAINER` | 41 unpinned, 6 pinned to `JavaSE-1.8` | UNPIN the 6 |
| `*.launch` `JRE_CONTAINER` | mix of `JavaSE-1.8`, `1.8.0_92_64`, `1.8.0_141_64`, `1.8.0_152_64`, `11.0.16.1` | repoint all to `JavaSE-17` |

## 3. Three runtime crashes encountered (one per phase)

### 3.1 `Unrecognized VM option 'MaxPermSize=512m'`

First product launch under JDK 17 aborted at JVM startup. Root cause:
PermGen was removed from HotSpot in Java 8u, but four product
launches and seven `<argLine>` entries across the two Tycho parents
still carried `-XX:MaxPermSize=512m -XX:PermSize=256m`. JDK 17 hard-fails
on `-XX:MaxPermSize` (warns and ignores `-XX:PermSize`). Solution:
strip both flags everywhere.

### 3.2 `java.lang.reflect.InaccessibleObjectException` from JAXB

Second launch attempt (one product) progressed past startup but crashed
inside the code-generator on a JAXB-driven artifact build. Stack trace
(redacted):

```text
Caused by: java.lang.ExceptionInInitializerError
    at com.sun.xml.bind.v2.runtime.reflect.opt.AccessorInjector.prepare
    ...
    at javax.xml.bind.JAXBContext.newInstance
    at <plugin>.dcg.engine.codegen.javaextensions.<XmlBuilder>.create<Doc>Xml
Caused by: java.lang.reflect.InaccessibleObjectException:
    Unable to make protected final java.lang.Class
    java.lang.ClassLoader.defineClass(...) accessible:
    module java.base does not "opens java.lang" to unnamed module
```

Cause: JAXB's `Injector` uses deep reflection on
`ClassLoader.defineClass` to inject optimised accessors. JPMS strong
encapsulation (default since JDK 16) blocks it. Solution: prepend the
standard `--add-opens` set to every launch's `VM_ARGUMENTS`. This list
became the Phase 4 reference table in the skill:

```text
--add-opens=java.base/java.lang=ALL-UNNAMED
--add-opens=java.base/java.lang.reflect=ALL-UNNAMED
--add-opens=java.base/java.io=ALL-UNNAMED
--add-opens=java.base/java.util=ALL-UNNAMED
--add-opens=java.base/java.net=ALL-UNNAMED
```

### 3.3 (None — the second product launch then ran end-to-end)

A successful run of a second product confirmed the `--add-opens` set
covered all reflection paths actually exercised. The skill keeps the
extended Phase 4 table for symptoms that did not appear here but are
documented in the Eclipse / Sphinx / EMF / Xtend ecosystem.

## 4. Atomic commit arrangement

The migration produced 21 modified files. Per
[`git-atomic-commit-construction`](../../../git-atomic-commit-construction/SKILL.md),
they were arranged into three independently-buildable commits:

1. `chore(jdt): unpin classpath JRE container from JavaSE-1.8` — 6 files
2. `build(tycho): drop obsolete PermGen JVM options for JDK 17` — 2 files
3. `chore(launch): migrate Eclipse launches to JDK 17 runtime` — 13 files

The third commit deliberately coalesces three logical edits per launch
(re-EE, drop PermGen, inject `--add-opens`) because splitting them
would leave every launch broken in two of three intermediate states —
the buildable-state priority overrides micro-atomicity.

## 5. What did NOT change (the "DO NOT" list)

- No bump of `compliance/source/target` (would force a language
  migration unrelated to the JDK runtime change)
- No edit of `MANIFEST.MF` `Bundle-RequiredExecutionEnvironment` (would
  force consumers to upgrade)
- No edit of the Tycho releng parent POM `<executionEnvironment>`
  property (lives outside the workspace; CI/CD-managed)
- No blanket VM-arg replacement (would clobber per-launch system
  properties, JFR flags, IPv4 stack pin, etc.)

## 6. Outputs

- Migration patch shipped on a dedicated migration branch
- `Survey-JrePins.ps1` script generalised from the four `grep`/`Select-String`
  patterns used during Phase 1
- This skill documents the protocol so the next major bump (17 → 21)
  reuses the same workflow without re-discovery cost
