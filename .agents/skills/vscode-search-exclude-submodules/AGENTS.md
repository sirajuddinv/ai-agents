---
name: VS Code Search Exclude Submodules
description: Bridge document linking to the composer skill that excludes every Git submodule from a VS Code Search-view query, by reusing the base Search-Exclude-Glob skill.
category: VSCode-Configuration
---

# VS Code Search Exclude Submodules (AGENTS.md)

This document is a passive companion to the active skill at [`./SKILL.md`](./SKILL.md).

**Skill Name**: VS Code Search Exclude Submodules

**Purpose**: Composer skill — extract submodule paths from the parent repo's
`.gitmodules`, hand them to the base
[VS Code Search Exclude Glob](../vscode-search-exclude-glob/SKILL.md) skill, and emit a
single brace-glob the user pastes into the Search view's **"files to exclude"** input.
No `settings.json` edits. Session-only.

**For Implementation Details**: Refer to [`./SKILL.md`](./SKILL.md) — the SSOT.

***

## Quick Reference

### Use Case

A monorepo or "umbrella" repo aggregates many Git submodules at its root. Repository-wide
searches in VS Code walk into every submodule by default, drowning out parent-repo
results. The user wants a **session-only** exclusion limited to exactly the submodules
listed in `.gitmodules`.

### Core Solution

```powershell
pwsh-preview -NoProfile -File .agents/skills/vscode-search-exclude-submodules/scripts/generate_submodule_exclude_glob.ps1
```

Falls back to `pwsh` when `pwsh-preview` is unavailable. Cross-compatible with Windows
PowerShell 5.1+ and PowerShell Core 7+.

Paste the printed line into the Search view's **"files to exclude"** input.

### Layer Diagram

```text
+-------------------------------------------------+
| vscode-search-exclude-submodules  (composer)    |
|   parses .gitmodules → list of submodule paths  |
+----------------------+--------------------------+
                       | pipes path list to
                       v
+-------------------------------------------------+
| vscode-search-exclude-glob       (base)         |
|   normalize → sort → dedupe → brace-glob        |
+-------------------------------------------------+
```

### Why Not `search.exclude` in `settings.json`?

| Approach | Persistence | Editor Footprint | Best For |
| :--- | :--- | :--- | :--- |
| `search.exclude` in `.vscode/settings.json` | Persistent, committed | Modifies repo | Team-wide, permanent rule |
| `search.exclude` in user/profile settings | Persistent, local | Modifies user config | Personal default across repos |
| Search-view "files to exclude" (this skill) | Session-only, ad-hoc | Zero file edits | One-off audits, exploratory searches |

***

## Quick Start

1. `cd` into the parent repository root (the one with `.gitmodules`).
2. Run the composer script (see Core Solution above).
3. Open the Search view (`Cmd+Shift+F` / `Ctrl+Shift+F`), expand the "…" toggle, and
   paste into **"files to exclude"**.
4. Run your search.
