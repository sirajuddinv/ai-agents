---
name: LOC Analysis
description: Passive context bridge for calculating lines of code added, deleted, and modified across a feature scope.
category: Metrics & Reporting
---

# LOC Analysis (Ref)

This bridge provides passive context for the `loc-analysis` skill, which calculates lines of code added, deleted,
and modified — comparing two codebases or analyzing git history within a scoped feature boundary.

It should be invoked whenever the user asks to "calculate LOC," "measure code changes," "quantify a feature's
footprint," or sizing a refactor before/after.

- **Primary Entry Point**: [.agents/skills/loc-analysis/SKILL.md](./SKILL.md)
