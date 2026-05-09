---
name: VS Code Search Exclude Glob
description: Bridge document linking to the base skill that converts any path list into a Search-view "files to exclude" brace-glob.
category: VSCode-Configuration
---

# VS Code Search Exclude Glob (AGENTS.md)

This document is a passive companion to the active skill at [`./SKILL.md`](./SKILL.md).

**Skill Name**: VS Code Search Exclude Glob

**Purpose**: Base primitive — turn a newline-separated list of repository-relative paths
into one brace-glob (`{a,b,c}/**`) suitable for the VS Code Search view's
**"files to exclude"** input. No persistent settings are modified; the result is a
session-only filter the user pastes into the Search UI.

**For Implementation Details**: Refer to [`./SKILL.md`](./SKILL.md) — the SSOT.

***

## Quick Reference

### Use Case

You (or another skill) have a list of paths to exclude from a one-off VS Code search,
and you want a clean, deterministic brace-glob without hand-writing it or touching
`settings.json`.

### Core Solution

```powershell
@('dir_a','dir_b','dir_c') |
    pwsh-preview -NoProfile -File .agents/skills/vscode-search-exclude-glob/scripts/generate_exclude_glob.ps1
# → {dir_a,dir_b,dir_c}/**
```

Fallback to `pwsh` if `pwsh-preview` is not on the system. Both Windows PowerShell 5.1+
and PowerShell Core 7+ are supported.

### Composition

This skill is intentionally generic. Higher-level skills (e.g.
[VS Code Search Exclude Submodules](../vscode-search-exclude-submodules/SKILL.md)) feed
their domain-specific path discovery into it.
