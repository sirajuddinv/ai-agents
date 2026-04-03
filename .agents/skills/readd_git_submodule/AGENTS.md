# Re-add Git Submodule Companion

> **Skill ID:** `readd_git_submodule`
> **SSOT:** [SKILL.md](./SKILL.md)

## Passive Context

This skill provides the mandatory protocol for migrating or repairing Git submodules. It enforces a "pure removal" phase before any re-addition to prevent configuration drift and stale metadata corruption.

## Usage Scenarios

| Trigger | Action |
|---|---|
| "Standardize submodule paths" | Apply Section 3 (Migration) one-by-one |
| "Repair broken submodule" | Apply Section 3 to clear and re-initialize |
| "Rename submodule directory" | Follow the Extraction -> Removal -> Re-addition sequence |

## Related Links

- [Submodule Addition Skill](../../../.agent/skills/git_submodule_addition/SKILL.md)
- [Git Submodule Rules](../../../ai-agent-rules/git-submodule-rules.md)
- [StackOverflow: Removal Instructions](https://stackoverflow.com/a/1260982/3333438)
