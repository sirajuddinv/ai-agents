---
name: VS Code Settings Promotion
description: Passive context bridge for migrating profile-specific settings to global scope with universal enforcement.
category: VSCode-Configuration
---

# VS Code Settings Promotion (Ref)

This bridge provides passive context for the `vscode-settings-promotion` skill, which automates migration of
profile-specific settings to global scope, ensuring a single setting value is enforced universally across all VS
Code profiles.

It should be invoked whenever the user asks to promote profile settings to global, deduplicate per-profile
configuration, or enforce a universal value of a particular setting.

- **Primary Entry Point**: [.agents/skills/vscode-settings-promotion/SKILL.md](./SKILL.md)
