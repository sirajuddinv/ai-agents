---
name: Git Commit Comparison Audit
description: Passive context bridge for high-fidelity comparative analysis between two Git commits.
category: Git-Hygiene
---

# Git Commit Comparison Audit (Ref)

This skill provides the architectural context for performing side-by-side comparative audits of Git commits. It is an orchestrator that leverages the `git_commit_details_audit` skill to analyze metadata, reachability, and submodule alignment.

### Core Documentation (SSOT)
- **Active Instructions**: [SKILL.md](./SKILL.md)
- **Orchestration Logic**: [scripts/compare.py](./scripts/compare.py)

### Functional Capabilities
1. Side-by-side comparison of commit metadata (Author, Date, Message).
2. Divergence analysis for branches and tags (Main + Submodules).
3. Automated submodule pointer audit and recursive history depth.
4. "Why vs. What" pedagogical reporting for historical realignment.

***

### Reference Mapping
- **Primary Tool**: `.agents/skills/git_commit_comparison_audit/scripts/compare.py`
- **Dependencies**: `git_commit_details_audit` (Orchestrated Skill)
