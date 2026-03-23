# [Create MCP Management Skill] (v1)

## Rule Compliance Reference

- [ai-rule-standardization-rules.md](../../ai-agent-rules/ai-rule-standardization-rules.md)
- [node-crypto-mcp-infrastructure-rules.md](../../ai-agent-rules/node-crypto-mcp-infrastructure-rules.md)
- [postman-mcp-server-rules.md](../../ai-agent-rules/postman-mcp-server-rules.md)

## Proposed Changes

### [MCP Management Skill]

#### [NEW] [SKILL.md](../../.agents/skills/mcp-management/SKILL.md)

Core instruction set for managing MCP servers, including configuration patterns and verification protocols.

#### [NEW] [AGENTS.md](../../.agents/skills/mcp-management/AGENTS.md)

Companion bridge for legacy context, referencing `SKILL.md`.

### [Workspace Registration]

#### [MODIFY] [AGENTS.md](../../AGENTS.md)

Add the new `MCP Management` skill to the skills registry table.

## Verification Plan

### Automated Tests

- [ ] Run `markdownlint-cli` (if available) on the new MD files.
- [ ] Verify all relative links within the skill are functional.

### Manual Verification

- [ ] Verify that the new skill appears in the `AGENTS.md` registry.
- [ ] Sample execution: Ask the agent to "use the MCP management skill to check current configuration" and see if it
  correctly refers to the new skill.
