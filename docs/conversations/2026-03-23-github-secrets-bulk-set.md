# Conversation Log: GitHub Secrets Bulk Set Skill

**Date:** 2026-03-23

**Objective:** Create an agent skill for bulk-setting GitHub Actions repository secrets from a local
`.env`-style secrets file using the `gh` CLI, following the Skill Factory and ai-rule-standardization-rules.

***

## 1. Request

> **User**: Can you use `gh` to set secrets on a GitHub repository from a local secrets file? Can we have a
> skill for this? You must obey `ai-rule-standardization-rules.md` and `skill_factory` skill instructions.

### Agent Response

Confirmed `gh secret set --env-file` as the correct mechanism. Set 5 secrets successfully (a 6th was rejected
by the GitHub API because its name started with `GITHUB_` — a core constraint now documented in the skill).
Then created the `github_secrets` skill.

***

## 2. Analysis & Planning

The skill was designed with the standard Skill-First architecture:

- `SKILL.md`: SSOT for environment verification, naming constraints, bulk import commands, and failure modes.
- `AGENTS.md`: Companion bridge with activation triggers and quick-reference commands.
- Registration in the root `AGENTS.md` skills table.

Key findings during the session:

- `gh secret set --env-file` is idempotent — safe to re-run.
- GitHub API rejects any secret name starting with `GITHUB_` (HTTP 422).
- `$HOME` must be used in example paths, never hardcoded usernames.
- Traceability section must link to `docs/conversations/`, not ephemeral brain paths.

***

## 3. Execution

1. **Drafting**: Created `SKILL.md` and `AGENTS.md` in `.agents/skills/github_secrets/`.
2. **Registration**: Added `GitHub Secrets Bulk Set` row to root `AGENTS.md`.
3. **Lint**: Fixed MD060 table-alignment violations by converting prose-heavy tables to bullet lists.
4. **Redaction (v2 — user-identified issues)**:
    - Replaced real repo name with `sample_owner/sample_repo`.
    - Replaced private path `$HOME/Lab_Data/…` with `$HOME/sample-repo/file.secrets`.
    - Fixed contradicting `/Users/dk/` in NOTE to `/Users/X/`.
    - Replaced non-portable Gemini brain path in Traceability with this relative docs link.

***

## 4. Confirmation & Outcome

- [x] `github_secrets` skill created in [.agents/skills/github_secrets/](../../.agents/skills/github_secrets/).
- [x] Skill registered in [AGENTS.md](../../AGENTS.md).
- [x] Redaction & Portability protocol applied (v2 corrections).
- [x] Session log stored in permanent `docs/conversations/` location.

***

## 5. Attachments & References

| File/Artifact | Description |
| :--- | :--- |
| [SKILL.md](../../.agents/skills/github_secrets/SKILL.md) | Core skill instructions (SSOT). |
| [AGENTS.md](../../.agents/skills/github_secrets/AGENTS.md) | Companion bridge. |

- Related Rule: [ai-rule-standardization-rules.md](../../ai-agent-rules/ai-rule-standardization-rules.md)
- Related Skill: [skill_factory/SKILL.md](../../.agents/skills/skill_factory/SKILL.md)
- Related Skill: [redaction_portability/SKILL.md](../../.agents/skills/redaction_portability/SKILL.md)

***

## 6. Summary

This session established the `GitHub Secrets Bulk Set` skill. The core capability (`gh secret set --env-file`)
was verified working for 5 of 6 secrets; the 6th failed due to the `GITHUB_` reserved prefix constraint, which
is now a prominent documented caveat. A second pass applied the Redaction & Portability protocol to remove all
data-leakage risks and non-portable path references from the skill files.
