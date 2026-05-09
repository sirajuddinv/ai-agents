---
name: Lower Case Hyphen Naming Convention
description: Passive context bridge for enforcing lowercase kebab-case naming with industry-standard exemptions.
category: Naming & Conventions
---

# Lower Case Hyphen Naming Convention (Ref)

This bridge provides passive context for the `lower-case-hyphen-naming` skill, which enforces lowercase kebab-case
(hyphen-based) naming for all project files, directories, and identifiers — with documented industry-standard
exemptions (e.g., `README.md`, `Dockerfile`, language-mandated names).

It should be invoked whenever the user asks to enforce hyphen naming, or when files/dirs with spaces or
underscores are detected and need normalization.

- **Primary Entry Point**: [.agents/skills/lower-case-hyphen-naming/SKILL.md](./SKILL.md)
- **Sibling Convention**: [`lower-case-underscore-naming`](../lower-case-underscore-naming/SKILL.md) — snake_case
  enforcement for projects choosing the underscore convention.
