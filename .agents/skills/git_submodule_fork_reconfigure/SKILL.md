---
name: Git Submodule Fork Reconfigure
description: Operational protocol for forking submodules on the fly and reconfiguring remotes to handle permission issues.
category: Git & Repository Management
---

# Git Submodule Fork Reconfigure Skill (v1)

This skill provides a surgical protocol for handling "Permission Denied" (403) errors when pushing to submodules. It automates the process of forking the upstream repository via the GitHub CLI and reconfiguring the submodule's local remotes to track the new fork while preserving the original as an `upstream` source.

***

## 1. Environment & Dependencies

Before execution, the agent **MUST** verify the industrial environment.

1. **Verify Git**:
   ```bash
   git --version
   ```
2. **Verify GitHub CLI**:
   ```bash
   gh --version
   gh auth status
   ```
   * *If `gh` is not logged in, the agent MUST instruct the user to run `gh auth login` manually.*

***

## 2. Phase 1: Forking & Remote Preparation

When a push to a submodule's `origin` fails due to 403 Forbidden.

1. **Identify Upstream URL**:
   ```bash
   git remote get-url origin
   ```
2. **Check for Existing Fork**:
   ```bash
   gh repo list <owner> --limit 100 | grep -i <fork_name>
   ```
   * `<owner>`: Your GitHub username.
   * `<fork_name>`: The expected fork name (submodule directory name).
   * **If fork exists, skip to Phase 2** — no need to create a new fork.
3. **Create Fork**:
   ```bash
   gh repo fork <upstream_repo_path> --fork-name <desired_name>
   ```
   * `<upstream_repo_path>`: The owner/repo string (e.g., `GuDaStudio/skills`).
   * `--fork-name`: The specific name for the fork. **MANDATORY**: This MUST match the submodule directory name unless the user explicitly requests otherwise.
   * **Note**: Handle the interactive clone prompt by sending `n` if already within the submodule directory.

***

## 3. Phase 2: Remote Reconfiguration

Realign the submodule's remotes to prioritize the personal fork.

1. **Rename Original Remote**:
   ```bash
   git remote rename origin upstream
   ```
   * Shifts the read-only original repo to the `upstream` namespace.

2. **Add Fork Remote**:
   ```bash
   git remote add origin <fork_url>
   ```
   * `<fork_url>`: The URL of the newly created fork (e.g., `https://github.com/<user>/<fork_name>.git`).

3. **Push & Track**:
   ```bash
   git push -u origin <branch_name>
   ```
   * `-u`: Sets the upstream tracking reference for the local branch.

***

## 4. Phase 3: Parent Repository Alignment

Ensure the parent repository recognizes the fork for future initializations.

1. **Update .gitmodules**:
   * Navigate to the parent repository root.
   * Update the `url` field for the relevant submodule in `.gitmodules`.
2. **Synchronize Config**:
   ```bash
   git submodule sync
   ```
   * Updates the `.git/config` of the parent repo with the new URL.
3. **Commit Alignment**:
   ```bash
   git add .gitmodules
   git commit -m "chore(submodules): align <submodule_name> with personal fork

- Update URL from <original_url> to <fork_url>.
- Enable write access via personal fork remote reconfiguration."
   ```
   * **MANDATORY**: Follow the project's [Git Commit Message Rules](../../../ai-agent-rules/git-commit-message-rules.md).
   * **Fidelity Requirement**: The body MUST include both the original and new fork URLs.

***

## 5. Related Conversations & Traceability

- Standard established during the **Industrial Git Submodule Maintenance** session (April 2026).
- Follows [Skill Factory Protocol](../../skills/skill_factory/SKILL.md).
- Complements [Git Submodule Fork Sync](../git_submodule_fork_sync/SKILL.md) (Automated Realignment).
- Compatibility: macOS/Linux/Windows (Git Bash/Zsh).
