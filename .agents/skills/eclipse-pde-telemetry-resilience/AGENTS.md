---
name: Eclipse PDE Telemetry Resilience
description: Passive context bridge for adding fire-and-forget HTTP telemetry to an Eclipse PDE/Tycho plugin without coupling tool exit code to telemetry availability.
category: Build & Dependency Management
---

# Eclipse PDE Telemetry Resilience (Ref)

This bridge provides passive context for the
`eclipse-pde-telemetry-resilience` skill, which integrates a
non-critical telemetry / tool-usage-logging library into an Eclipse
PDE / Tycho headless application such that:

- The library compiles under PDE (which cannot reuse traditional Maven
  JARs the way a plain Java app can).
- A slow, hung, or unreachable telemetry server never stalls the tool,
  blocks JVM shutdown, or alters the tool's exit code.
- Every lifecycle event is observable in the console even when the
  host application later replaces `System.out` with its own logging
  appender.

It should be invoked whenever:

- A telemetry / tool-usage-logging library must be added to an
  Eclipse PDE / Tycho plugin.
- An existing telemetry integration causes the tool to hang when its
  server is down.
- A telemetry integration's `[telemetry]`-style log lines disappear after
  the host's logging framework starts up.
- A consuming PDE plugin still ships JARs in a `libs/` folder under
  `Bundle-ClassPath` and needs to migrate to a vendored-source +
  target-platform model.
- Native-binding libraries (JNA, JNR-FFI, JNI bridges) must be added
  to a PDE workspace.

This is a **base** skill. Vendor-specific composers supply the
payload model, server URL, and tool identity. None are registered in
this public repository — organization-specific composers live in the
organization's own private skills repository.

- **Primary Entry Point**: [.agents/skills/eclipse-pde-telemetry-resilience/SKILL.md](./SKILL.md)
