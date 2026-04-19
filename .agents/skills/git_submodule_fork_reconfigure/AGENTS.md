# Git Submodule Fork Reconfigure Bridge

## Overview
This bridge provides passive context for the `git_submodule_fork_reconfigure` skill, enabling the agent to handle submodule push failures by forking and swapping remotes.

## Active Instructions
For full operational protocols, refer to [SKILL.md](./SKILL.md).

## Usage Triggers
- Submodule push fails with `403 Forbidden` or `Permission denied`.
- Requirement to maintain a personal fork of a submodule while tracking the original as `upstream`.
- Reconfiguring submodule remotes for write access.
