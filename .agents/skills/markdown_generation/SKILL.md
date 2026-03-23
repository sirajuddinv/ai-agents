---
name: Markdown Generation
description: Industrial protocol for generating lint-compliant, high-fidelity markdown documentation.
category: Documentation-Standards
---

# Markdown Generation Skill (v1)

This skill provides a standardized protocol for generating Markdown that complies with the **Industrial standard**
(120-character line limit) and passes `markdownlint-cli2` audits.

***

## 1. Core Syntax Standards

Every generated file MUST adhere to these absolute constraints:

### 1.1 Line Length (MD013)

- **Limit**: 120 characters per line.
- **Exception**: Long URLs and file paths that cannot be broken. Use **Reference-style links** at the bottom of the
  document to resolve length violations for URLs.
- **Wrapping**: Proactively wrap descriptions and YAML blocks to stay under the limit.

### 1.2 Layout & Tables (MD060)

- **Table Alignment**: Use mathematically perfect aligned pipes (`|`).
- **Cell Spacing**: One mandatory space padding on both sides of every pipe (` | content | `).
- **Blank Lines**: Headers, lists, and code blocks MUST be surrounded by blank lines.

### 1.3 Frontmatter

- **Rules/Skills**: Use the triple-dash block (`---`) as defined in [ai-rule-standardization-rules.md](../../../ai-agent-rules/ai-rule-standardization-rules.md).
- **General Docs**: Use the HTML comment block (`<!-- title: ... -->`) for indexing.

***

## 2. Verification Workflow

Before finalizing ANY markdown file, the agent MUST:

1. **Sync Check**: Ensure `.vscode/settings.json` contains `"markdownlint.configFile": ".markdownlint.jsonc"` to
   synchronize the IDE extension with the project's Industrial standard.
2. **Auto-Fix**: Run `markdownlint-cli2 --fix <file_path>` from the project root.
3. **Audit Check**: Run `markdownlint-cli2 <file_path>`.
4. **Manual Correction**: Fix any remaining semantic or structural errors (e.g., heading increments).
5. **Fidelity Verification**: Ensure the "Fidelity Mandate" (no loss of user technical specifics) is upheld during
   formatting.

***

## 3. Related Rules

- **SSOT**: [markdown-generation-rules.md](../../../ai-agent-rules/markdown-generation-rules.md)
- **Formatting Protocol**: [ai-rule-standardization-rules.md](../../../ai-agent-rules/ai-rule-standardization-rules.md)
