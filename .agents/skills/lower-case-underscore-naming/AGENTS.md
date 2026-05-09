---
name: Lower Case Underscore Naming Convention
description: Passive context bridge for enforcing lowercase snake_case naming with industry-standard exemptions.
category: Naming & Conventions
---

# Lower Case Underscore Naming Convention (Ref)

This bridge provides passive context for the `lower-case-underscore-naming` skill, which enforces lowercase
snake_case naming for all project files, directories, and identifiers — with documented industry-standard
exemptions.

It should be invoked whenever the user asks to enforce underscore naming, or when files/dirs with hyphens are
detected in a project that has chosen snake_case as its convention.

- **Primary Entry Point**: [.agents/skills/lower-case-underscore-naming/SKILL.md](./SKILL.md)
- **Sibling Convention**: [`lower-case-hyphen-naming`](../lower-case-hyphen-naming/SKILL.md) — kebab-case
  enforcement for projects choosing the hyphen convention.
