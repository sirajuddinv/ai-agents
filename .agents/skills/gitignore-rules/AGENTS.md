---
name: Gitignore Rules
description: Passive context bridge for auditing .gitignore files and applying verified fixes to common pitfalls.
category: Git & Version Control
---

# Gitignore Rules (Ref)

This bridge provides passive context for the `gitignore-rules` skill, which audits `.gitignore` files for common
pitfalls — especially directory-ignore patterns that silently break negation rules — and applies verified fixes.

It should be invoked whenever the user asks to audit `.gitignore`, debug "why is my file still ignored," or
whenever a directory-ignore + negation pattern combination is detected.

- **Primary Entry Point**: [.agents/skills/gitignore-rules/SKILL.md](./SKILL.md)
