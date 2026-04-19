# Git Cross-Repository Cherry-Pick Bridge

## Overview
This bridge provides passive context for the `git_cross_repo_cherry_pick` skill, enabling the agent to transfer commits between unrelated local repositories.

## Active Instructions
For full operational protocols, refer to [SKILL.md](./SKILL.md).

## Usage Triggers
- User asks to "cherry-pick" or "move" a commit between different submodules.
- User wants to apply a "project-standard" change from one repo to another.
- Requirement to maintain git history/metadata during cross-repo file transfers.
