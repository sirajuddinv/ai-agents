# maven-build-failure-analysis — Companion Bridge

This directory is an **Agent Skill** following the agentskills.io protocol. The active SSOT is [SKILL.md](SKILL.md).

## Passive Context

Use this skill to diagnose **Maven / Tycho** (Eclipse PDE/OSGi) build failures — especially the
`Missing requirement: ... could not be found` class. The framework:

1. Parses the failing reactor output (isolate the first unsatisfied requirement).
2. Reconstructs the OSGi/p2 dependency chain.
3. Extracts and compares MANIFEST.MF headers across a known-good and a broken bundle.
4. Decodes OSGi `Bundle-Version` qualifier timestamps to build a regression timeline.
5. Classifies p2-repo vs plain-Eclipse layouts.
6. Designs a rollback strategy (local p2 publish vs PDE target directory).

The deterministic MANIFEST extraction/comparison core is
[scripts/analyze_maven_build_failure.py](scripts/analyze_maven_build_failure.py).

## When NOT to use this skill

- Source compilation errors (fix the source).
- Purely environmental failures (network / auth).

## Composition

This is a **base skill**. Organization-specific investigations compose it by adding an
artifact-discovery layer:

- `toolbase_build_investigation` (`bosch_ai_agents`, org-private) — scans a shared component-store
  filesystem for bundle versions and product installations.

Cross-repository composers reference this base by prose path, never a relative link.
