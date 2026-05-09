# AGENTS.md — git-post-gitignore-untrack

This is the passive-context bridge for the [`git-post-gitignore-untrack`](./SKILL.md) skill.

## Purpose

Refer the agent to `SKILL.md` whenever a freshly added or expanded `.gitignore` leaves previously
tracked OS / IDE noise files (e.g. `.DS_Store`, `Thumbs.db`, `__pycache__/`) lingering in the index.

## Trigger Phrases

- "untrack `.DS_Store`"
- "the new `.gitignore` doesn't take effect"
- "residual modifications after the gitignore commit"
- "fold the untrack into the previous commit"

## Authority

`SKILL.md` in this directory is the SSOT. Do not duplicate its operational logic here.
