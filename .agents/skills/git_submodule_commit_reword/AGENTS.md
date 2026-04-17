# Git Submodule Commit Reword — Agent Bridge

> **Skill Location:** `.agent/skills/git_submodule_commit_reword/SKILL.md`

## When to Use This Skill

Invoke this skill when the user asks to **reword** a submodule commit with complete metadata (similar to the first commit format in the repository).

## Quick Reference

| Trigger Phrase | Action |
| :--- | :--- |
| "reword the second commit" | Load skill, extract submodule info, amend with full metadata |
| "fix commit message with submodule details" | Load skill, follow metadata extraction protocol |
| "add parent, author, committer info to commit" | Load skill, use complete message format |

## What This Skill Does

1. Creates backup branch before any changes
2. Creates temp branch at target commit
3. Extracts complete submodule metadata:
   - Submodule path and commit SHA
   - Parent commit(s)
   - Commit message
   - File changes (added/modified/deleted with line counts)
   - Author name, email, timestamp
   - Committer name, email, timestamp
4. Amends commit with complete message format
5. Cherry-picks remaining commits
6. Updates master branch
7. Cleans up temporary branches

## Key Commands

```bash
# Extract submodule commit
git ls-tree HEAD <submodule-name>

# Get commit metadata
GIT_PAGER=cat git -C <submodule-path> log --format=format:"%P%n%an <%ae>%n%ad%n%cn <%ce>%n%cd%n%B" <sha> -1

# Get file changes
GIT_PAGER=cat git -C <submodule-path> diff-tree --no-commit-id -r --numstat <sha>
```

## Related Skills

- `git_submodule_addition` — Adding new submodules
- `git_history_refinement` — Complex history reconstruction
- `git_submodule_pointer_repair` — Fixing detached HEAD in submodules

---

> **Note:** Full operational details are in `SKILL.md`. This file provides passive context for quick reference.