# java-vendored-snapshot-compile-check — Companion Bridge

This directory is an **Agent Skill** following the agentskills.io protocol. The active SSOT is [SKILL.md](SKILL.md).

## Passive Context

Use this skill when you have a directory of patched Java source extracted from a host project you cannot build
(Eclipse PDE bundle, internal SDK, closed-source product) and need to prove the patch still type-checks against
the host's API contract. The protocol:

1. Enumerate external symbol surface (`Select-String -Pattern '^import '` + qualified-reference grep).
2. Classify imports into JDK / library-JAR / self / host-project buckets.
3. Write minimal compile-only stubs (no-op bodies, exact signatures, correct packages).
4. Compile stubs to `stubs-bin/`.
5. `javac` the snapshot against `stubs-bin/` + library JARs.
6. Confirm output `.class` files include any patch-introduced inner classes.

## What this skill does NOT do

- Verify runtime behaviour, OSGi bundle activation, or end-to-end integration.
- Replace a real host-workspace build — only proves the patch's type contract is consistent.
- Run tests or instrument coverage.

## Related Skills

- Composers built on top: none registered in this public repository.
  Organization-specific composers live in the organization's own private
  skills repository.
- Companion validation when a host workspace IS available:
    - [eclipse-pde-telemetry-resilience](../eclipse-pde-telemetry-resilience/SKILL.md) — Eclipse PDE/Tycho `IApplication`.
