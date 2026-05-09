# AGENTS.md (Ref)

This directory hosts the **Git Submodule Uninitialized Audit** skill — a strictly read-only, recursive enumeration
of every submodule pointer (top-level + nested + orphan), with HTTP reachability probing and a deterministic
classified report.

For the full active instructions, see [SKILL.md](./SKILL.md).

## Composition

This is a **diagnostic composer** that delegates dead-upstream investigation to:

- [Git Submodule Dead Upstream Audit](../git-submodule-dead-upstream-audit/SKILL.md) — SHA-based fork/mirror search.

Inlining that primitive is **FORBIDDEN** by the Layered Composition Mandate. Remediation work belongs to the
sibling consumer skill [Git Submodule Uninitialized Handler](../git-submodule-uninitialized-handler/SKILL.md).
