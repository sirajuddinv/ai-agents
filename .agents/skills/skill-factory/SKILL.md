---
name: skill-factory
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

### 2.0 Layering Decision (Base vs. Composer)

Before creating any new skill, the Agent MUST decide whether the requested capability is:

1. **Atomic** — a single, indivisible workflow with no reusable primitive. Proceed to §2.1 as one skill.
2. **Layerable** — contains a generic primitive (glob assembly, metadata extraction, path normalization, brace
   expansion, list sort+dedupe, etc.) that other domain-specific tasks could reuse. Split into:
    - A **base skill** owning ONLY the primitive, with a stdin / file / argument CLI contract and deterministic output.
      The base skill MUST be domain-agnostic.
    - One or more **composer skills** owning the domain-specific discovery, piping their output into the base skill.

The layering test: *"Could a different domain ever need the same primitive?"* If yes, layering is **MANDATORY** —
inlining the primitive into a single skill is a violation of the SSOT contract.

Reference exemplar: [vscode-search-exclude-glob](../vscode-search-exclude-glob/SKILL.md) (base) +
[vscode-search-exclude-submodules](../vscode-search-exclude-submodules/SKILL.md) (composer).

### 2.1 Directory Structure

- Create the target folder in `.agents/skills/<skill-name>/` (hyphens required for names).
- Initialize `SKILL.md` (active SSOT) and `AGENTS.md` (companion bridge).
- For **composer skills**: the composer's script MUST resolve the base script via a relative path anchored to its own
  location (`SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"` then `BASE="$SCRIPT_DIR/../../<base-skill>/scripts/..."`),
  so invocation works regardless of the caller's `cwd`. The composer MUST verify the base script exists and exit
  non-zero with a clear error if it is missing.

### 2.2 SKILL.md Composition

The `SKILL.md` MUST include:

1. **YAML Frontmatter**: name, description, category. Skill names MUST use lowercase letters, numbers, and hyphens.
2. **Environment & Dependencies**: Mandated verification logic (`which`, version checks).
3. **Operational Logic**: The EXACT steps provided by the user (**Zero Omission**).
4. **SSOT Compliance**: The skill MUST NOT duplicate technical standards
   defined in the central rule repository. Instead, it MUST link to the
   authoritative rule files using relative links (e.g., to the atomic
   commit rules or commit message rules).
5. **Traceability Section**: Links to permanent conversation logs using the **Redaction & Portability** protocol.

### 2.2.1 Script Authoring Mandates

When the skill ships executable scripts under `scripts/`, every script MUST obey:

1. **Language**: PowerShell (`.ps1`) by default, cross-compatible with Windows PowerShell 5.1+ and PowerShell Core 7+.
   Other languages require an explicit user override or a documented technical justification.
2. **Documentation Headers**: Comment-based help with `.SYNOPSIS`, `.DESCRIPTION`, `.PARAMETER`, `.EXAMPLE`, `.NOTES`
   sections — see the [Script Management Rules](../../../ai-agent-rules/script-management-rules.md).
3. **Execution**: Documented invocations MUST use `pwsh-preview` (preferred) with `pwsh` as fallback.
4. **Common-Utils Dot-Source**: Scripts MUST dot-source `Common-Utils.ps1` from the
   [`powershell-scripts`](../../../ai-agent-rules/powershell-scripts/) submodule of `ai-agent-rules` for shared
   helpers (`Write-Message`, etc.) unless an explicit exemption is justified in the script's `.NOTES` block.
5. **Portable Anchored Paths**: All sibling-artifact lookups (the dot-source above, base-skill scripts under the
   Layered Composition Mandate, config files) MUST be resolved through paths anchored on the script's own location
   via `Split-Path -Parent $MyInvocation.MyCommand.Path` + `Join-Path` — NEVER `$PWD`-relative or hard-coded.
6. **Write-Message Safeguard**: Every `Write-Message` call MUST be guarded with
   `if (-not [string]::IsNullOrWhiteSpace($Message)) { ... }`.
7. **Recursive Submodule Bootstrap**: Any documentation that instructs the user to clone or initialize the
   `powershell-scripts` submodule (or any other submodule) MUST use the recursive form
   (`git submodule update --init --recursive <path>` or `git clone --recurse-submodules <url>`).
8. **Strict Mode Hygiene**: Scripts SHOULD declare `Set-StrictMode -Version Latest` and `$ErrorActionPreference = 'Stop'`.
   When reading `$LASTEXITCODE` after invoking another script, guard with
   `Test-Path Variable:LASTEXITCODE` to avoid strict-mode failures on first invocation.

### 2.3 Registration

- Update the root `AGENTS.md` skills table to register the new skill with its absolute path and description.
- **Alphabetical Order Mandate**: The root `AGENTS.md` skills table MUST remain sorted alphabetically (case-insensitive)
  by the **Skill** column. New entries MUST be inserted at the correct sorted position \u2014 NEVER appended to the end.
  After insertion, the Agent MUST visually verify that the row above and below the new entry maintain the sort order.
- For layered pairs: register **both** the base and the composer in the same change at their respective sorted
  positions, with the composer's row explicitly noting *"Composer \u2014 feeds X into the base Y skill"* so the dependency
  is visible at the index level.

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
- **Registration Audit**: Confirm the new skill row was inserted into the root `AGENTS.md` skills table at the correct
  alphabetical (case-insensitive) position by the **Skill** column, NOT appended to the end. Spot-check the rows
  immediately above and below to verify the sort order holds.
- **Composition Audit** (when layering applies):
    1. **No Inlining**: Confirm the composer script does NOT reimplement the base primitive — it MUST shell out to
       the base script.
    2. **End-to-End Pipeline Validation**: Execute the composer against a real input and confirm the output matches
       the base skill's expected format (deterministic, sorted, deduped, correctly framed).
    3. **Bidirectional Discoverability**: Confirm the base skill lists the new composer in its
       `## Composition by Higher-Level Skills` table, and the composer links back to the base in its
       `## Composition Rationale` and `## Related Skills` sections.
- **Script Authoring Audit** (when scripts are shipped):
    1. **Cross-Version Smoke Test**: Execute the script with `pwsh-preview` (and, where feasible, `pwsh`) on a real
       input and confirm exit code 0 on the success path and exit code 1 with a `Write-Message`-rendered diagnostic on
       the failure path.
    2. **Pipeline Cleanliness**: Capture the script's stdout into a variable (`$out = & ./script.ps1 ...`) and confirm
       it contains exactly the expected payload — no diagnostic noise leaking onto the success stream.
    3. **Common-Utils Dependency**: Confirm the documented `git submodule update --init --recursive` snippet for the
       `powershell-scripts` submodule appears in the skill's Environment & Dependencies section.
    4. **Path Portability**: Run the script from at least two different working directories (e.g., the repo root and
       `/tmp`) to prove the `$MyInvocation`-anchored relative paths still resolve.
