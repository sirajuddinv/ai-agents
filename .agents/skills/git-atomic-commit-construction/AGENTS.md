---
name: Git Atomic Commit Construction
description: Passive context bridge for analyzing, grouping, and arranging working-tree changes into atomic commits.
category: Git & Repository Management
---

# Git Atomic Commit Construction (Ref)

This bridge provides passive context for the `git-atomic-commit-construction` skill, which analyzes working-tree
changes, groups them by logical concern, isolates formatting from semantic edits, performs hunk-based staging, and
proposes an authorization-gated commit sequence.

It should be invoked whenever the user asks to "commit changes," "stage and commit," "arrange commits," or whenever
working-tree changes span multiple concerns that need atomic grouping.

- **Primary Entry Point**: [.agents/skills/git-atomic-commit-construction/SKILL.md](./SKILL.md)
- **Related Skills**:
    - [`git-commit-edit`](../git-commit-edit/SKILL.md) — for editing commits already in history
    - [`git-history-refinement`](../git-history-refinement/SKILL.md) — for reconstructing diverged history
