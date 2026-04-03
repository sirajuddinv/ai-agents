# git_submodule_removal

This skill executes the atomic removal of a Git submodule from the repository, purging its `.gitmodules` entry and
internal caching directory.
It should be invoked whenever the user explicitly requests to "remove", "delete", or "purge" a submodule or an unneeded
external tracking dependency.

- **Primary Entry Point**: `.agents/skills/git_submodule_removal/SKILL.md`
