# MCP Server Management Agent (v1)

This agent is specialized in the industrial integration and lifecycle management of MCP (Model Context Protocol) servers.

## Single Source of Truth

The core instructions, configuration standards, and verification protocols are defined in the **Skill SSOT**:
[SKILL.md](./SKILL.md)

## Passive Context & Agent Mandates

This bridge provides context for tools that do not natively support agent skills. It MUST refer to the [SKILL.md](./SKILL.md) for all operational logic, including:

- **Environment & Dependencies**: Refer to [Section 1 of SKILL.md](./SKILL.md#1-environment--dependencies) for configuration discovery and runtime verification.
- **Configuration Standards**: Refer to [Section 2](./SKILL.md#2-configuration-standards) for alphabetical ordering, absolute pathing, and security mandates.
- **Integration Workflow**: Refer to [Section 3](./SKILL.md#3-integration-workflow) for the 5-step integration process.
- **Verification Protocol**: Refer to [Section 4](./SKILL.md#4-verification-protocol) for JSON-RPC pipe testing and syntax validation.
- **Traceability**: Refer to [Section 5](./SKILL.md#5-related-conversations--traceability) for conversation history and architectural precedents.
