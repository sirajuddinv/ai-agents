# Git Divergence Audit Bridge (v1)

This document provides the "passive context" for AI agents to identify and execute the [Git Divergence Audit Skill](./SKILL.md).

## Usage & Routing

When the user asks to compare branches, reconcile divergence, or perform a manual audit of local vs. remote histories:

1. **Routing**: Immediately route the execution logic to the [SKILL.md](./SKILL.md).
2. **Standard**: Adhere to the **Ultra-Lean Industrial** standards for Git operations.
3. **Tooling**: Prioritize the `./scripts/audit.ps1` industrial script for discovery.

## Contextual Integration

- **Git Repositories**: This skill is applicable to any Git-managed workspace.
- **Submodules**: Can be used to audit divergence in submodules (e.g., `ai-agents` vs `origin/main`).
- **Industrial Compliance**: Follows Rule 1.1 (tilde-portable) and Rule 4.2.9 (Redaction/PII Neutralization).

***

## Skill Registration (AGENTS.md SSOT)

| Skill | Path | Description |
| :--- | :--- | :--- |
| Git Divergence Audit | [`.agents/skills/git_divergence_audit/SKILL.md`](./SKILL.md) | Industrial comparison of diverged branches with CAM table generation. |
