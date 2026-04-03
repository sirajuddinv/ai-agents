---
name: Rule-to-Skill Industrialization
description: Meta-automation protocol for transforming redundant rule files into
  high-fidelity AI Agent Skills with 100% industrial fidelity.
category: Meta-Automation
---

# Rule-to-Skill Industrialization Skill (v1)

This skill provides the mandatory industrial protocol for transforming flat, redundant rules into authoritative,
high-fidelity AI Agent Skills. It is the definitive process for achieving a Single Source of Truth (SSOT) across
the repository.

***

## 1. Preparation: The Fidelity Scan

Before beginning the transformation, the agent MUST perform a surgical audit of the source rule to prevent data loss.

1. **Mandate Extraction**: Identify every technical mandate, command payload, and safety guardrail in the source rule.
2. **Anti-Loss Validation**: Create a "Traceability Matrix" (Mapping) to ensure every source mandate is tracked to a
   specific section in the target Skill.
3. **Summarization Block**: **Summarization is STRICTLY FORBIDDEN**. Every technical detail must be preserved with
   literal fidelity or enhanced with additional context.

***

## 2. Phase-by-Phase Execution

### 2.1 Phase 1: Mapping & Gap Analysis

- **Audit**: Compare the source rule against the target skill (if it exists).
- **Gap Identification**: Explicitly document what is missing from the skill that exists in the rule (and vice-versa).
- **Conclusion**: Document the "Final Verdict" on what needs to be blended to reach 100% coverage.

### 2.2 Phase 2: High-Fidelity Blending

- **Integration**: Blend all missing pieces into the `SKILL.md`.
- **Greater-Than-Before**: The resulting skill document MUST be more detailed and industrially hardened than the
  original rule.
- **Portability Hardening**: Apply Section 4.2.8 (Hosted VCS Links) for any cross-repository references.

### 2.3 Phase 3: SSOT Promotion & Re-linking

- **Decommissioning**: Once 100% coverage is verified, the source rule file is officially **REDEEMED REDUNDANT**.
- **Global Refactoring**: Perform a search-and-replace across the repository to update all links pointing to the
  old rule file.
- **Hosted VCS Protocol**: If the link is in a submodule and the target is in the parent, you MUST use the
  **Hosted VCS Permanent Link (SHA)** protocol as defined in
  **[markdown-generation-rules.md Section 4.2.8](../../../ai-agent-rules/markdown-generation-rules.md#428-cross-repository--submodule-isolation-links)**.

### 2.4 Phase 4: CI/CD & Output Integrity

- **Output Restriction**: The agent is **BLOCKED** from manually editing auto-generated files (e.g., `README.md`,
  `agent-rules.md`).
- **Template SSOT**: All structural changes to generated indices MUST be made in the `templates/*.template` files.
- **Automation Reliance**: Allow the CI/CD pipeline/sync scripts to update indices automatically once the source
  rule is deleted.

### 2.5 Portability & Depth Audit

Before the final commit, the agent MUST perform a **Portability & Redaction Audit** as defined in the
**[Skill Factory Section 3](../skill_factory/SKILL.md#3-post-drafting-checklist)**. This ensures all documentation
is functionally independent from ephemeral session storage and correctly path-referenced.

***

## 3. Rule Decommissioning Mandate

The source rule file MUST be deleted only after the following conditions are met:

1. 100% technical mandate coverage in the Skill.
2. All static (non-generated) references correctly refactored.
3. A final `markdownlint-cli2` audit passes with **ZERO** errors.

***

## 4. Environment & Dependencies

- **Verification Tool**: `markdownlint-cli2` (Mandatory for compliance checks).
- **Search Tool**: `grep` or `ripgrep` (Mandatory for global reference audit).
- **VCS Tool**: `git` (Mandatory for commit-SHA retrieval).

***

## 5. Traceability & Pedagogical Audit

This skill was established to codify the resolution of the `git_history_refinement` industrialization.

- **Originating Plan**: `implementation_plan.md` (2026-03-29).
- **Industrial Resolution Trace**: [Walkthrough](./docs/walkthrough_init.md).
- **Rule Mapping Documentation**: [Traceability Matrix](./docs/history_refinement_rule_mapping.md).
