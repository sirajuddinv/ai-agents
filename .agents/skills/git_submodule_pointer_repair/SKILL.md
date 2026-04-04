---
name: Git Submodule Pointer Repair
description: Industrial protocol for surgically fixing invalid submodule pointers in parent repository history using the Synchronization Horizon algorithm.
category: Git & Repository Management
---

# Git Submodule Pointer Repair Skill (v1)

This skill provide surgical, high-fidelity repair of invalid submodule pointers within a parent repository's history. It implements the **Synchronization Horizon** algorithm to autonomously identify the correct architectural alignment point between parent mandates and modular history.

***

## 1. Environment & Dependencies

The agent MUST verify the following tools are available before execution:

- **Git**: Mandatory for repository operations.
- **Python 3**: Mandatory for the `repair.py` synchronization engine.

```bash
# Verify environment
which git && git --version
which python3 && python3 --version
```

***

## 2. Operational Logic: The Synchronization Horizon

This algorithm identifies the exact architectural alignment point ($s_p$) where parent repository mandates are satisfied by submodule history.

### 2.1 Detection & Backtracking (The Discovery)
1. **Identify Target**: Locate submodules with invalid pointers in the input Parent SHA.
2. **Verify Validity**: For every invalid pointer, backtrack in the parent history to find the **Last Known Valid SHA**.
3. **Isolate Intro Commit**: The commit that changed the last known valid SHA to the first invalid SHA is the **Invalid Reference Introduction Commit**.

### 2.2 Cumulative Synchronization Scan (Mapping)
1. **Extract Mandates**: Retrieve the commit message of the **Invalid Reference Introduction Commit**.
2. **Successor Analysis**: Identify the successor commits ($s_1, s_2, \dots, s_n$) of the Last Known Valid SHA in the submodule repository.
3. **Iterative Alignment**: Analyze the cumulative changes $\{s_1 \dots s_i\}$. 
4. **Identify Boundary $s_p$**: The loop stops at $s_p$ where the cumulative changes correctly and completely satisfy the parent's mandates ($s_{p+1}$ MUST be unrelated drift).

### 2.3 Surgical Repair (Execution)
1. **Safety Backup**: MUST create a backup tag before modification (e.g., `backup-pointer-repair-<timestamp>`).
2. **Pointer Swap**: Surgically edit the **Invalid Reference Introduction Commit**, replacing the invalid hash with $s_p$.
3. **Propagation**: Propagate the fix across subsequent history using a non-interactive rebase or equivalent transformation.

***

## 3. Cleanup Protocol

The safety backup tag MUST be managed with 100% human-in-the-loop fidelity.

1. **Verification**: Confirm `ls-tree` at the sync point reflects $s_p$.
2. **Authorization**: Explicitly ask the user: *"History repair verified. May I delete the safety backup tag <tag_name>?"*
3. **Execution**: Delete the tag ONLY upon explicit "yes" confirmation.

***

## 4. Automation Engine

The surgical logic is encapsulated in the industrial Python engine:
[scripts/repair.py](./scripts/repair.py)

```bash
# Example Usage:
python3 .agents/skills/git_submodule_pointer_repair/scripts/repair.py --parent <SHA> --submodule <PATH>
```

***

## 5. Traceability & Related Conversations

- **Rule Source**: Promotion of **[Git Submodule History Repair Rules](../../../ai-agent-rules/git-submodule-history-repair-rules.md)**.
- **Session Log**: Industrialized from the 110-commit surgical repair walkthrough.
