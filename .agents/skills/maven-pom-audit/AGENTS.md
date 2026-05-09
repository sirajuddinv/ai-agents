---
name: Maven POM Audit
description: Passive context bridge for section-by-section audit of Maven pom.xml files.
category: Build & Dependency Management
---

# Maven POM Audit (Ref)

This bridge provides passive context for the `maven-pom-audit` skill, which performs a section-by-section audit of
Maven `pom.xml` files — catching invalid URLs, wrong developer identities, missing metadata, and enforcing
placeholder conventions.

It should be invoked whenever the user asks to audit `pom.xml`, or whenever invalid URLs / wrong developer
identity blocks are detected in a Maven project.

- **Primary Entry Point**: [.agents/skills/maven-pom-audit/SKILL.md](./SKILL.md)
