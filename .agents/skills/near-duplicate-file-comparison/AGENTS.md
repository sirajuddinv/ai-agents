# Near-Duplicate File Comparison — Agents Bridge

This directory contains the `near-duplicate-file-comparison` skill.

The active, authoritative instructions live in [SKILL.md](SKILL.md).
This file exists only to provide passive context for agents that
auto-discover `AGENTS.md` files.

## When to Read SKILL.md

Read [SKILL.md](SKILL.md) when:

- Two files in the same directory share a base name with a suffix like
  `_old`, `_backup`, `_v1`, `_copy`, `.bak`, `_draft`, `_wip`, `_new`,
  and the user (or a build error) asks which one wins.
- The user asks to "deeply compare" two near-duplicate source files.
- A duplicate class/function declaration is suspected (compile-blocker
  risk in Java/Kotlin/C#/Go).

For broader / different scopes, see the
[Related Skills](SKILL.md#related-skills) section in `SKILL.md`.
