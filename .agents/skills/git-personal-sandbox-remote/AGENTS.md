# Git Personal Sandbox Remote — Agent Bridge

This is the passive context bridge for the
[`git-personal-sandbox-remote`](./SKILL.md) skill.

## When to engage

The user has files in a team-repo clone that:

- need version control + remote backup, AND
- must NOT reach the team's `origin` (build configs, IDE artifacts the team
  rejected, sandbox patches), AND
- should NOT appear as a **fork** in the team upstream's fork network.

## What this skill does

Provisions an independent personal repository (not a fork) on the same GitHub
host as `origin`, registers it as the `personal` remote, and pushes a
`personal/<purpose>` branch to it — without ever touching `origin`.

## Active SSOT

All operational instructions live in [`SKILL.md`](./SKILL.md). This file
provides discovery context only — defer to `SKILL.md` for every command,
decision matrix, and failure-mode resolution.

## Composes

- [`github-rest-api-fallback`](../github-rest-api-fallback/SKILL.md) — for
  creating / deleting the personal repo via REST when `gh` is unavailable
- [`git-github-auth-fallback`](../git-github-auth-fallback/SKILL.md) §3.2.1 —
  for the push-without-`-u` two-step pattern that avoids leaking PATs into
  branch tracking config
- [`git-atomic-commit-construction`](../git-atomic-commit-construction/SKILL.md)
  — for the commit on the personal branch
