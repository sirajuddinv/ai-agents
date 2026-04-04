# Git Submodule Pointer Repair Skill

## Overview
This skill provides high-fidelity, surgical repair of invalid submodule pointers within a parent repository's history. It implements the **Synchronization Horizon** algorithm to autonomously identify the correct architectural alignment point between parent mandates and modular history.

## Skill Path
[.agents/skills/git_submodule_pointer_repair/SKILL.md](./SKILL.md)

## Usage Scenarios
- **Broken Pointer Resolution**: Fixing submodule hashes that no longer exist in the submodule repository.
- **Historical Realignment**: Surgically updating a specific commit to point to a valid submodule state while preserving parental metadata.
- **Mandate Auditing**: Identifying exactly which submodule commit satisfies a parent's synchronization requirements.

## Engine
[scripts/repair.py](./scripts/repair.py) (Surgical Synchronization Engine)
