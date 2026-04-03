# Git Repository Status Agent Bridge

This skill provides the authoritative protocol for auditing a Git repository's status with high fidelity.

## When to Use

- Before starting any new feature or fix.
- Before performing a synchronization (rebase/pull/push).
- After a long gap in the conversation to re-sync the agent's context.

## Active Instructions

The agent **MUST** follow the diagnostic steps and reporting format in the active **[SKILL.md](./SKILL.md)**.

## Key Protocols

- **Connectivity & Context**: Verified via `git branch -vv` and `git status -u`.
- **Working Tree Audit**: Includes staged, modified, and recursive submodule checks.
- **Traceability**: Visualized through `git log --graph` and `git stash list`.
