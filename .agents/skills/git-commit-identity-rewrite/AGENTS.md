# AGENTS.md — Git Commit Identity Rewrite

This directory hosts a single AI Agent Skill. The Single Source of
Truth for execution is [`SKILL.md`](./SKILL.md).

## Purpose

Rewrite the **author** and **committer** identity (and optionally the
author/committer dates) of one or more historical commits, copying
the identity from a designated source commit. Coordinates rewrites
across a parent repo and one of its submodules in a single workflow.

## Composition

This is a **composer** over [`../git-commit-edit/SKILL.md`](../git-commit-edit/SKILL.md).
The base owns the interactive-rebase mechanics, backup branches,
push gate, and cleanup gate. This skill owns source-identity
discovery, the committer-override env-var block, date-preservation
modes, and the submodule-pointer cascade.

## When to Use

- Both author **and** committer must be rewritten in lock-step.
- Identity is copied from a designated source commit.
- The same identity must land on commits across a parent repo and
  one of its submodules.

## When NOT to Use

- Author alone is wrong → `git-commit-edit` §3e (single-field
  `--author=`) is sufficient.
- Message only → use [`../git-commit-message-reword/SKILL.md`](../git-commit-message-reword/SKILL.md).
- Content only → use [`../git-commit-edit/SKILL.md`](../git-commit-edit/SKILL.md).
- Target is a merge commit → re-plan with `git rebase -i --rebase-merges`.

## Active Instructions

See [`SKILL.md`](./SKILL.md) for:

- §0 Pre-edit discovery (source identity, target dates, merge guard,
  cross-repo cascade detection, date-scope decision).
- §1 Per-target loop (delegates to `git-commit-edit`).
- §3 Identity-override env-var block (the core mechanic).
- §4 Tree-parity verification.
- §5 Submodule pointer cascade handling.
- §6 / §7 Push and cleanup gates (delegated).

## Related Skills

- [`../git-commit-edit/SKILL.md`](../git-commit-edit/SKILL.md) — base
- [`../git-commit-message-reword/SKILL.md`](../git-commit-message-reword/SKILL.md) — sibling composer
- [`../git-submodule-pointer-repair/SKILL.md`](../git-submodule-pointer-repair/SKILL.md) — multi-commit cascade
