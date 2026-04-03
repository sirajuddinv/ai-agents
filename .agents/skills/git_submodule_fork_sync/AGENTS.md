# git_submodule_fork_sync

This skill oversees the global synchronization between the root repository's `.gitmodules` registry and the internal
remote endpoints of isolated submodules.
It should be explicitly invoked whenever a user references "forking a submodule", "updating submodule URLs to track a
fork", or resolving "fork misalignment" issues where `.gitmodules` points to an upstream branch rather than internally
established work.

- **Primary Entry Point**: `.agents/skills/git_submodule_fork_sync/SKILL.md`
- **Execution Engine**: `.agents/skills/git_submodule_fork_sync/scripts/sync.py`
