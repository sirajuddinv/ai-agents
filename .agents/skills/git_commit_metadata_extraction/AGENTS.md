# Git Commit Metadata Extraction — Agent Bridge

> **Skill Location:** `.agents/skills/git_commit_metadata_extraction/SKILL.md`

## When to Use This Skill

Invoke this skill whenever **complete, zero-omission commit metadata** is needed from any Git repository (parent or submodule). This is a foundational primitive meant to be consumed by higher-level analytical or formatting skills.

## Quick Reference

| Trigger Phrase | Action |
| :--- | :--- |
| "extract raw commit details" | Load skill, run Steps 1–4 |
| "get commit metadata from repo" | Load skill, run Steps 1–4 |
| "what does this commit contain exactly?" | Load skill, run Steps 1–4 |
| "analyze this commit" | Use this skill to gather data, then apply `git_commit_details_audit` |

## What This Skill Produces

A single generic structured record per SHA containing:

1. Target commit SHA
2. Parent SHA(s) — merge-aware
3. Full commit message body (zero summarization)
4. File changes — additions, deletions, per-file classification
5. Author name, email, timestamp
6. Committer name, email, timestamp

## Key Commands

```bash
# Step 1 — extract core metadata
GIT_PAGER=cat git -C <repo-path> log \
  --format=format:"%P%n%an <%ae>%n%ad%n%cn <%ce>%n%cd%n%B" \
  <commit-sha> -1

# Step 2 — file changes (regular commits)
GIT_PAGER=cat git -C <repo-path> diff-tree \
  --no-commit-id -r --numstat <commit-sha>

# Step 3 — classify added vs modified vs deleted
GIT_PAGER=cat git -C <repo-path> ls-tree -r <parent-sha> | grep <filename>
```

## Consumer Skills

- [`git_submodule_commit_details`](../git_submodule_commit_details/SKILL.md)
  — uses this primitive to extract raw submodule commit data before formatting.
- [`git_commit_details_audit`](../git_commit_details_audit/SKILL.md)
  — uses this primitive to gather the raw facts before generating pedagogical analysis.

---

> **Note:** Full operational details, pedagogical command breakdowns,
> and prohibited behaviors are in `SKILL.md`. This file provides passive
> context for quick reference only.
