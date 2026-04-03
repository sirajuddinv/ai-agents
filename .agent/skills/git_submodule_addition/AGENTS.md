# Git Submodule Addition Skill

This is an Agent Skill for automating the addition of Git submodules with consistent naming and initialization.
Refer to the Single Source of Truth [SKILL.md](./SKILL.md) for active instructions and standards.

## Usage Protocol

- **Input**: User provides a repository URL (e.g., `https://github.com/user/repo`).
- **Action**: Follow the mapping logic to `user_repo` and execute the industrial workflow.
- **Verification**: Ensure the submodule is initialized and on a branch, NOT a detached HEAD.
