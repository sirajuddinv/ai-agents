---
name: Git Commit Details Audit
description: Industrial protocol for retrieving and analyzing high-fidelity commit metadata, hunks, and pedagogical explanations across the repository and its submodules.
category: Git-Hygiene
---

# Git Commit Details Audit Skill (v1)

This skill mandates the retrieval and deep analysis of commit metadata, changed files, and code hunks. It ensures 100% fidelity to the repository's **Atomic History Mandate** by providing standardized, pedagogical explanations for every modification.

***

## 1. Environment & Dependencies

The agent MUST autonomously verify the availability of required tools before executing an audit:

- **Git**: Verified via `which git`.
- **Python 3**: Verified via `which python3` (required for the industrial audit engine).
- **PAGER**: All Git commands MUST be prepended with `PAGER=cat` to prevent terminal hangs.

***

## 2. Operational Logic: The Audit Workflow

### 2.1 Automated Audit (Industrial Standard)

The agent MUST prioritize the use of the Python-backed audit engine to guarantee standardized formatting and cross-repository auto-discovery.

```bash
# Execute the audit engine from the skill's scripts directory
python3 .agents/skills/git_commit_details_audit/scripts/audit.py <COMMIT_SHA>
```

#### Detailed Command Explanation:
- `python3`: Invokes the Python 3 interpreter to run the audit logic.
- `audit.py`: The specialized engine that iterates through the main repository and all submodules to resolve the SHA.
- `<COMMIT_SHA>`: The 40-character (full) or unique short SHA of the commit to be audited.

#### Output Features:
- **Metadata**: Author, Date, and Pedagogical Commit Message.
- **Advanced Reference Tracking**: Tabular identification of all branches (local/remote) and tags containing the SHA, along with their current Tips and Divergence Status.
- **Changed Files Inventory**: High-level modification status codes.
- **Hunk Exposure**: Full diff analysis with "Why vs. What" narrative context.

### 2.2 Manual Fallback (Hunk Isolation)

If the audit engine is unavailable, the agent MUST orchestrate the **[Git Commit Metadata Extraction](../git_commit_metadata_extraction/SKILL.md)** primitive. 

1. Execute the `git_commit_metadata_extraction` primitive on the `<COMMIT_SHA>` to obtain the zero-omission metadata and exact file classifications.
2. After retrieving the core metadata, extract the full diff hunks for analysis:

```bash
# Extract full diff hunks
PAGER=cat git show -p <COMMIT_SHA>
```

*Do not attempt to write custom bash commands to extract metadata; rely entirely on the primitive to ensure fidelity.*

***

## 3. Pedagogical Narrative Mandate (Crucial)

Every audit report presented to the user MUST follow the **"Why vs. What"** standard. The agent is BLOCKED from merely restating the code changes in the diff.

1. **High-Level Impact**: Summarize *why* the commit exists and what architectural goal it accomplishes.
2. **Hunk Analysis**: For each modified file, explain the rationale behind specific logic shifts (e.g., "Hardening the regex to avoid catastrophic backtracking").
3. **Deep Technical Breakdown Table**: If the commit contains more than 3 hunks or complex logic, the agent MUST include a table in the following format:

| Line Range | Logic Modification | Pedagogical Rationale |
| :--- | :--- | :--- |
| `L123-145` | Implementation of `try-catch` wrapper | Defensive hardening against missing submodule pointers. |

***

## 4. Traceability & Related Conversations

- **Session Log**: Results from this skill should be linked to the relevant industrial walkthrough in `docs/walkthroughs/`.
- **Rules Mapping**: All audit findings MUST comply with the **[Git Operation Rules](../../../ai-agent-rules/git-operation-rules.md)**.
- **Related Skills**: Uses **[Git Commit Metadata Extraction](../git_commit_metadata_extraction/SKILL.md)** as its fallback primitive.

***

## 5. Post-Audit Verification Checklist

- [ ] Does the output match the requested "Commit Details" template?
- [ ] Are all SHAs cross-referenced between repositories (main vs. submodule)?
- [ ] Does the "Why vs. What" narrative avoid redundant "fluff"?
- [ ] Is the Markdown output 100% lint-compliant?
