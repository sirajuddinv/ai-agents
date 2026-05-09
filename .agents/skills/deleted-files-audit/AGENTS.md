---
name: Deleted Files Audit
description: Passive context bridge for systematic audit of deleted files in a Git repository.
category: Code Hygiene & Maintenance
---

# Deleted Files Audit (Ref)

This bridge provides passive context for the `deleted-files-audit` skill, which categorizes pending or recent
deletions, scans the codebase for stale references, checks IDE configurations, and reports a safety verdict before
the user commits a destructive change.

It should be invoked whenever the user deletes files and asks to verify, or whenever `git status` shows pending
deletions and the user wants a hygiene check before commit.

- **Primary Entry Point**: [.agents/skills/deleted-files-audit/SKILL.md](./SKILL.md)
- **Verdict Output**: Safety classification per deleted path + list of dangling references requiring fix or
  acknowledgment.
