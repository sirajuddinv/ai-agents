---
name: Mise Tool Management
description: Passive context bridge for mise configuration trust, tool version selection, and Python package setup.
category: Environment-Management
---

# Mise Tool Management (Ref)

This bridge provides passive context for the `mise-tool-management` skill, which encodes industrial protocols for
mise configuration trust, tool version selection, and Python package setup into a mise-managed environment.

It should be invoked whenever a `mise.toml` is untrusted, a required tool is missing, or a Python package needs to
be installed into a mise-managed virtualenv.

- **Primary Entry Point**: [.agents/skills/mise-tool-management/SKILL.md](./SKILL.md)
- **Related Skill**: [`system-wide-tool-management`](../system-wide-tool-management/SKILL.md) — for tools that
  belong globally rather than in a mise environment.
