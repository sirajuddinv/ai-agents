<!--
title: Git Repository Initialization
description: Initialize a new Git repository with optional Git LFS setup,
    file tracking, and atomic initial commits — following the full
    atomic commit construction protocol.
category: Git & Repository Management
-->

# Git Repository Initialization Skill

> **Skill ID:** `git_repo_initialization`
> **Version:** 1.0.0
> **Standard:** [Agent Skills (agentskills.io)](https://agentskills.io)

## Description

Initialize a new Git repository from an existing directory of files.
This skill covers the full lifecycle: environment validation, `git init`,
optional Git LFS setup with file-type tracking, deep change analysis of
all pre-existing files, atomic commit construction, and post-commit
verification.

When Git LFS is requested, the `.gitattributes` foundation is always
committed **before** the LFS-tracked binary assets to ensure the LFS
filter is active in history before any large files are stored. This
prevents binaries from being committed as regular blobs.

The skill delegates to the
[`git_atomic_commit`](../git_atomic_commit/SKILL.md) skill for all
commit construction, preview, and authorization protocols. The user
retains full control via mandatory preview and explicit "start"
authorization.

## Source Rules

This skill operationalizes the following rule files:

| Rule File | Scope Incorporated |
|---|---|
| [`git-atomic-commit-construction-rules.md`](../../../ai-agent-rules/git-atomic-commit-construction-rules.md) | Phases 1–2, 5, 8–9 (change analysis, grouping, config coupling, message quality, execution) |
| [`git-operation-rules.md`](../../../ai-agent-rules/git-operation-rules.md) | Phase 0 (environment and repository context) |

## Prerequisites

| Requirement | Minimum |
|---|---|
| VCS | Git 2.x+ |
| Git LFS | Git LFS 3.x+ (only when LFS tracking is requested) |
| Shell | PowerShell 5.1+ or Bash 4+ |
| Access | Write access to the target directory |

## When to Apply

Apply this skill when:
- A user asks to "initialize a repo," "git init," or "set up a new
  repository" from an existing directory
- A user asks to set up Git LFS tracking for specific file types in a
  new repository
- A directory contains files that need to be brought under version
  control for the first time
- Multiple repositories need to be initialized in a single session

Do NOT apply when:
- The directory is already a Git repository — use
  [`git_atomic_commit`](../git_atomic_commit/SKILL.md) for committing
  existing changes instead
- The user asks to clone an existing remote repository — that is
  `git clone`, not initialization
- The user asks to add LFS tracking to an **existing** repository with
  history — that requires `git lfs migrate` and is out of scope

---

## Step-by-Step Procedure

### Step 1 — Environment Verification

Validate that required tools are available before any operations.

#### 1a — Verify Git Installation

```powershell
git --version
```

> `--version` — prints the installed Git version. If the command fails,
> Git is not installed or not on `PATH`.

#### 1b — Verify Git LFS Installation (Conditional)

Only when Git LFS is requested:

```powershell
git lfs version
```

> `lfs version` — prints the installed Git LFS version. If this fails,
> instruct the user to install Git LFS via their package manager
> (`winget install Git.LFS`, `brew install git-lfs`, `apt install
> git-lfs`).

#### 1c — Inspect Target Directory

List the directory contents to understand what pre-existing files will
become candidates for version control:

```powershell
Get-ChildItem -Path <target-dir>
```

**Bash:**

```bash
ls -la <target-dir>
```

Categorize each file by type (source code, binary, config, data,
documentation) to inform the commit grouping in Step 4.

---

### Step 2 — Initialize the Repository

#### 2a — Run `git init`

```powershell
cd <target-dir>
git init
```

> `git init` — creates a new `.git/` directory, establishing the
> directory as a Git repository with an empty commit history on the
> default branch.

#### 2b — Verify Initialization

```powershell
git status
```

Confirm the output shows "No commits yet" and lists all pre-existing
files as untracked.

---

### Step 3 — Git LFS Setup (Conditional)

Skip this step entirely if Git LFS is not requested.

#### 3a — Install LFS Hooks

```powershell
git lfs install
```

> `git lfs install` — configures Git hooks (`pre-push`, `post-checkout`,
> `post-commit`, `post-merge`) in the repository to intercept LFS-tracked
> files during push/pull operations. This is a **per-repository** setup
> that must run after `git init`.

#### 3b — Track File Types

For each file extension requested by the user:

```powershell
git lfs track "*.<ext>"
```

> `git lfs track` — appends a pattern line to `.gitattributes` with
> `filter=lfs diff=lfs merge=lfs -text`, instructing Git to route
> matching files through the LFS filter instead of storing them as
> regular blobs.

**Example — tracking `.7z` archives:**

```powershell
git lfs track "*.7z"
```

This produces the following `.gitattributes` entry:

```gitattributes
*.7z filter=lfs diff=lfs merge=lfs -text
```

#### 3c — Verify `.gitattributes`

```powershell
Get-Content .gitattributes
```

Confirm the tracking rules are correctly written. Each tracked
extension should appear as a separate line with the full LFS filter
specification.

---

### Step 4 — Deep Change Analysis

Perform the full change analysis protocol per the
[`git_atomic_commit`](../git_atomic_commit/SKILL.md) skill (Step 1).

#### 4a — Inventory All Files

```powershell
git status
```

Every file in the directory is untracked at this point. List ALL files
with their categories:

| # | File | Category | Notes |
|---|---|---|---|
| 1 | `.gitattributes` | Infrastructure | LFS tracking rules |
| 2 | `data.7z` | Data (LFS) | Binary archive |
| 3 | `README.md` | Documentation | Project readme |

#### 4b — Analyze Cross-File Dependencies

Identify ordering constraints:

- **LFS Foundation Rule (Critical):** `.gitattributes` MUST be committed
  **before** any LFS-tracked files. Without the LFS filter active in
  history, Git stores binaries as regular blobs, defeating the purpose
  of LFS. This is a hard ordering dependency, not a preference.
- **Configuration Coupling:** If a `.gitignore` exists alongside config
  files it governs, they may be coupled per Phase 5 of the atomic commit
  rules.
- **Functional Grouping:** Files serving the same architectural purpose
  (e.g., all workspace definitions, all source files for a module) should
  be grouped into a single commit.

---

### Step 5 — Arrange Atomic Commits

Based on the dependency analysis, propose a commit sequence.

#### 5a — Standard Arrangement for LFS Repositories

When Git LFS is configured, the minimum arrangement is:

| Order | Commit | Files | Rationale |
|---|---|---|---|
| 1 | LFS infrastructure | `.gitattributes` | Foundation — LFS filter must be active before binaries |
| 2 | Binary assets | All LFS-tracked files | Depend on Commit 1 for correct storage |
| 3+ | Remaining files | Source, docs, config | Grouped by architectural purpose |

#### 5b — Standard Arrangement for Non-LFS Repositories

When no LFS is involved, group files by architectural purpose:

| Order | Commit | Files | Rationale |
|---|---|---|---|
| 1 | Infrastructure | `.gitignore`, `.editorconfig`, etc. | Foundation configs |
| 2+ | Content files | Source, docs, data, IDE config | Grouped by function |

If all files serve the same purpose (e.g., all workspace definitions),
a single commit is appropriate.

#### 5c — Present the Commit Preview

Follow the mandatory verbose display format from the
[`git_atomic_commit`](../git_atomic_commit/SKILL.md) skill (Step 2d).

**The agent MUST NOT proceed with any commit execution until the user
explicitly says "start".**

---

### Step 6 — Execute Commits

After receiving "start" authorization from the user, execute commits
sequentially.

#### 6a — Pre-Staging Status Check

Before every staging action:

```powershell
git status
```

Verify the working tree state matches expectations.

#### 6b — Stage Files for Current Commit

```powershell
git add <file1> <file2> ...
```

Stage only the files planned for the current atomic unit.

#### 6c — Verify Staged Contents

```powershell
git diff --cached --stat
```

> `--cached` — shows only what is in the staging area (index).
> `--stat` — summarizes file-level additions/deletions without full
> patch content. Useful for confirming the correct files are staged.

Confirm that **only** the planned files appear. If unexpected files
are staged, unstage them:

```powershell
git reset <file>
```

#### 6d — Commit

```powershell
git commit -m "<title>" -m "<body>"
```

> `-m "<title>"` — the first `-m` sets the commit subject line.
> `-m "<body>"` — the second `-m` sets the commit body, separated from
> the subject by a blank line. This avoids needing an interactive editor.

#### 6e — Verify Commit

```powershell
git log --oneline -1
```

Confirm the commit hash and subject match the plan.

#### 6f — Repeat for Remaining Commits

Return to Step 6a for each subsequent commit in the arrangement.

---

### Step 7 — Post-Execution Verification

After all commits are executed, perform a final verification.

#### 7a — Clean Working Tree

```powershell
git status
```

The output MUST show `nothing to commit, working tree clean`.

#### 7b — Review Full History

```powershell
git log --oneline
```

Verify the commit sequence matches the approved arrangement — correct
order, correct messages, correct count.

#### 7c — Verify LFS Tracking (Conditional)

If LFS was configured:

```powershell
git lfs ls-files
```

> `git lfs ls-files` — lists all files currently tracked by Git LFS in
> the repository. Each entry shows the LFS OID and filename. If
> LFS-tracked files do not appear here, the `.gitattributes` was not
> committed before the binary files or the LFS filter is misconfigured.

---

## Scope Coverage

| Capability | Covered |
|---|---|
| `git init` | ✅ |
| `git lfs install` | ✅ (conditional) |
| `git lfs track` | ✅ (conditional) |
| `.gitattributes` ordering | ✅ |
| Multi-repo batch initialization | ✅ |
| Atomic commit construction | ✅ (delegates to `git_atomic_commit`) |
| Commit preview and authorization | ✅ |
| Post-commit verification | ✅ |
| `git lfs migrate` (rewriting history) | ❌ Out of scope |
| `git clone` | ❌ Out of scope |
| Remote setup (`git remote add`) | ❌ Out of scope |

## Prohibited Behaviors

- **MUST NOT** commit LFS-tracked files before `.gitattributes` is
  committed — this causes binaries to be stored as regular blobs
- **MUST NOT** auto-commit without presenting the Arranged Commits
  Preview and receiving explicit "start" from the user
- **MUST NOT** stage untracked files without explicit user confirmation,
  especially in repositories with minimal or default `.gitignore`
- **MUST NOT** chain Git commands with `&&` — each command must be
  executed and verified independently
- **MUST NOT** run `git lfs install` before `git init` — the repository
  must exist first
- **MUST NOT** skip the post-execution verification (clean working tree
  and history review)

## Common Pitfalls

| Pitfall | Cause | Solution |
|---|---|---|
| LFS files stored as regular blobs | `.gitattributes` committed after or alongside binary files | Always commit `.gitattributes` as the first commit |
| `git lfs install` fails | Repository not yet initialized | Run `git init` before `git lfs install` |
| Credentials committed | No `.gitignore` and untracked files auto-staged | Confirm every untracked file with the user before staging |
| LFS hooks not active | `git lfs install` skipped or run outside the repo | Run `git lfs install` inside the initialized repo directory |
| Binary files not in `git lfs ls-files` | Tracking rule added after file was committed | Commit `.gitattributes` first, then add the files |
