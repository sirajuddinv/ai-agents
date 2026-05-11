---
name: Java Classpath Telemetry Integration
description: Passive context bridge for adding fire-and-forget HTTP telemetry to a plain Java CLI application packaged as a Jar-in-Jar runnable JAR.
category: Build & Dependency Management
---

# Java Classpath Telemetry Integration (Ref)

This bridge provides passive context for the
`java-classpath-telemetry-integration` skill, which integrates a
non-critical telemetry / tool-usage-logging library into a **plain Java
CLI application** (not an OSGi/PDE plugin). The skill covers:

- JAR-on-classpath delivery via `libs/` wired into both Eclipse
  `.classpath` and the build script (Ant Jar-in-Jar Loader, Maven
  Shade, Gradle Shadow).
- Bundling vendor JARs into the runnable JAR's `Rsrc-Class-Path` (or
  equivalent).
- Classpath `<vendor>.properties` + JVM system property + OS
  environment variable resolution chain.
- Single-source-of-truth `version.properties` read by both build and
  runtime.
- `rsrc:` → `user.dir` resource-path fallback for Jar-in-Jar runs.
- log4j-based lifecycle logging (no `System.out` swap to defend
  against, no flushed-timestamp helpers required).
- `*.spool`-style store-and-forward retry that drains on the next
  process invocation.
- Defensive `main(...)` integration with `finally`-block `sendLog()`.

It should be invoked whenever:

- A telemetry / tool-usage-logging library must be added to a plain
  Java CLI tool packaged as a runnable JAR.
- An existing classpath-JAR telemetry integration needs documenting
  or auditing.
- A new tool needs the SSOT `version.properties` + classpath
  `<vendor>.properties` + `rsrc:` fallback combo.

If the host is an Eclipse RCP / Equinox / PDE / Tycho application
instead, use the sibling base
[`eclipse-pde-telemetry-resilience`](../eclipse-pde-telemetry-resilience/SKILL.md).

This is a **base** skill. Vendor-specific composers supply the
payload model, server URL, and tool identity. None are registered in
this public repository — organization-specific composers live in the
organization's own private skills repository.

- **Primary Entry Point**: [.agents/skills/java-classpath-telemetry-integration/SKILL.md](./SKILL.md)
- **Sibling base (PDE/OSGi)**: [`eclipse-pde-telemetry-resilience`](../eclipse-pde-telemetry-resilience/SKILL.md)
