---
name: manifest-driven-file-collection-zip
description: Collect files listed in a plain-text manifest (one relative path per line) from anywhere under a root directory and package them into a single flat, timestamped zip archive with automatic duplicate-leaf-name suffixing and missing-path reporting, using a zero-dependency PowerShell tool that can be dropped into an arbitrary directory tree.
category: File Operations
---

# Manifest-Driven File Collection Zip Skill (v1)

Collect an explicit, curated set of files — named in a plain-text manifest — from anywhere under a
root directory and package them into one **flat, timestamped** zip archive. The defining traits are
deterministic selection (you list exactly the files you want, by relative path), flat output (every
collected file lands at the zip root, no directory nesting), safe de-duplication (two files with the
same leaf name are auto-suffixed `_1`, `_2`, …), and **zero external dependencies** so the tool runs
on any host with stock PowerShell 5.1+.

This is a **base skill**. Domain-specific collectors (build-artifact pickers, log bundlers, evidence
packagers) compose it by owning *which* paths go in the manifest while delegating the
collect-and-zip mechanics here. See **Composition by Higher-Level Skills** below.

***

## 1. When to Apply

Apply this skill when the task is:

- "Collect these specific files into a zip" where the file set is known and curated (not "zip the
  whole folder").
- "Bundle build outputs / logs / generated files for delivery or review."
- "Set up a reusable, re-runnable file-collection tool inside a project tree."
- Maintaining a pick list (add / remove / comment out paths) as the set of files of interest evolves.

Do **NOT** apply when:

- The user wants to archive an entire directory tree — use a plain `Compress-Archive <dir>` /
  archiver instead; a manifest is pointless.
- The user wants to preserve sub-directory structure inside the zip — this tool flattens by design.
- The user wants to copy files to a remote location — this tool is local-only.

***

## 2. Environment & Dependencies

| Requirement | Minimum |
| :--- | :--- |
| Shell | PowerShell 5.0+ (for `Compress-Archive`) |
| Permissions | Read access to every manifest path; write access to the output directory |
| Encoding | The script file MUST be ASCII (no characters above code point 127) for PowerShell 5.1 safety |

```powershell
# Verify Compress-Archive is available
Get-Command Compress-Archive -ErrorAction SilentlyContinue | Select-Object Name, Version
```

No modules, no submodules, no network. The tool is deliberately self-contained — see the `.NOTES`
exemption in the script.

***

## 3. The Script

The deterministic collect-and-zip mechanics live in
[scripts/Collect-ManifestFiles.ps1](scripts/Collect-ManifestFiles.ps1) (Tier 2 / PowerShell per
[Scripting Language Selection Rules §4](../../../ai-agent-rules/scripting-language-selection-rules.md)).

```powershell
# Default deployment: tool sits in a sub-folder, root = parent folder
.\Collect-ManifestFiles.ps1

# Explicit root + manifest + name prefix
.\Collect-ManifestFiles.ps1 -Root 'C:\builds\projX' -Manifest .\pick.txt -NamePrefix projX_logs
```

### 3.1 Parameters

| Parameter | Default | Meaning |
| :--- | :--- | :--- |
| `-Root` | Parent of the script's own directory | Directory that manifest-relative paths resolve against |
| `-Manifest` | `<ScriptBaseName>.txt` next to the script | Plain-text pick list, one relative path per line |
| `-OutputDir` | The script's own directory | Where the zip is written |
| `-NamePrefix` | Leaf name of `-Root` | Zip name prefix; final name is `<NamePrefix>_<yyyyMMdd_HHmmss>.zip` |

***

## 4. Manifest Format

One relative path per line, resolved against `-Root`. Blank lines and lines starting with `#` are
ignored, so comments and section headers are safe.

```text
# --- Logs ---
logs\build.log
logs\run.log

# --- Generated ---
out\artifacts\result.bin
```

***

## 5. Design Decisions (why it behaves this way)

| Decision | Rationale |
| :--- | :--- |
| Default root = parent of script dir | Supports the "drop a tool sub-folder into a project root" pattern with zero config |
| Manifest paths are relative | The manifest is portable across machines; no absolute paths baked in |
| Flat zip (no sub-dirs) | Simplifies downstream consumption of the collected files |
| Duplicate leaf names auto-suffixed `_1`, `_2` | Prevents silent overwrites when two paths share a leaf name |
| Timestamped zip name | Prevents overwrites across multiple runs |
| Missing paths warn but do not abort | A partial collection is still useful; the run surfaces the full missing list |
| ASCII-only source, zero dependencies | Runs on any stock PowerShell 5.1 host, including locked-down workstations |

***

## 6. Interpreting the Summary

```text
===== Manifest Collection Summary =====
  Root      : C:\builds\projX
  Collected : 5 file(s)
  Missing   : 0 file(s)
  Output    : C:\builds\projX\tool\projX_20260603_214519.zip
=======================================
```

If `Missing > 0`, the zip is still created for the collected files and the missing relative paths are
printed. Surface that list to the user — the root may not have been built yet, or a manifest path may
be wrong.

***

## 7. Troubleshooting

| Symptom | Cause | Resolution |
| :--- | :--- | :--- |
| `The string is missing the terminator` | Script saved BOM-less UTF-8 with non-ASCII chars; PS 5.1 reads it as ANSI | Recreate the script ASCII-only (replace `─`→`-`, `—`→`-`); verify no char > 127 |
| `Duplicate name '<x>' - saved as <x>_1` warning | Two manifest paths share a leaf name | Expected and safe — both files are kept, second is suffixed |
| `No files were collected` | Every manifest path was missing | Confirm `-Root` is correct and the source files exist |

```powershell
# ASCII verification
$content  = Get-Content '.\Collect-ManifestFiles.ps1' -Raw
$nonAscii = $content.ToCharArray() | Where-Object { [int]$_ -gt 127 }
$nonAscii.Count   # MUST be 0
```

***

## 8. Composition by Higher-Level Skills

This base is composed by domain-specific collectors that own only the manifest content (which paths
to pick) and delegate collection mechanics here:

| Composer | Repo | Domain binding it adds |
| :--- | :--- | :--- |
| `pver_pick_pointer` | `bosch_ai_agents` (org-private) | Build-tree root conventions + the curated set of build/log artifacts to collect |

A composer MUST reference this base by **prose path** (not a cross-repository relative link) when it
lives in a different repository, per the Standalone-Clone Test in the AI Rule Standardization Rules.

***

## 9. Prohibited Behaviors

- **Do not** preserve sub-directory structure — the contract is flat output.
- **Do not** zip an entire directory tree — that defeats the curated-manifest purpose.
- **Do not** abort the run on a missing path — collect what exists, report the rest.
- **Do not** introduce module/submodule/network dependencies — zero-dependency portability is the
  skill's reason to exist.
