---
name: Git Rebase Standardization
description: Passive context bridge for hierarchical multi-branch rebasing with dependency mapping and Commit Action Mapping.
category: Git & Repository Management
---

# Git Rebase Standardization (Ref)

This bridge provides passive context for the `git-rebase-standardization` skill, which performs hierarchical
multi-branch rebasing using dependency mapping, Commit Action Mapping (CAM), dig-down fidelity, and operational
guardrails to deduplicate cross-branch commits.

It should be invoked whenever the user asks to rebase branches, manage multi-branch chains, or deduplicate commits
across diverged feature branches.

- **Primary Entry Point**: [.agents/skills/git-rebase-standardization/SKILL.md](./SKILL.md)
- **Related Skills**:
    - [`git-history-refinement`](../git-history-refinement/SKILL.md) — single-branch reconstruction
    - [`git-divergence-audit`](../git-divergence-audit/SKILL.md) — pre-rebase diff analysis
