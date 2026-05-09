# AGENTS.md — git-submodule-missing-revision-recovery

This is the passive-context bridge for the
[`git-submodule-missing-revision-recovery`](./SKILL.md) skill.

## Purpose

Resolve `fatal: Unable to find current revision in submodule path '<path>'` when `git submodule update --init` fails
because the recorded pointer SHA is not present in the submodule's local object database.

## Activation Triggers

- The literal error string `Unable to find current revision in submodule path` appears in terminal output.
- A registered submodule has an empty working tree, a `No commits yet` status, and `git ls-tree HEAD <path>` shows a
  valid `160000 commit <sha>` entry.
- A submodule was just added but its initial fetch silently failed; subsequent `git submodule update --init` exits
  non-zero.

## Authoritative Procedure

All operational logic lives in [`SKILL.md`](./SKILL.md). Do NOT duplicate it here.

## Companion Skills

- [`git-submodule-uninitialized-handler`](../git-submodule-uninitialized-handler/SKILL.md)
- [`git-submodule-dead-upstream-audit`](../git-submodule-dead-upstream-audit/SKILL.md)
- [`git-submodule-orphan-gitlink-recovery`](../git-submodule-orphan-gitlink-recovery/SKILL.md)
- [`git-submodule-fork-reconfigure`](../git-submodule-fork-reconfigure/SKILL.md)
