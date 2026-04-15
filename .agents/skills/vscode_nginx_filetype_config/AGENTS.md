---
name: VSCode NGINX File Type Configuration
description: Bridge document linking to the VSCode NGINX file type configuration skill for multi-tier setup including code-workspace files.
category: VSCode-Configuration
---

# VSCode NGINX File Type Configuration (AGENTS.md)

This document serves as a companion bridge to the active skill at `./SKILL.md`.

**Skill Name**: VSCode NGINX File Type Configuration

**Purpose**: Automatically configure VSCode to recognize all files within a project's `nginx/` directory as NGINX language type across four configuration tiers: application (user-wide), profile (profile-specific), workspace (project-level), and code-workspace (multi-root workspace files).

**For Implementation Details**: Refer to [`./SKILL.md`](./SKILL.md) — the Single Source of Truth (SSOT) for this skill.

***

## Quick Reference

### Use Case

You have a repository with an `nginx/` directory containing NGINX configuration files without standard extensions. VSCode cannot automatically identify these as NGINX files, resulting in lack of syntax highlighting.

You want to configure this at one or more of these levels:
- **Workspace** (project-specific, shared with team)
- **Code-Workspace** (multi-root workspace file, shared with team)
- **Profile** (profile-specific, personal to your workflow)
- **Application** (user-wide, affects all VSCode projects)

### Core Solution

Add the NGINX file association glob pattern to `settings.json` at your chosen tier:

```json
{
  "files.associations": {
    "nginx/**": "nginx"
  }
}
```

Or in `.code-workspace` files, add it to the `settings` key:

```json
{
  "folders": [...],
  "settings": {
    "files.associations": {
      "nginx/**": "nginx"
    }
  }
}
```

### Configuration Tiers

| Tier | Location | Scope | Persistence | Priority |
|------|----------|-------|-------------|----------|
| **Code-Workspace** | `*.code-workspace` | Multi-root workspace | Committed to repo | 1 (highest) |
| **Workspace** | `.vscode/settings.json` | Project-specific | Committed to repo | 2 |
| **Profile** | `~/Library/.../profiles/<name>/settings.json` | Profile-specific | Local only | 3 |
| **Application** | `~/Library/.../Code/User/settings.json` | User-wide | All VSCode instances | 4 (lowest) |

### Key Features

- **4-Tier Configuration**: Application, profile, workspace, or code-workspace
- **Atomic Merging**: Preserves existing settings; no overwrites
- **Cross-platform**: Supports macOS, Linux, Windows with automatic OS detection
- **Multi-Root Workspaces**: Direct support for `.code-workspace` files
- **Glob Pattern Matching**: `nginx/**` matches all files and subdirectories
- **Syntax Highlighting**: Enables automatic highlighting for all NGINX configuration files
- **Code Intelligence**: Integrates with VSCode NGINX extensions
- **Portable Workspace Config**: Configuration committed to repo for team-wide benefit

***

## Quick Start

### For Workspace Configuration (Recommended for Single-Root Projects)

```bash
python3 ./scripts/vscode-nginx-config.py --workspace-root /path/to/project
```

Then commit `.vscode/settings.json` to your repository.

### For Code-Workspace Configuration (Recommended for Multi-Root Projects)

```bash
python3 ./scripts/vscode-nginx-config.py --tier code-workspace --workspace-file myproject.code-workspace
```

Then commit `*.code-workspace` file to your repository.

### For Application Configuration (User-wide)

```bash
python3 ./scripts/vscode-nginx-config.py --tier application
```

All future VSCode projects will recognize `nginx/` files.

### For Profile Configuration (Profile-specific)

```bash
python3 ./scripts/vscode-nginx-config.py --tier profile --profile-name my-profile
```

### Preview Changes Before Applying

```bash
python3 ./scripts/vscode-nginx-config.py --tier workspace --dry-run
```

***

## Configuration Hierarchy (Priority Order)

When multiple tiers define the same setting:

1. **Code-Workspace** (highest) — Multi-root workspace overrides everything
2. **Workspace** — Project-specific `.vscode/settings.json`
3. **Profile** — Active profile overrides application
4. **Application** (lowest) — User-wide defaults

***

## For Detailed Implementation

Including environment checks, verification protocols, multi-tier merging strategies, edge case handling, and `.code-workspace` specifics:

**→ See [`./SKILL.md`](./SKILL.md)**

***

## Related Documentation

- **VSCode File Associations**: https://code.visualstudio.com/docs/languages/identifiers
- **VSCode Settings Tiers**: https://code.visualstudio.com/docs/getstarted/settings
- **VSCode Workspaces**: https://code.visualstudio.com/docs/editor/workspaces
- **NGINX Language Support**: Built-in VSCode support; enhanced with [NGINX IntelliSense](https://marketplace.visualstudio.com/items?itemName=hangxingliu.vscode-nginx-conf)
- **Standardization Rules**: Follow [ai-rule-standardization-rules.md](../../../../ai-agent-rules/ai-rule-standardization-rules.md) for skill architecture

