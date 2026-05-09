---
name: Git Commit Edit
description: Passive context bridge for in-place editing of existing Git commits via interactive rebase.
category: Git & Repository Management
---

# Git Commit Edit (Ref)

This bridge provides passive context for the `git-commit-edit` skill, enabling the agent to perform targeted,
surgical modifications to a specific commit — removing files, adding files, amending content, or fixing mixed
concerns — while preserving descendant commits and working-tree state. It is the "scalpel" complement to the
"rebuild" approach in [`git-history-refinement`](../git-history-refinement/SKILL.md).

It should be invoked whenever the user asks to "edit a commit," "remove files from a commit," "fix a commit," or
"correct the author of a historical commit," and whenever a specific commit hash is named with targeted changes.

### Core Documentation (SSOT)

- **Active Instructions**: [SKILL.md](./SKILL.md)
- **Primary Entry Point**: `.agents/skills/git-commit-edit/SKILL.md`

### Functional Capabilities

1. Pre-edit analysis — target identification, descendant count, remote divergence check.
2. Mandatory workspace backup branch (`backup/pre-edit-<n>`) before any destructive rebase.
3. Sequence-editor automation that marks the target commit as `edit` non-interactively.
4. Stash / amend / continue / pop lifecycle with explicit user authorization gates.
5. Force-push reconciliation guidance when the branch is already published.

### When NOT to Use

- Splitting a commit into atomic pieces → [`git-history-refinement`](../git-history-refinement/SKILL.md)
- Composing new commits from working-tree changes → [`git-atomic-commit-construction`](../git-atomic-commit-construction/SKILL.md)
- Multi-branch rebasing → [`git-rebase-standardization`](../git-rebase-standardization/SKILL.md)
- Message-only fix on the most recent commit → `git commit --amend -m "..."` directly

### Reference Mapping

- **Source Rules**:
    - [`git-operation-rules.md`](../../../ai-agent-rules/git-operation-rules.md) — Sections 2–4 (commit/push/stash protocols)
    - [`git-atomic-commit-construction-rules.md`](../../../ai-agent-rules/git-atomic-commit-construction-rules.md) — Phase 9 (execution & verification), Phase 14 (push protocol)
- **Composer Skill**: [`noise-removal-via-commit-edit`](../noise-removal-via-commit-edit/SKILL.md) — invokes this
  skill to purge IDE artifact noise from existing commits.
