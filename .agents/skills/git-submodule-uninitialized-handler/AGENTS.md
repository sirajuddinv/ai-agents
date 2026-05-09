# AGENTS.md (Ref)

This directory hosts the **Git Submodule Uninitialized Handler** skill — the remediation half of the audit/handler
pair. It consumes the report from
[Git Submodule Uninitialized Audit](../git-submodule-uninitialized-audit/SKILL.md) and drives every pointer to a
fully-initialized state via init, orphan recovery, fork re-pointing, or (gated) removal.

For the full active instructions, see [SKILL.md](./SKILL.md).

## Composition

This is a **remediation composer** that orchestrates:

- [Git Submodule Uninitialized Audit](../git-submodule-uninitialized-audit/SKILL.md) — consumed input.
- [Git Submodule Orphan Gitlink Recovery](../git-submodule-orphan-gitlink-recovery/SKILL.md) — Phase 2 delegate.
- [Git Submodule Fork Reconfigure](../git-submodule-fork-reconfigure/SKILL.md) — Phase 3 delegate.
- [Git Submodule Removal](../git-submodule-removal/SKILL.md) — last-resort delegate, requires user approval.

Inlining any of the above primitives is **FORBIDDEN** by the Layered Composition Mandate.
