---
name: Git Cross-Repository Cherry-Pick
description: Industrial protocol for cherry-picking commits across unrelated Git repositories or submodules via temporary remote bridging.
category: Git & Repository Management
---

# Git Cross-Repository Cherry-Pick Skill (v1)

This skill provides a standardized workflow for transferring specific commits from one Git repository (source) to another (target) where no direct relationship exists. It utilizes temporary remote bridging to maintain commit metadata and history fidelity.

***

## 1. Environment & Dependencies

Before execution, the agent **MUST** verify the industrial environment.

1. **Verify Git**:
   ```bash
   git --version
   ```
2. **Verify Repository Context**:
   ```bash
   git rev-parse --is-inside-work-tree
   ```
   * *Returns `true` if within a Git repo (target).*

***

## 2. Phase 1: Bridging & Discovery

Establish a temporary connection to the source repository.

1. **Add Temporary Remote**:
   ```bash
   git remote add <temp_name> <absolute_path_to_source_repo>
   ```
   * `<temp_name>`: A unique temporary identifier (e.g., `source_bridge`).
   * `<absolute_path_to_source_repo>`: The local filesystem path to the source repository.

2. **Fetch Source History**:
   ```bash
   git fetch <temp_name>
   ```
   * Retrieves the commit objects and references from the source repo.

3. **Verify Commit Hash**:
   ```bash
   git log <temp_name>/<branch_name> --oneline -n 5
   ```
   * Ensures the target commit hash is visible and correct.

***

## 3. Phase 2: Execution & Conflict Resolution

Transfer the commit and handle any environmental friction.

1. **Initiate Cherry-Pick**:
   ```bash
   git cherry-pick <commit_hash>
   ```
   * If the cherry-pick is clean, proceed to Phase 3.
   * If a **CONFLICT** occurs, follow the sub-protocol below.

### 2.1 Conflict Resolution Protocol

1. **Identify Conflicts**:
   ```bash
   git status
   ```
2. **Merge Content**:
   * Manually resolve conflicts in the affected files, prioritizing project-standard rules while preserving required local logic.
3. **Stage Resolutions**:
   ```bash
   git add <resolved_file>
   ```
4. **Complete Cherry-Pick**:
   ```bash
   git cherry-pick --continue --no-edit
   ```
   * *Note: Use `--no-edit` to preserve the original commit message unless a reword is specifically requested.*

***

## 4. Phase 3: Cleanup & Verification

Restore the repository to a clean, production-ready state.

1. **Remove Temporary Remote**:
   ```bash
   git remote remove <temp_name>
   ```
   * **MANDATORY**: Never leave bridging remotes in the configuration.

2. **Verify Result**:
   ```bash
   git log -n 1 --oneline
   git status
   ```
   * Ensure the commit is present and the working tree is clean.

***

## 5. Related Conversations & Traceability

- Standard established during the **Industrial Git Submodule Maintenance** session (April 2026).
- Follows [Skill Factory Protocol](../../skills/skill_factory/SKILL.md).
- Compliance: 100% Rule 1.1 (tilde-portable).
- Compatibility: macOS/Linux (zsh/bash).
