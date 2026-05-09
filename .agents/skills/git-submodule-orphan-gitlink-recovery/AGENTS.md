# AGENTS.md (Ref)

This directory hosts the **Git Submodule Orphan Gitlink Recovery** skill — an industrial protocol for repairing
submodule pointers that exist in a Git tree (mode `160000`) but are missing from `.gitmodules`, by SHA-based
upstream discovery, optional fork reconfiguration, selective registration, and explicit drop of unrecoverable
pointers.

For the full active instructions, see [SKILL.md](./SKILL.md).

## Composition

This skill is a **domain composer** built on two base primitives:

- [Git Submodule Dead Upstream Audit](../git-submodule-dead-upstream-audit/SKILL.md) — SHA-to-repo search.
- [Git Submodule Fork Reconfigure](../git-submodule-fork-reconfigure/SKILL.md) — fork + remote swap.

Inlining either primitive is **FORBIDDEN** by the Layered Composition Mandate.
