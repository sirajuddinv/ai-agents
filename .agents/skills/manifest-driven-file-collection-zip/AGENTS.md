# manifest-driven-file-collection-zip — Companion Bridge

This directory is an **Agent Skill** following the agentskills.io protocol. The active SSOT is [SKILL.md](SKILL.md).

## Passive Context

Use this skill to collect a curated, explicitly-listed set of files from anywhere under a root
directory into a single flat, timestamped zip — driven by a plain-text manifest (one relative path
per line, `#` comments allowed). Key traits:

1. **Deterministic selection** — you list exactly the files you want; nothing is auto-discovered.
2. **Flat output** — every collected file lands at the zip root; no nesting.
3. **Safe de-dup** — same-leaf-name files are auto-suffixed `_1`, `_2`, …
4. **Zero dependencies** — runs on stock PowerShell 5.1+; droppable into any tree.

The mechanics live in [scripts/Collect-ManifestFiles.ps1](scripts/Collect-ManifestFiles.ps1).

## When NOT to use this skill

- Archiving an entire directory tree — use plain `Compress-Archive <dir>`.
- Preserving sub-directory structure inside the zip — this tool flattens by design.
- Copying files to a remote location — this tool is local-only.

## Composition

This is a **base skill**. Domain-specific collectors compose it by owning only the manifest content:

- `pver_pick_pointer` (`bosch_ai_agents`, org-private) — build-artifact collection for a build tree.

Cross-repository composers reference this base by prose path, never a relative link.
