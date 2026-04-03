---
name: Redaction & Portability
description: Protocol for addressing, redacting, and relativizing sensitive/absolute information in artifacts.
category: Security-Standards
---

# Redaction & Portability Skill (v1)

This skill provides a mandatory protocol for ensuring all session artifacts are portable, non-sensitive, and
contextually hosted within the workspace.

***

## 1. Data Fidelity & Redaction

Every absolute path or system-specific identifier MUST be handled according to the following rules:

### 1.1 Absolute Path Handling

- **Biological/System Identifiers**: Replace any user-specific path prefix (e.g., `/Users/X/`), biological identifiers (e.g., human names like `Anushad PK`), or technical identifiers with a redacted placeholder: `[REDACTED]` or `[REDACTED_NAME]`.
- **Environmental Context**: If a path must be specific but is sensitive, replace it with a descriptive placeholder: `[USER_PROVIDED_PATH]`.
- **Absolute Limit**: Total absolute paths in a finalized document MUST be zero.

### 1.2 Link Relativization

- **Workspace Portability**: All links to other files within the workspace MUST use relative paths (e.g.,
  `../../docs/plan.md`).
- **Standard**: Follow [markdown-generation-rules.md](../../../ai-agent-rules/markdown-generation-rules.md) for
  authoritative link syntax.

***

## 2. Contextual Hosting (Root-Level)

Session artifacts related to rule-sets or specific components MUST be stored in the appropriate hierarchy to
ensure they are not "orphaned" when a subset of the workspace is used.

### 2.1 Artifact Relocation

- **Rules Documentation**: Keep logs related to `ai-agent-rules` in `ai-agent-rules/docs/`.
- **Codebase Documentation**: Keep logs related to the primary codebase in `docs/` at the workspace root.
- **Portability Mandate**: Artifacts MUST be moved from ephemeral brain locations to these permanent stores
  before the session concludes.

***

## 3. Implementation Workflow

1. **Relativize**: Scan for `file:///` and convert to relative links.
2. **Redact**: Replace sensitive identifiers (paths, human names, emails) with `[REDACTED]` or `[REDACTED_NAME]`.
3. **Relocate**: Move files to the permanent `docs/` hierarchy.
4. **Link Audit**: Verify all relative links point to the new permanent locations.
