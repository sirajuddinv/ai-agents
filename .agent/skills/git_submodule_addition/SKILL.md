---
name: git_submodule_addition
description: Industrial protocol for adding Git submodules with automated naming conventions and branch tracking initialization. Use when the user provides a repository URL and asks to "add as a submodule".
category: Git & Repository Management
---

# Git Submodule Addition Skill (v1)

This skill automates the integration of external repositories as Git submodules, ensuring consistent naming,
initialization, and compliance with the project's branch-tracking standards.

***

## 1. Environment & Dependencies

Before execution, the agent MUST verify:

- **git**: Core tool for submodule operations.
    - Check: `which git`
    - Version: `git --version`
- **Submodule Protocol Compliance**: Refer to `ai-agent-rules/git-submodule-rules.md` for the core principles of
  branch tracking and avoiding detached HEAD states.

***

## 2. Extraction & Path Mapping Protocol

The agent MUST automatically map the repository URL to a standardized, underscore-based directory name.

- **Extraction Logic**:
    - URL: `https://github.com/[OWNER]/[REPO](.git)`
    - Target Directory: `[owner_lowercase]_[repo_lowercase]`
        - `[owner_lowercase]`: Output of `[OWNER]` lowercased with hyphens preserved.
        - `[repo_lowercase]`: Output of `[REPO]` lowercased with hyphens preserved.
- **Transformation Examples**:
    - Source: `https://github.com/LJT-520/openClaw-backup.git`
    - Target: `ljt-520_openclaw-backup`
    - Source: `https://github.com/H-H-E/media-center.git`
    - Target: `h-h-e_media-center`
    - Source: `https://github.com/microsoft/GitHub-Copilot-for-Azure.git`
    - Target: `microsoft_github-copilot-for-azure`
    - Source: `https://github.com/coreyhaines31/marketingskills.git`
    - Target: `coreyhaines31_marketingskills`
    - Source: `https://github.com/obra/superpowers.git`
    - Target: `obra_superpowers`

***

## 3. Implementation Workflow (Zero Omission)

When a repository URL is provided, follow these steps exactly:

### 3.1 Initial Addition

> [!IMPORTANT]
> **Industrial Mandate**: Submodules MUST be added and initialized **one by one**. Do NOT chain multiple additions in a single command. This ensures atomic failure detection and prevents configuration corruption.

```bash
# Add the submodule at the derived path
git submodule add <URL> <OWNER_REPO_PATH>
```

- **Pedagogical Breakdown**:
    - `add`: Registers the new submodule in `.gitmodules`.
    - `<URL>`: The source repository.
    - `<OWNER_REPO_PATH>`: The target directory (e.g., `owner_repo`).

### 3.2 Initialization & Synchronization

```bash
# Initialize the submodule and fetch data
git submodule update --init --recursive
```

- **Pedagogical Breakdown**:
    - `--init`: Initializes the submodule in `.git/config` if not already present.
    - `--recursive`: Ensures nested submodules (if any) are also handled.

### 3.3 Branch Tracking Enforcement (Critical)

Per `git-submodule-rules.md`, the agent MUST NOT leave the submodule in a "detached HEAD" state.

1. **Enter the Submodule**: `cd <OWNER_REPO_PATH>`
2. **Identify Default Branch**: Run `git remote show origin | grep "HEAD branch" | cut -d ":" -f 2 | xargs` or assume `main`/`master` based on inspection.
3. **Checkout Branch**:

    ```bash
    git checkout main # or master, based on discovery
    git pull origin main
    ```

4. **Return to Root**: `cd ..`

***

## 4. Verification & Commit Preparation

1. **Verify Status**: Run `git status` to confirm the addition and pointer change.
2. **Propose Commit**: Follow the atomic commit standard.
    - Message: `feat(submodule): add <OWNER_REPO_PATH> submodule`
    - Include: URL and purpose.

***

## 5. Migration & Standardization Protocol

When standardizing an existing submodule to the current naming convention, the agent MUST perform the following steps **atomically for each submodule**:

1. **Identify URL**: Retrieve the repository URL from `.gitmodules`.
2. **Pure Removal**:
    ```bash
    git rm <OLD_PATH>
    git config --remove-section submodule.<OLD_PATH>
    rm -rf .git/modules/<OLD_PATH>
    ```
3. **Re-Addition**:
    - Derive `<NEW_PATH>` per Section 2.
    - `git submodule add <URL> <NEW_PATH>`
4. **Synchronization**: `git submodule update --init --recursive <NEW_PATH>`

***

## 6. Traceability & Related Protocols

- **Parent Rules**: `ai-agent-rules/git-submodule-rules.md`
- **Naming Standard**: `ai-agent-rules/underscore-naming-rules.md` (if applicable) or `Underscore Naming Convention` skill.
- **Session Log**: Document the addition in `docs/conversations/` if requested.
