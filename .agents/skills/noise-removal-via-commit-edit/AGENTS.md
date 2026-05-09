---
name: Noise Removal via Commit Edit
description: Passive context bridge for purging IDE artifact noise from existing commits via interactive rebase.
category: Git & Repository Management
---

# Noise Removal via Commit Edit (Ref)

This bridge provides passive context for the `noise-removal-via-commit-edit` skill, which detects and removes IDE
artifact noise (m2e `.project`, `.classpath`, `.settings/`, JDT LS, `filteredResources`) from existing commits by
composing the [`git-commit-edit`](../git-commit-edit/SKILL.md) skill, with mandatory user confirmation.

It should be invoked whenever the user asks to remove IDE artifact noise from a specific historical commit, or
whenever a commit audit surfaces Eclipse/IntelliJ/VSCode artifacts that should never have been committed.

- **Primary Entry Point**: [.agents/skills/noise-removal-via-commit-edit/SKILL.md](./SKILL.md)
- **Composed Skill**: [`git-commit-edit`](../git-commit-edit/SKILL.md) — provides the underlying interactive-rebase
  mechanics.
