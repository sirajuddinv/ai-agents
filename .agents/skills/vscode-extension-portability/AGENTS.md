---
name: VS Code Extension Link Portability
description: Passive context bridge for refactoring non-portable extension-linked paths in settings.json to portable tilde-anchored links.
category: VSCode-Configuration
---

# VS Code Extension Link Portability (Ref)

This bridge provides passive context for the `vscode-extension-portability` skill, which refactors non-portable
extension-linked paths in `settings.json` (absolute `/Users/...`, `C:\Users\...` paths) into permanent, portable
links anchored on `~`.

It should be invoked whenever a `settings.json` audit surfaces machine-specific absolute paths in extension
configuration keys, or whenever the user asks to make a VS Code profile portable across machines.

- **Primary Entry Point**: [.agents/skills/vscode-extension-portability/SKILL.md](./SKILL.md)
