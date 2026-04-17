---
name: Markdown Generation
description: Industrial protocol for generating lint-compliant, high-fidelity markdown documentation.
category: Documentation-Standards
---

# Markdown Generation Skill (v1)

This skill provides a standardized protocol for generating Markdown that complies with the **Industrial standard**
(120-character line limit) and passes `markdownlint-cli2` (markdown linting CLI tool) audits.

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

### 1.4 Cross-Reference Links & Anchors

The `markdownlint-cli2` tool validates anchors via **MD051 - Link fragments should be valid**.

- **Anchor Format**: For header `### Step 1 — Deep Change Analysis`, the anchor is `#step-1-deep-change-analysis`
- **Generation Rule**: Convert header to lowercase, replace spaces and `—` (em dash) with dashes (`-`)
- **Verification**: Run `markdownlint-cli2` - it will catch broken anchor errors (MD051)
- **Best Practice**: Always use anchors when linking to headers within skill/rule files

### 1.5 Path Verification

#### Default (CLI-Only)

- **Anchor**: Enforced by MD051 (built-in)
- **File Path**: NOT enforced - run manual verification:
    - `ls -la <path>` to confirm target exists
    - From `skills/<skill>/`: `ls ../<sibling-skill>/SKILL.md`
    - From `skills/<skill>/`: `ls ../../../ai-agent-rules/<rule>.md`

#### With Node.js Custom Rules (If Available)

Install and configure:

```bash
npm install --save-dev markdownlint-rule-relative-links
```

Add to `.markdownlint-cli2.jsonc` (NOT `.markdownlint.jsonc`):

```jsonc
{
    "customRules": ["markdownlint-rule-relative-links"],
    "config": {
        "relative-links": { "root_path": "." }
    }
}
```

Then both anchors AND file paths validated automatically.

***

## 2. Verification Workflow

Before finalizing ANY markdown file, the agent MUST:

1. **Config Initialization**: If the project lacks a `.markdownlint.jsonc` file, the agent
   MUST initialize it using rules from the reference config (`../../../.markdownlint.jsonc`
   relative to this skill file), incorporating the `MD013` 120-character line length exception.
2. **Sync Check**: Ensure `.vscode/settings.json` contains `"markdownlint.configFile": ".markdownlint.jsonc"` to
   synchronize the IDE extension with the project's Industrial standard.
3. **Auto-Fix**: Run `markdownlint-cli2 --fix <file_path>` from the project root.
4. **Audit Check**: Run `markdownlint-cli2 <file_path>`.
5. **Manual Correction**: Fix any remaining semantic or structural errors (e.g., heading increments).
6. **Fidelity Verification**: Ensure the "Fidelity Mandate" (no loss of user technical specifics) is upheld during
   formatting.

***

## 3. Related Rules

- **SSOT**: [markdown-generation-rules.md](../../../ai-agent-rules/markdown-generation-rules.md)
- **Formatting Protocol**: [ai-rule-standardization-rules.md](../../../ai-agent-rules/ai-rule-standardization-rules.md)
