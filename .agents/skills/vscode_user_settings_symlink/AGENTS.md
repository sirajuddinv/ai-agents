# AGENTS.md (VS Code User Settings Symlink)

Refer to [SKILL.md](./SKILL.md) for the active operational protocol.

## When to Use

- User requests creating a symlink for VS Code settings portability
- Source symlink points to an intermediate nested "User" subfolder incorrectly

## Key Points

- Symlink MUST point directly to destination (no `/User` suffix)
- Destination MUST contain settings files directly
- Run verification commands after execution
