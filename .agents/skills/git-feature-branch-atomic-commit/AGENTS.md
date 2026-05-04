# AGENTS.md (Git Feature Branch Atomic Commit)

Refer to [SKILL.md](./SKILL.md) for the active operational protocol for creating
atomic commits on separate feature branches with isolated branch-per-commit
workflow.

## When to Use

Use this skill when:

- User requests commits to go to **separate branches**
- Each atomic change needs its own branch for independent PR
- Branch naming follows `<prefix>/<scope>_<impact>` convention

## Related Skills

| Skill | Purpose |
| :--- | :--- |
| [`git_atomic_commit`](../git_atomic_commit/SKILL.md) | Single-branch atomic commit construction |
| [`git_history_refinement`](../git_history_refinement/SKILL.md) | Split/fix existing commit history |

## Mandates

- **Branch-Per-Commit**: Each atomic change MUST get its own branch
- **Naming Convention**: Follow `<prefix>/<scope>_<impact>` pattern
- **Preview Before Execution**: Branch names presented in preview before "start"
- **Explicit Push**: Never push without user confirmation
