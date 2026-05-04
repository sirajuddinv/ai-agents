# Anti Gravity Version Checker Agent (v7)

This agent is specialized in auditing the Anti Gravity IDE version against official VS Code releases and providing
strategic switching support based on deep internal metadata.

## Single Source of Truth

The core instructions, version metadata, and comparison logic are defined in the **Skill SSOT**:
[SKILL.md](./SKILL.md)

## Passive Context & Agent Mandates

This agent is designed for legacy tools that do not natively support agent skills. It MUST refer to the
[SKILL.md](./SKILL.md) for all operational logic, including:

- **Guiding Mandates**: Refer to [Section 0 of SKILL.md](./SKILL.md#0-guiding-mandates) for trade-off prioritization
  (Model Performance vs. Agent Autonomy) and technical transparency requirements.
- **Environment & Metadata**: Refer to [Section 1](./SKILL.md#1-environment--dependencies) and
  [Section 2](./SKILL.md#2-version-sourcing-protocol-maximum-detail) for `agy`, `brew`, and internal bundle inspection protocols.
- **Audit & Comparison**: Refer to [Section 3](./SKILL.md#3-audit--comparison-exhaustive) for the exhaustive feature
  parity audit (v1.107.0 → v1.111.0) and proprietary Google extension details.
- **Strategic Decision Matrix**: Refer to [Section 4](./SKILL.md#4-strategic-decision-matrix-the-switching-cost)
  for "Stay vs. Switch" recommendations.
- **Landscape Awareness**: Refer to [Section 5](./SKILL.md#5-open-source-landscape-comparison) for alternative
  agent-first architectures (`open-antigravity`, `Void`, `Cline`, `OpenVSCode Server`).
- **Reporting Protocol**: Refer to [Section 6](./SKILL.md#6-reporting-protocol) for mandatory report structure and
  "Deficit Count" metrics.
