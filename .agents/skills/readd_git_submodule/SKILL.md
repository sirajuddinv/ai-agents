---
name: readd_git_submodule
description: Industrial protocol for removing and re-adding Git submodules to standardize paths or repair configurations.
category: Git & Repository Management
---

# Re-add Git Submodule Skill (v1)

This skill provides a standardized, high-fidelity protocol for the atomic removal and re-addition of Git submodules. It ensures a "pure removal" (cleaning up all internal Git metadata) before re-adding at a new or standardized path.

***

## 1. Environment & Dependencies

Before execution, the agent MUST verify:

- **git**: Core tool for submodule operations.
    - Check: `which git`
    - Version: `git --version`
- **Submodule Protocol Compliance**: Refer to `ai-agent-rules/git-submodule-rules.md` for the core principles of branch tracking.

***

## 2. Extraction & Plan Mapping

1. **Identify Repository URL**: Extract the URL from `.gitmodules` for the target path.
2. **Determine New Path**: Apply the project's naming convention (e.g., `git_submodule_addition` skill's mapping) to derive the target directory.
3. **Atomic Plan**: Present a step-by-step plan for the specific submodule migration.

***

## 3. Execution Workflow (Atomic & Sequential)

The agent MUST perform the following steps **atomically for each submodule** to ensure zero error propagation:

### 3.1 Pure Removal

```bash
# Force remove the submodule from the working tree and .gitmodules
git rm -f <OLD_PATH>

# Clean up the cached configuration from .git/config
git config --remove-section submodule.<OLD_PATH>

# Purge the internal Git storage for the submodule
rm -rf .git/modules/<OLD_PATH>
```

- **Pedagogical Breakdown**:
    - `git rm -f`: Force removes the directory and updates `.gitmodules`.
    - `git config --remove-section`: Ensures future re-addition at a similar path doesn't conflict with stale config.
    - `rm -rf .git/modules/`: Completely wipes the submodule's history storage, allowing a fresh clone.

### 3.2 Re-addition

```bash
# Add the submodule at the new/standardized path
git submodule add <URL> <NEW_PATH>
```

### 3.3 Synchronization & Tracking

```bash
# Initialize and fetch data recursively
git submodule update --init --recursive <NEW_PATH>

# Ensure branch tracking (don't leave in detached HEAD)
cd <NEW_PATH>
git checkout $(git remote show origin | grep "HEAD branch" | cut -d ":" -f 2 | xargs)
cd -
```

***

## 4. Verification & Commit

1. **Verify Status**: Run `git status` to confirm the deletion of the old path and addition of the new path.
2. **Propose Atomic Commit**:
    - Message: `refactor(submodule): standardize <OLD_PATH> to <NEW_PATH>`
    - Include: URL and rationale.

***

## 5. Traceability & Related Protocols

- **Skill Factory**: Generated via the Skill Factory protocol.
- **Related Skill**: `git_submodule_addition` (for initial extraction logic).
- **Parent Rules**: `ai-agent-rules/git-submodule-rules.md`.
- **Reference**: [StackOverflow: How do I remove a submodule?](https://stackoverflow.com/a/1260982/3333438)
