---
name: github-workflow-creation
description: Protocol for creating CI/CD workflows with atomic script separation,
    access control, and optimized deployment patterns.
category: CI/CD & DevOps
---

# GitHub Workflow Creation Skill

> **Skill ID:** `github-workflow-creation`
> **Version:** 1.1.0
> **Standard:** [Agent Skills (agentskills.io)](https://agentskills.io)

## Description

Automates creation of GitHub Actions workflows following industrial standards:
workflow organization, script separation, access control, checkout optimization,
and deployment via rsync/sshpass.

***

## 1. Workflow Organization

### 1.1 Directory Structure

Workflow files MUST be placed in `.github/workflows/` root for GitHub discovery.
Nested directories (e.g., `.github/workflows/deploy/`) are sometimes ignored by
GitHub Actions.

```text
.github/workflows/
  production.yml          # Target-specific workflow file
  staging.yml             # Future environments
  deploy-azure.yml        # Other deployment targets
  scripts/                # Shared scripts across workflows
    check-user.bash
    ...
```

### 1.2 File Naming

- Use environment/purpose names: `production.yml`, `staging.yml`, `ci.yml`
- Avoid generic names like `main.yml` when multiple workflows exist

***

## 2. Script Separation Mandate

### 2.1 No Inline Scripts

ALL shell logic MUST be extracted to separate `.bash` files under
`.github/workflows/scripts/`. Inline `run:` blocks are BLOCKED except for
single-line commands like `npm ci`.

### 2.2 Script Design

Each script MUST:
- Accept parameters via command-line arguments or environment variables
- NOT hardcode values like usernames, hosts, or paths
- Use `$GITHUB_ACTOR` for user context (built-in environment variable)
- Validate required arguments before execution
- Output `::error::` prefixed messages for GitHub Actions error reporting

### 2.3 Script Naming

- Use descriptive names: `check-user.bash`, `deploy-via-rsync.bash`
- Prefix with action verb: `check-`, `verify-`, `deploy-`, `install-`

***

## 3. Access Control

### 3.1 User Restriction

Workflows can be restricted to specific users:

```yaml
- name: Check Deploy Permission
  env:
    ALLOWED_USER: baneeishaque-ompventure
  run: bash .github/workflows/scripts/check-user.bash $ALLOWED_USER
```

### 3.2 Check Script Pattern

```bash
#!/bin/bash

ALLOWED="$1"

if [[ -z "$ALLOWED" ]]; then
  echo "::error::Allowed user argument is required."
  exit 1
fi

if [[ "$GITHUB_ACTOR" != "$ALLOWED" ]]; then
  echo "::error::Only authorized personnel can trigger this deployment. Current user: $GITHUB_ACTOR"
  exit 1
fi

echo "User check passed: $GITHUB_ACTOR"
```

***

## 4. Checkout Optimization

### 4.1 Production Branch Targeting

When building from a specific branch (e.g., production):

```yaml
- name: Checkout Production Branch
  uses: actions/checkout@v6.0.2
  with:
    ref: production
    fetch-depth: 1
    lfs: false
    persist-credentials: false
```

### 4.2 Flag Explanation

| Flag | Purpose |
|------|---------|
| `ref` | Target branch to checkout |
| `fetch-depth: 1` | Only fetch last commit (speed optimization) |
| `lfs: false` | Skip Git LFS objects if not used |
| `persist-credentials: false` | Skip credential setup when no git ops follow |

### 4.3 Version Pinning

ALWAYS use full version tags (e.g., `@v6.0.2`, not `@v6`) for reproducibility.

***

## 5. Build Configuration

### 5.1 Node.js Setup

Match the project's `mise.toml` or `.nvmrc` for version consistency:

```yaml
- name: Setup Node.js
  uses: actions/setup-node@v4
  with:
    node-version: "18.20.8"
    cache: "npm"
```

### 5.2 CI Mode Control

GitHub Actions automatically sets `CI=true`, which causes `react-scripts` to
treat ESLint warnings as fatal errors. For existing codebases with warnings:

```yaml
- name: Build Project
  env:
    CI: "false"
  run: npm run build
```

**When to use:**
- `CI: "false"` — Codebase has existing warnings that shouldn't block deployment
- Omit or `CI: "true"` — Fresh projects where zero warnings are enforced

### 5.3 Memory Management

Large React/Node projects require increased heap allocation:

```yaml
- name: Build Project
  env:
    NODE_OPTIONS: "--max-old-space-size=4096"
    CI: "false"
  run: npm run build
```

**Common combination:** Both `CI` and `NODE_OPTIONS` are typically needed together.

### 5.4 Dependency Installation

Use `npm ci` for deterministic, CI-optimized installs (reads only `package-lock.json`).

***

## 6. Deployment Patterns

### 6.1 Rsync via SSH Pass

For password-based SSH deployments:

```yaml
- name: Check SSH Pass
  run: bash .github/workflows/scripts/check-sshpass.bash

- name: Verify Runner Rsync
  run: bash .github/workflows/scripts/verify-runner-rsync.bash

- name: Verify Server Rsync
  env:
    VPS_PASSWORD: ${{ secrets.VPS_PASSWORD }}
    VPS_HOST: ${{ secrets.VPS_HOST }}
    VPS_USER: ${{ secrets.VPS_USER }}
  run: bash .github/workflows/scripts/verify-server-rsync.bash

- name: Deploy Static Build To Server
  env:
    VPS_PASSWORD: ${{ secrets.VPS_PASSWORD }}
    SOURCE: "build/"
    DEST: "${{ secrets.VPS_USER }}@${{ secrets.VPS_HOST }}:/var/www/acers/build/"
  run: bash .github/workflows/scripts/deploy-via-rsync.bash
```

### 6.2 Delta Sync Benefits

`rsync` only transfers changed files, unlike SCP which sends everything.
The `--delete` flag removes stale files from the target.

***

## 7. Step Naming Standards

All step names MUST use Title Case (capitalize first letter of each word):

- ✅ `Checkout Production Branch`
- ✅ `Check Deploy Permission`
- ✅ `Deploy Static Build To Server`
- ❌ `checkout production branch`
- ❌ `Check deploy permission`

***

## 8. Trigger Types

### 8.1 Manual Dispatch

For controlled deployments:

```yaml
on:
  workflow_dispatch:
```

### 8.2 Push Trigger

For automatic CI:

```yaml
on:
  push:
    branches: [main]
```

***

## 9. Runner Selection

### 9.1 Explicit Version

Use explicit OS versions instead of `latest`:

```yaml
runs-on: ubuntu-24.04
```

### 9.2 Available Runners

| Runner | Status |
|--------|--------|
| `ubuntu-24.04` | Current LTS |
| `ubuntu-22.04` | Legacy support |
| `ubuntu-latest` | Avoid (changes over time) |

***

## 10. Common Pitfalls

| Pitfall | Solution |
|---------|----------|
| Workflow not discovered by GitHub | Place `.yml` in `.github/workflows/` root, not subdirectories |
| Build fails with heap OOM | Add `NODE_OPTIONS: --max-old-space-size=4096` |
| Build fails with ESLint warnings as errors | Add `CI: "false"` to build step environment |
| SCP transfers all files every time | Use `rsync` with `--delete` for delta sync |
| Hardcoded values in scripts | Pass via arguments or environment variables |
| Using `@v6` instead of `@v6.0.2` | Always pin to full version for reproducibility |
| Inline scripts in workflow YAML | Extract to `.bash` files in `scripts/` folder |
