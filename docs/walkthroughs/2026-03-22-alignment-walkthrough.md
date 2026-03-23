# Walkthrough - Industrial Alignment (Fidelity & Redaction)

This walkthrough documents the conversion of alignment feedback into permanent workspace infrastructure.

## 1. New Industrial Skills

### [Redaction & Portability](../../.agents/skills/redaction_portability/SKILL.md)

- **Purpose**: SSOT for path redaction, link relativization, and contextual artifact hosting.
- **Key Mandate**: Zero absolute `file:///` paths in finalized work.

### [Skill Factory](../../.agents/skills/skill_factory/SKILL.md)

- **Purpose**: Automation of "Skill-First" creation following the Fidelity Mandate.
- **Key Mandate**: "Fidelity Scan" to prevent summarization or omission of user-defined operational logic.

## 2. Rule Standardization Updates

### [AI Rule Standardization Rules](../../ai-agent-rules/ai-rule-standardization-rules.md)

- **Fidelity Mandate (Section 4)**: Explicitly forbids the summarization or removal of technical specifics provided by
  the user.

## 3. Workspace Integration

- **Registry**: Both new skills are registered in the root [AGENTS.md](../../AGENTS.md).
- **Contextual Portability**: All session artifacts for this alignment phase have been kept in the appropriate `docs/`
  hierarchy, following the newly established "Contextual Hosting" rule.

***

## Verification Results

- **Binary Check**: Verified folder structure and file existence for all new skills.
- **Grep Audit**: Confirmed the Fidelity Mandate is live in the standardization rules.
- **Redaction**: Verified that all internal links in the new skills are relative.
