# AGENTS.md

## Skills

| Skill | Path | When to use |
|---|---|---|
| Underscore Naming Convention | [`.agents/skills/underscore_naming/SKILL.md`](.agents/skills/underscore_naming/SKILL.md) | User asks to enforce underscore naming, or files/dirs with hyphens are detected |
| Maven POM Audit | [`.agents/skills/maven_pom_audit/SKILL.md`](.agents/skills/maven_pom_audit/SKILL.md) | User asks to audit pom.xml, or invalid URLs/developer identity detected |
| Project Structure & Documentation | [`.agents/skills/project_structure/SKILL.md`](.agents/skills/project_structure/SKILL.md) | User asks to organize project, fix folder structure, or create README/AGENTS.md |
| Deleted Files Audit | [`.agents/skills/deleted_files_audit/SKILL.md`](.agents/skills/deleted_files_audit/SKILL.md) | User deletes files and asks to verify, or `git status` shows pending deletions |
| LOC Analysis | [`.agents/skills/loc_analysis/SKILL.md`](.agents/skills/loc_analysis/SKILL.md) | User asks to calculate LOC, measure code changes, or quantify a feature's footprint |
| Gitignore Rules | [`.agents/skills/gitignore_rules/SKILL.md`](.agents/skills/gitignore_rules/SKILL.md) | User asks to audit `.gitignore`, or directory-ignore + negation patterns detected |
| Text to Markdown | [`.agents/skills/text_to_markdown/SKILL.md`](.agents/skills/text_to_markdown/SKILL.md) | User asks to convert plain-text data to markdown, or `.txt` files with delimiter-separated status data detected |
| Git Atomic Commit | [`.agents/skills/git_atomic_commit/SKILL.md`](.agents/skills/git_atomic_commit/SKILL.md) | User asks to commit changes, arrange commits, or stage and commit — working-tree changes need atomic grouping |
| Git History Refinement | [`.agents/skills/git_history_refinement/SKILL.md`](.agents/skills/git_history_refinement/SKILL.md) | User asks to refine, split, or reconstruct existing commit history |
| Git Rebase | [`.agents/skills/git_rebase/SKILL.md`](.agents/skills/git_rebase/SKILL.md) | User asks to rebase branches, manage multi-branch chains, or deduplicate cross-branch commits |
| Commit Edit | [`.agents/skills/commit_edit/SKILL.md`](.agents/skills/commit_edit/SKILL.md) | User asks to edit, fix, or remove files from an existing commit via interactive rebase |
| Noise Removal via Commit Edit | [`.agents/skills/noise_removal_via_commit_edit/SKILL.md`](.agents/skills/noise_removal_via_commit_edit/SKILL.md) | User asks to remove IDE artifact noise (m2e `.project`, `.classpath`, `.settings/`) from an existing commit |
| Anti Gravity Version Checker | [`.agent/skills/antigravity-version-checker/SKILL.md`](.agent/skills/antigravity-version-checker/SKILL.md) | Audit Anti Gravity vs VS Code versions and feature parity |
| Code Explanation | [`.agent/skills/code-explanation/SKILL.md`](.agent/skills/code-explanation/SKILL.md) | Deep-dive, pedagogical code documentation standards |
| Folder Comparison | [`.agent/skills/folder-comparison/SKILL.md`](.agent/skills/folder-comparison/SKILL.md) | Compare directories for content-level consistency |
| Harper Linting Suppression | [`.agent/skills/harper-linting-suppression/SKILL.md`](.agent/skills/harper-linting-suppression/SKILL.md) | Protocol for addressing Harper linter false positives |
| Mise Tool Management | [`.agent/skills/mise-tool-management/SKILL.md`](.agent/skills/mise-tool-management/SKILL.md) | Protocols for mise configuration trust and tool version selection |
| Python Script Generation | [`.agent/skills/python-script-generation/SKILL.md`](.agent/skills/python-script-generation/SKILL.md) | Standards for generating "Ultra-Lean Industrial" Python scripts |
| System-Wide Tool Management | [`.agent/skills/system-wide-tool-management/SKILL.md`](.agent/skills/system-wide-tool-management/SKILL.md) | Protocol for detecting and installing system-wide CLI tools |
| Redaction & Portability | [`.agents/skills/redaction_portability/SKILL.md`](.agents/skills/redaction_portability/SKILL.md) | Protocol for addressing, redacting, and relativizing sensitive/absolute information in artifacts |

## Conventions

- Underscore naming for author-chosen files and directories
- Kebab-case for files in `ai-agent-rules/` (per `ai-rule-standardization-rules.md`)
- See [README.md](README.md) for project overview
