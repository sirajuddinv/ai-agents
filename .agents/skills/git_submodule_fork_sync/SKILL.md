---
name: git_submodule_fork_sync
description: Automates the realignment of .gitmodules to track internal submodule forks while securing origin upstreams.
category: Git & Repository Management
---

# Git Submodule Fork Synchronization Skill (v1.1)

This skill tracks and remedies discrepancies where a localized submodule has been forked by the user. It asserts that
the fork becomes the true tracked dependency inside `.gitmodules`, while enforcing that the original repository is
locked in as the `upstream` remote natively to support downstream rebasing.

> [!IMPORTANT]
> **Atomic History Mandate**: Per repository standards, submodule synchronization adjustments MUST be woven back into the
> original initialization commits (`chore(submodules): add <name>`) rather than appended as a monolithic fix at the end
> of the history tree.

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

### 2.1 Analysis

```bash
# Analyze discrepancies
python3 .agents/skills/git_submodule_fork_sync/scripts/sync.py analyze
```

### 2.2 Atomic History Integration

#### Strategry A: Fixup & Autosquash (Recommended for 1-2 changes)

1. Identify the origin commit SHA for the submodule.
2. Update `.gitmodules` URL manually or via script.
3. Stage changes: `git add .gitmodules`
4. Commit as fixup: `git commit --fixup <SHA>`
5. Execute rebase: `GIT_SEQUENCE_EDITOR=true PAGER=cat git rebase -i --autosquash <BASE>`

#### Strategy B: Total Reconstruction (Required for large or linear chains)

If the rebase triggers massive conflicts (common in linear `.gitmodules` stacks), the agent MUST reconstruct the
history stack to guarantee atomicity.

```bash
# Execute total reconstruction from a clean base SHA
python3 .agents/skills/git_submodule_fork_sync/scripts/sync.py rebuild --base <BASE_SHA>
```

- **Pedagogical Breakdown**:
    - The `rebuild` command resets the branch to the base.
    - It then programmatically redraws every submodule initialization commit.
    - It natively handles both the fork `url=` tracking and the `upstream` remote injection.
    - Feature commits MUST be cherry-picked onto the newly perfected baseline once reconstruction is complete.

***

## 3. Verification & Finalization

1. **Verify Lineage**: Run `PAGER=cat git log --oneline` to ensure the history stack is a clean vertical line of
   `chore(submodules): add` commits.
2. **Verify Remotes**: Use `git -C <path> remote -v` on a fork submodule to confirm both `origin` (fork) and
   `upstream` (author) are correctly established.

***

## 4. Traceability & Related Protocols

- **Skill Factory**: Generated via the Skill Factory protocol responding explicitly to the need for local fork
  integration.
- **Related Meta-Skill**: `readd_git_submodule` (Orchestrator).
- **Parent Rules**: `ai-agent-rules/git-submodule-rules.md`, `ai-agent-rules/git-atomic-commit-construction-rules.md`.
