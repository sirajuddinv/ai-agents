---
name: Git Commit Comparison Audit
description: Active instruction set for side-by-side comparative analysis between two commits via skill orchestration.
category: Git-Hygiene
---

# Git Commit Comparison Audit Skill (v1)

This skill mandates high-fidelity comparison of two Git commits. It **orchestrates** the `git_commit_details_audit` skill to retrieve individual commit data and then synthesizes a "Why vs. What" comparative report.

***

## 1. Environment & Dependencies

The agent MUST autonomously verify the availability of required tools:

- **Git**: Verified via `which git`.
- **Python 3**: Verified via `which python3`.
- **Orchestrated Skill**: Verify existence of `.agents/skills/git_commit_details_audit/scripts/audit.py`.

***

## 2. Operational Logic: The Comparison Workflow

### 2.1 Automated Orchestration (Industrial Standard)

The agent MUST use the `compare.py` orchestrator to guarantee standardized tabular formatting and automated submodule depth.

```bash
# Execute the comparison orchestrator
python3 .agents/skills/git_commit_comparison_audit/scripts/compare.py <SHA1> <SHA2>
```

#### Detailed Command Explanation:
- `python3`: Invokes the interpreter.
- `compare.py`: The specialized orchestrator that calls the detail-audit script for each SHA.
- `<SHA1> <SHA2>`: The two commits to be compared.

#### Output Features:
- **Side-by-Side Metadata**: Comparative table of Author, Date, and Message.
- **Reachability Audit**: Divergence status for branches/tags across both commits.
- **Submodule Pointer Audit**: Detection of mismatched submodule pointers.
- **Recursive Submodule Depth**: If pointers differ, the orchestrator automatically performs a detail-audit *inside* the submodule for both target SHAs.
- **1. High-Fidelity Pointer Comparison**: Tabular summary of parent commits vs. submodule SHAs and their functional significance.
- **2. Recursive History Audit Results**: Orchestrated audit of the submodule's internal history between the two pointers.
- **3. High-Level Impact: "Why vs. What"**: Pedagogical synthesis of the technical delta and historical rationale.

***

## 3. Pedagogical Narrative Mandate

Every comparison report MUST follow the **"Why vs. What"** standard, utilizing the auto-generated summary from `compare.py`:

1. **The What**: The technical delta (e.g., "SHA1 points to functional rules, SHA2 is a legacy snapshot"). This is pre-populated by the orchestrator but should be refined by the agent for clarity.
2. **The Why**: The historical rationale (e.g., "Commit 64f0f89 was preserved in the 2026-04-04 backup branches during the industrialization rebase"). This MUST be provided by the agent using context from the current session.

***

## 4. Traceability & Related Conversations

- **Session Log**: Results from this skill should be linked to the relevant industrial walkthrough.
- **Rules Mapping**: All comparative findings MUST comply with the **[Git Operation Rules](../../../ai-agent-rules/git-operation-rules.md)**.

***

## 5. Post-Audit Verification Checklist

- [ ] Are both SHAs independently audited using the detail-audit script?
- [ ] Does the report include a side-by-side metadata table?
- [ ] Is the submodule pointer shift clearly identified and analyzed?
- [ ] Does the "Why vs. What" narrative explain the divergence between versions?
