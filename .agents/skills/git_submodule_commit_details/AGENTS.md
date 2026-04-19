# Git Submodule Commit Details — Agent Bridge

> **Skill Location:** `.agents/skills/git_submodule_commit_details/SKILL.md`

## When to Use This Skill

Invoke this skill whenever **complete submodule commit metadata** is
needed — regardless of what the metadata will be used for (rewording,
sync message composition, audit, etc.).

## Quick Reference

| Trigger Phrase | Action |
| :--- | :--- |
| "extract submodule commit details" | Load skill, run Steps 1–6 |
| "get commit metadata from submodule" | Load skill, run Steps 1–6 |
| "what does this submodule commit contain?" | Load skill, run Steps 1–6 |
| "compose submodule sync commit message" | Load skill, pass output to `git_atomic_commit` |
| "reword submodule commit with full metadata" | Load skill, pass output to `git_submodule_commit_reword` |

## What This Skill Produces

A single structured record per submodule SHA containing:

1. Submodule path and SHA
2. Parent SHA(s) — merge-aware
3. Full commit message body (zero summarization)
4. File changes — additions, deletions, per-file classification
5. Author name, email, timestamp
6. Committer name, email, timestamp
7. Registration URL from `.gitmodules`

## Key Commands

```bash
# Step 1 — resolve pointer
GIT_PAGER=cat git -C <parent-repo-path> ls-tree HEAD <submodule-name>

# Step 2 — extract core metadata
GIT_PAGER=cat git -C <submodule-path> log \
  --format=format:"%P%n%an <%ae>%n%ad%n%cn <%ce>%n%cd%n%B" \
  <submodule-sha> -1

# Step 3 — file changes (regular commits)
GIT_PAGER=cat git -C <submodule-path> diff-tree \
  --no-commit-id -r --numstat <submodule-sha>

# Step 3 — file changes (merge commits)
GIT_PAGER=cat git -C <submodule-path> diff <parent1> <parent2> --stat

# Step 4 — classify added vs modified vs deleted
GIT_PAGER=cat git -C <submodule-path> ls-tree -r <parent-sha> | grep <filename>

# Step 5 — registration URL
GIT_PAGER=cat git -C <parent-repo-path> config \
  --file .gitmodules submodule.<submodule-name>.url
```

## Consumer Skills

- [`git_submodule_commit_reword`](../git_submodule_commit_reword/SKILL.md)
  — passes the record into the amended commit message
- [`git_atomic_commit`](../git_atomic_commit/SKILL.md)
  — passes the record into submodule sync commit messages

---

> **Note:** Full operational details, pedagogical command breakdowns,
> and prohibited behaviors are in `SKILL.md`. This file provides passive
> context for quick reference only.
