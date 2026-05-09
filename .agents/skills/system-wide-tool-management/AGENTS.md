---
name: System-Wide Tool Management
description: Passive context bridge for detecting, installing, and verifying system-wide CLI tools across macOS, Linux, and Windows.
category: Environment-Management
---

# System-Wide Tool Management (Ref)

This bridge provides passive context for the `system-wide-tool-management` skill, which encodes the industrial
protocol for detecting, installing, and verifying system-wide CLI tools (e.g., `jq`, `curl`, `git`, `gh`) across
macOS (`brew`), Linux (`apt`/`yum`/`dnf`), and Windows (`winget`/`choco`).

It should be invoked whenever a system tool is required but may not be installed or available in `PATH`, and
whenever a skill's Environment & Dependencies section needs to autonomously verify a missing tool.

- **Primary Entry Point**: [.agents/skills/system-wide-tool-management/SKILL.md](./SKILL.md)
- **Related Skill**: [`mise-tool-management`](../mise-tool-management/SKILL.md) — for tools that belong inside a
  mise-managed environment rather than globally.
