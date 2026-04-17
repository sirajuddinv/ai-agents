---
name: Git Feature Branch Atomic Commit
description: Create atomic commits on separate feature branches with
    isolated branch-per-commit workflow for pull request preparation.
category: Git & Repository Management
---

# Git Feature Branch Atomic Commit Skill

> **Skill ID:** `git_feature_branch_atomic_commit`
> **Version:** 1.0.0
> **Standard:** [Agent Skills (agentskills.io)](https://agentskills.io)

## Description

Create atomic commits on separate feature branches using an isolated
branch-per-commit workflow. Each change gets its own branch, commit,
and optional PR preparation.

This skill extends the [`git_atomic_commit`](../git_atomic_commit/SKILL.md)
skill by adding multi-branch creation, branch naming, and push protocols.

## Source Rules

This skill distills and operationalizes:

| Rule File | Scope Incorporated |
| :--- | :--- |
| [`git-atomic-commit-construction-rules.md`](../../../ai-agent-rules/git-atomic-commit-construction-rules.md) | All 15 phases (primary source) |
| [`git-operation-rules.md`](../../../ai-agent-rules/git-operation-rules.md) | Environment, repo context, push protocols |
| [`skill_factory`](../skill_factory/SKILL.md) | Skill creation patterns |
| [`markdown_generation`](../markdown_generation/SKILL.md) | Artifact lint verification via `markdownlint-cli2` CLI |

## Prerequisites

| Requirement | Minimum |
| :--- | :--- |
| VCS | Git 2.x+ |
| Shell | PowerShell 5.1+ or Bash 4+ |
| Access | Write access to the project repository |
| Auth | GitHub CLI authenticated (if pushing to GitHub) |

## When to Apply

Apply this skill when:

- User asks to commit changes to multiple feature branches
- Changes require isolated commits on separate branches
- Each atomic change needs its own branch for PR
- Branch-per-commit isolation is requested

Do NOT apply when:

- Single commit on single branch is sufficient
- User wants commits on existing branches (use `git_atomic_commit`)
- Existing commits need refinement (use `git_history_refinement`)

---

## Step-by-Step Procedure

### Step 1 — Deep Change Analysis

Follow [Step 1 from git_atomic_commit](../git_atomic_commit/SKILL.md#step-1-deep-change-analysis):

- Detect ALL staged, unstaged, and untracked changes
- Analyze dependencies and cross-file references
- Present complete inventory to user

### Step 2 — Logical Grouping (Arrangement)

Follow [Step 2 from git_atomic_commit](../git_atomic_commit/SKILL.md#step-2-logical-grouping-arrangement):

- Arrange changes into independent, atomic commits
- Each commit MUST be able to stand alone on its own branch

### Step 3 — Branch Naming Protocol

For each atomic commit, derive a feature branch name:

#### 3.1 Branch Name Pattern

```text
<prefix>/<scope>_<impact>
```

| Component | Description |
| :--- | :--- |
| `<prefix>` | User-provided prefix (e.g., `banee/`, `feature/`) |
| `<scope>` | Affected area or component (e.g., `ice-client`, `vscode`) |
| `<impact>` | Change type or purpose (e.g., `relative-paths`, `spell-check`) |

#### 3.2 Naming Rules

- Use lowercase, kebab-case for words
- Omit commit type prefix (e.g., `config:`, `docs:`) from branch name
- Use descriptive nouns/adjectives, not verbs
- Keep branch name under 50 characters

#### 3.3 User Confirmation for Branch Names

Present proposed branch names alongside commit preview:

````markdown
## Arranged Commits Preview

### Commit 1: config: use relative paths in ICE client configuration
- **Branch**: `banee/ice-client-relative-paths`
- **Files**: `acers/apps/paper_app/APITrades/ICE/client.cfg`
- **Message**: ...
### Commit 2: config: add VS Code spell check words
- **Branch**: `banee/vscode-spell-check`
- **Files**: `.vscode/settings.json`
- **Message**: ...
---
Please say "start" to create branches and commit each change atomically.
````

---

### Step 4 — Interactive Hunk-Based Staging (If Needed)

Follow [Step 3 from git_atomic_commit](../git_atomic_commit/SKILL.md#step-3-interactive-hunk-based-staging):

- Use `git add -p <file>` for mixed concerns
- Evaluate each hunk individually
- Verify with `git diff --cached`

---

### Step 5 — Execution Protocol

Execute commits one-by-one with branch isolation:

#### 5.1 For Each Commit

1. **Create Branch**:

   ```bash
   git -C /repo checkout -b <branch-name>
   ```

2. **Stage**:

   ```bash
   git -C /repo add <file>
   ```

3. **Commit**:

   ```bash
   git -C /repo commit -m "<conventional-message>
   
   <detailed-body>"
   ```

4. **Return to Original Branch**:

   ```bash
   git -C /repo checkout <original-branch>
   ```

#### 5.2 Repeat for Each Commit

Execute steps 5.1.1–5.1.4 for EACH atomic commit, creating a new branch from the base branch each time.

---

### Step 6 — Push Protocol

After all commits are complete:

#### 6.1 Offer, Don't Execute

- Do NOT push without explicit user request
- Present summary of created branches
- Wait for explicit "yes" or "push" command

#### 6.2 Multi-Branch Push

For simultaneous push of multiple branches:

```bash
git -C /repo push -u origin branch1 branch2 branch3
```

Or push each individually:

```bash
git -C /repo push -u origin <branch-name>
```

---

### Step 7 — Post-Commit Verification

After execution:

1. **Verify Clean State**:

   ```bash
   git -C /repo status
   ```

2. **Return to Original Branch**:

   ```bash
   git -C /repo checkout <original-branch>
   ```

3. **Summary Table**:
   Present a table of created branches and their commits:

   | Branch | Commit |
   | :--- | :--- |
   | `<prefix>/<scope>_<impact>` | `<conventional-message>` |

---

## Branch Naming Examples

| Change | Branch Name |
   | :--- | :--- |
   | `config: update nginx file association` | `banee/nginx-file-association` |
   | `docs: add venv copies flag macOS issue` | `banee/venv-macos-documentation` |
   | `scripts: add database restore script` | `banee/database-restore-script` |
   | `fix: resolve connection timeout` | `banee/connection-timeout-fix` |
   | `refactor: extract validation logic` | `banee/validation-logic-refactor` |

---

## Prohibited Behaviors

The agent is BLOCKED from:

- **Auto-pushing** — Never push without explicit user request
- **Committing to same branch** — Each atomic change MUST get its own branch
- **Skipping branch creation** — Must create new branch for each commit
- **Merging branches locally** — Feature branches are for PR preparation only
- **Using generic branch names** — Must follow `<prefix>/<scope>_<impact>` pattern
- **Skipping preview** — Branch names must be presented in preview before execution
- **Auto-committing** — Never commit without explicit "start" authorization

---

## Traceability

- **Source Conversation**: This skill was created based on the atomic commit workflow
  demonstrated in the oleovista-acers and acers-backend repositories
- **Related Skills**: [`git_atomic_commit`](../git_atomic_commit/SKILL.md), [`git_history_refinement`](../git_history_refinement/SKILL.md)
