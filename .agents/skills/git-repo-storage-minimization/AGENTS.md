# AGENTS.md — Git Repository Storage Minimization

This directory hosts a single AI Agent Skill. The Single Source of
Truth for execution is [`SKILL.md`](./SKILL.md).

## Purpose

Reduce on-disk size of a Git repository and its initialized
submodules via deinitialization, aggressive `gc`, reflog expiry,
and pruning — **without rewriting commit history**.

## When to Use

- User asks to "shrink", "minimize", "reduce size of", or "clean
  up disk usage" of a Git repository.
- `du -sh .git` shows a footprint disproportionate to content.
- User wants to deinitialize unused submodules to reclaim
  `.git/modules/` storage.
- After a destructive content removal where unreachable objects
  need pruning.

## Active Instructions

See [`SKILL.md`](./SKILL.md) for:

- Pre-minimization audit protocol (Step 0).
- Submodule deinit + cache deletion (Step 1).
- Aggressive `gc --prune=now` on parent (Step 2).
- Reflog expiry + final prune (Step 3).
- Per-submodule maintenance (Step 4).
- Before/after audit (Step 5).
- Prohibited behaviors and common pitfalls.

## Related Skills

- [`../git-commit-edit/SKILL.md`](../git-commit-edit/SKILL.md)
- [`../git-submodule-removal/SKILL.md`](../git-submodule-removal/SKILL.md)
- [`../git-submodule-uninitialized-handler/SKILL.md`](../git-submodule-uninitialized-handler/SKILL.md)
