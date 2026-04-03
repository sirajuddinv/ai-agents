---
name: Skill Factory
description: Industrial protocol for automated creation of "Skill-First" AI Agent skills with high fidelity.
category: Meta-Automation
---

# Skill Factory Skill (v1)

This skill automates the creation of new AI Agent Skills following the **agentskills.io** protocol and the
**Industrial Fidelity** mandates.

***

## 1. Preparation: The Fidelity Scan

The Agent MUST ensure that no operational detail is lost during the skill creation process.

1. **Source Discovery**: Identify all user-provided operational logic, dependencies, and constraints from the
   conversation history.
2. **Anti-Loss Validation**: Create a list of "Must-Include" technical specifics. **Summarization is BLOCKED** for
   these items.
3. **Preservation Check**: Ensure existing content is preserved and blended. **Destructive overwriting is FORBIDDEN**.
4. **Script Audit**: Search the target skill directory and workspace for existing automation scripts. **Consolidation
   is MANDATORY**—Utility duplication is a failure of the Industrial standard.

- **Greater-Than-Before**: The skill MUST be more detailed than the prompt that initiated it, including
  extrapolated context where necessary.

***

## 2. Skill Generation Protocol

### 2.1 Directory Structure

- Create the target folder in `.agents/skills/<skill-name>/` (underscores preferred for names).
- Initialize `SKILL.md` (active SSOT) and `AGENTS.md` (companion bridge).

### 2.2 SKILL.md Composition

The `SKILL.md` MUST include:

1. **YAML Frontmatter**: name, description, category.
2. **Environment & Dependencies**: Mandated verification logic (`which`, version checks).
3. **Operational Logic**: The EXACT steps provided by the user (**Zero Omission**).
4. **Traceability Section**: Links to permanent conversation logs using the **Redaction & Portability** protocol.

### 2.3 Registration

- Update the root `AGENTS.md` skills table to register the new skill with its absolute path and description.

***

## 3. Post-Drafting Checklist

Every skill generated via the Factory MUST automatically undergo the final verification:

- **Portability, Redaction & PII Audit**: Every file MUST be neutral and portable.
    1. **Link Relativization**: All `file:///` absolute paths MUST be replaced with relative paths to the permanent
       `docs/` directory of the skill.
    2. **Redaction & Normalization**: PII, account names, and biological path prefixes MUST be replaced with standard
       placeholders as defined in **[Section 4.2.9 of the Generation Rules](../../../ai-agent-rules/markdown-generation-rules.md#429-redaction--pii-neutralization)**.
    3. **Directory Depth Audit**: Verify the correct directory depth (e.g., `../../../` from a 3-level deep skill).
- **Contextual Hosting**: Documentation (logs, artifacts) MUST reside in the component's `docs/` folder.
- **Fidelity Check**: Verify that no technical details from the source conversation were summarized or lost.
- **Markdown Audit**: Run the **Markdown Generation** protocol to ensure 100% lint compliance.
