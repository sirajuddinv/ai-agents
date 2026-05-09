# AGENTS.md — Git Commit Message Bulk Reword

This directory hosts a single AI Agent Skill. The Single Source of
Truth for execution is [`SKILL.md`](./SKILL.md).

## Purpose

Audit a contiguous range of commits against the project's commit
message rules (Conventional Commits, etc.), propose
diff-driven replacements, and reword them all in a single
non-interactive rebase.

## Composition

This is the **range** layer of a 3-skill stack:

```
git-commit-edit                       (base)
└── git-commit-message-reword         (single-commit composer)
    └── git-commit-message-bulk-reword (THIS — range composer)
```

The per-commit message authoring concern is owned by
[`../git-commit-message-reword/SKILL.md`](../git-commit-message-reword/SKILL.md).
The rebase mechanics, backup, and push gates are owned by
[`../git-commit-edit/SKILL.md`](../git-commit-edit/SKILL.md). This
skill amortizes the per-commit primitive across N commits via a
shared map and a single rebase invocation.

## When to Use

- A contiguous range of commits has non-compliant subject lines
  (e.g., GitHub Web UI auto-generated `Create X.md` / `Update X.md`).
- The user wants the entire range fixed in one rebase rather than
  one-at-a-time.

## When NOT to Use

- Only one commit needs rewording → use
  [`../git-commit-message-reword/SKILL.md`](../git-commit-message-reword/SKILL.md).
- Commits also need file content changes → use
  [`../git-commit-edit/SKILL.md`](../git-commit-edit/SKILL.md) per commit.
- Range spans a public, actively-shared base branch → coordinate first.

## Active Instructions

See [`SKILL.md`](./SKILL.md) for:

- §0 Pre-reword audit (rules-file discovery, range enumeration, diff
  classification, proposal table, backup).
- §1–3 Reword map, sequence/commit editor scripts, rebase execution.
- §4 Verification + Conventional Commits lint regex.
- §5 Push authorization (delegated).
- §6 Cleanup.

## Related Skills

- [`../git-commit-message-reword/SKILL.md`](../git-commit-message-reword/SKILL.md) — single-commit composer (this skill's primitive)
- [`../git-commit-edit/SKILL.md`](../git-commit-edit/SKILL.md) — base of the 3-layer stack
- [`../git-history-refinement/SKILL.md`](../git-history-refinement/SKILL.md)
- [`../noise-removal-via-commit-edit/SKILL.md`](../noise-removal-via-commit-edit/SKILL.md)
