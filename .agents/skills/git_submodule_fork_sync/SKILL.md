---
name: git_submodule_fork_sync
description: Automates the realignment of .gitmodules to track internal submodule forks while securing origin upstreams.
category: Git & Repository Management
---

# Git Submodule Fork Synchronization Skill (v1)

This skill tracks and remedies discrepancies where a localized submodule has been forked by the user. It asserts that
the fork becomes the true tracked dependency inside `.gitmodules`, while enforcing that the original repository is
locked in as the `upstream` remote natively to support downstream rebasing.

***

## 1. Environment & Dependencies

Before execution, the agent MUST verify:

- **git**: Core tool for submodule operations.
    - Check: `which git`
    - Version: `git --version`
- **python3**: Required execution engine for the discrepancy analysis sequence.
    - Check: `which python3`
- **PAGER Environment**: The agent MUST ensure `PAGER=cat` is universally utilized for Git invocations to prevent
  hanging interactive shells.

***

## 2. Fork Synchronization Protocol

The logic to traverse the submodules, analyze the internal `.git/config` against `.gitmodules`, and inject the
`upstream` remotes is maintained via a standalone payload.

### 2.1 Script Execution

> [!IMPORTANT]
> The agent MUST NOT use generic Bash loops for this logic to adhere to the Script SSOT Mandate. Instead, invoke the
> centralized discrepancy parser.

```bash
# Execute the discrepancy synchronization payload from the root workspace
python3 .agents/skills/git_submodule_fork_sync/scripts/sync.py
```

- **Pedagogical Breakdown**:
    - The script identifies any submodule where the globally-registered `url=` inside `.gitmodules` inherently
      diverges from the initialized submodule's internal `origin`.
    - It overwrites `.gitmodules` to track the fork.
    - It extracts the replaced tracking URL and checks the isolated `.git/config` within the submodule context.
      "If not already there", it adds `git remote add upstream <original>`.

***

## 3. Verification & Commit

1. **Verify Lineage**: Run `PAGER=cat git diff --cached` or `PAGER=cat git status` to strictly verify that
`.gitmodules` reflects exclusively the precise URL swap and nothing else.
2. **Propose Atomic Commit**:
    - Execute the atomic `fix` commit confirming the realignment to strictly obey the rules.
    - **Required Form**:
      `fix(submodules): synchronize .gitmodules with internal fork URLs`
    - **Body Element**: Add detailed reasoning verifying exactly how many instances were adjusted alongside the
      addition of `upstream` safety parameters.

***

## 4. Traceability & Related Protocols

- **Skill Factory**: Generated via the Skill Factory protocol responding explicitly to the need for local fork
  integration.
- **Related Meta-Skill**: `readd_git_submodule` (Orchestrator).
- **Parent Rules**: `ai-agent-rules/git-submodule-rules.md`, `ai-agent-rules/git-atomic-commit-construction-rules.md`.
