# AGENTS.md (Ref)

This directory hosts the **Git LFS Selective Clone** skill — the industrial
protocol for cloning a Git LFS repository (and its submodules) without
downloading any LFS blobs, then selectively materializing only the LFS
objects the user actually needs.

For the full active instructions, see [SKILL.md](./SKILL.md).

## When to Reach For This Skill

- The user says "clone without LFS" / "skip LFS" / "I want pointers only".
- A clone of a known LFS repo "hangs" or downloads many GB unexpectedly.
- The user wants a subset of LFS files (e.g., one zip but not the 5 GB
  of video companions).
- A repo's submodules ship LFS objects and must be initialized without
  pulling those blobs.

## Critical Reminder

`GIT_LFS_SKIP_SMUDGE=1` alone is **NOT** sufficient on modern Git LFS
installs. The skill mandates the **four-override** combination:

1. `GIT_LFS_SKIP_SMUDGE=1` (env var)
2. `-c filter.lfs.smudge=`
3. `-c filter.lfs.process=` ← the one usually forgotten
4. `-c filter.lfs.required=false`

Submodule recursion MUST re-supply all four overrides — Git config does
not cross the submodule boundary.

## Related Skills & Rules

- [`git-repo-storage-minimization`](../git-repo-storage-minimization/SKILL.md)
- [`git-submodule-uninitialized-handler`](../git-submodule-uninitialized-handler/SKILL.md)
- [Git Repository Management Rules](../../../ai-agent-rules/git-repo-management-rules.md)
- [Repo Discovery Rules](../../../ai-agent-rules/repo-discovery-rules.md)
