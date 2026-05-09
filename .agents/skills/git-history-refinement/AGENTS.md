---
name: Git History Refinement
description: Passive context bridge for refining or reconstructing existing commit history with backup branches and tree parity verification.
category: Git & Repository Management
---

# Git History Refinement (Ref)

This bridge provides passive context for the `git-history-refinement` skill, which uses backup branches, atomic
extraction, tree parity verification, and safe remote push reconciliation to refine, split, or reconstruct existing
commit history without losing content.

It should be invoked whenever the user asks to refine, split, reorganize, or reconstruct commit history, especially
when the working tree must remain bit-identical after history rewrite.

- **Primary Entry Point**: [.agents/skills/git-history-refinement/SKILL.md](./SKILL.md)
- **Related Skills**:
    - [`git-commit-edit`](../git-commit-edit/SKILL.md) — surgical single-commit edits (scalpel vs rebuild)
    - [`git-rebase-standardization`](../git-rebase-standardization/SKILL.md) — multi-branch rebasing chains
