# AGENTS.md — Git Commit Message Reword

This directory hosts a single AI Agent Skill. The Single Source of
Truth for execution is [`SKILL.md`](./SKILL.md).

## Purpose

Reword a **single** existing commit's message into Conventional
Commits format compliant with the project's commit-message rules.

## Composition

This is a **composer** over [`../git-commit-edit/SKILL.md`](../git-commit-edit/SKILL.md).
The base skill owns the `reword` rebase mechanics, backup branches,
and push authorization. This skill owns reading the project's
commit-message rules, classifying the target commit's diff, authoring
the new message, and lint-verifying it.

## When to Use

- A single commit's message is non-compliant.
- Content of the commit is correct — only the message needs fixing.

## When NOT to Use

- Commit also needs content changes → use the base skill directly.
- Range of commits → use
  [`../git-commit-message-bulk-reword/SKILL.md`](../git-commit-message-bulk-reword/SKILL.md).
- Most-recent commit, never pushed → `git commit --amend -m`.

## Active Instructions

See [`SKILL.md`](./SKILL.md) for:

- §0 Pre-reword audit (rules-file discovery, diff inspection, message
  authoring, proposal table).
- §1 Delegation to `git-commit-edit` with `reword` mode and editor
  scripts.
- §2 Verification + Conventional Commits lint.
- §3 Push authorization (delegated).

## Related Skills

- [`../git-commit-edit/SKILL.md`](../git-commit-edit/SKILL.md) — base
- [`../git-commit-message-bulk-reword/SKILL.md`](../git-commit-message-bulk-reword/SKILL.md) — range composer
