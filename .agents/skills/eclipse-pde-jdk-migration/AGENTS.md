---
name: Eclipse PDE JDK Migration
description: Passive context bridge for Eclipse PDE/Tycho workspace migration across JDK major versions.
category: Build & Dependency Management
---

# Eclipse PDE JDK Migration (Ref)

This bridge provides passive context for the `eclipse-pde-jdk-migration`
skill, which migrates an Eclipse PDE / Tycho / OSGi workspace from one
JDK major version to another (e.g., 8 → 11, 11 → 17, 17 → 21) without
rewriting source-code language compliance.

It should be invoked whenever:

- An Eclipse PDE / Tycho workspace must move to a new JDK major version
- A launch configuration crashes with `Unrecognized VM option 'MaxPermSize'`
  or `'PermSize'` after a JDK bump
- A launch configuration crashes with `InaccessibleObjectException` or
  `module java.base does not "opens X" to unnamed module`
- A launch's `JRE_CONTAINER` references a JDK install that no longer exists
- `.classpath` files are pinned to an obsolete `JavaSE-<OLD>` execution
  environment

- **Primary Entry Point**: [.agents/skills/eclipse-pde-jdk-migration/SKILL.md](./SKILL.md)
