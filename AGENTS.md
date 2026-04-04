# AGENTS.md

## Skills

| Skill | Path | When to use |
| :--- | :--- | :--- |
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
| Git Repository Status | [`.agents/skills/git_repository_status/SKILL.md`](.agents/skills/git_repository_status/SKILL.md) | Industrial protocol for auditing branch divergence, staged/unstaged changes, and repository history |
| Commit Edit | [`.agents/skills/commit_edit/SKILL.md`](.agents/skills/commit_edit/SKILL.md) | User asks to edit, fix, or remove files from an existing commit via interactive rebase |
| Git Commit Details Audit | [`.agents/skills/git_commit_details_audit/SKILL.md`](.agents/skills/git_commit_details_audit/SKILL.md) | Industrial protocol for retrieving and analyzing high-fidelity commit metadata, hunks, and pedagogical explanations |
| Git Commit Comparison Audit | [`.agents/skills/git_commit_comparison_audit/SKILL.md`](.agents/skills/git_commit_comparison_audit/SKILL.md) | User asks to compare two commits, or submodule pointer mismatches are detected |
| Noise Removal via Commit Edit | [`.agents/skills/noise_removal_via_commit_edit/SKILL.md`](.agents/skills/noise_removal_via_commit_edit/SKILL.md) | User asks to remove IDE artifact noise (m2e `.project`, `.classpath`, `.settings/`) from an existing commit |
| Anti Gravity Version Checker | [`.agent/skills/antigravity-version-checker/SKILL.md`](.agent/skills/antigravity-version-checker/SKILL.md) | Audit Anti Gravity vs VS Code versions and feature parity |
| Code Explanation | [`.agent/skills/code-explanation/SKILL.md`](.agent/skills/code-explanation/SKILL.md) | Deep-dive, pedagogical code documentation standards |
| Folder Comparison | [`.agent/skills/folder-comparison/SKILL.md`](.agent/skills/folder-comparison/SKILL.md) | Compare directories for content-level consistency |
| Harper Linting Suppression | [`.agent/skills/harper-linting-suppression/SKILL.md`](.agent/skills/harper-linting-suppression/SKILL.md) | Protocol for addressing Harper linter false positives |
| Mise Tool Management | [`.agent/skills/mise-tool-management/SKILL.md`](.agent/skills/mise-tool-management/SKILL.md) | Protocols for mise configuration trust and tool version selection |
| Python Script Generation | [`.agent/skills/python-script-generation/SKILL.md`](.agent/skills/python-script-generation/SKILL.md) | Standards for generating "Ultra-Lean Industrial" Python scripts |
| System-Wide Tool Management | [`.agent/skills/system-wide-tool-management/SKILL.md`](.agent/skills/system-wide-tool-management/SKILL.md) | Protocol for detecting and installing system-wide CLI tools |
| Redaction & Portability | [`.agents/skills/redaction_portability/SKILL.md`](.agents/skills/redaction_portability/SKILL.md) | Protocol for addressing, redacting, and relativizing sensitive/absolute information in artifacts |
| Markdown Generation | [`.agents/skills/markdown_generation/SKILL.md`](.agents/skills/markdown_generation/SKILL.md) | Industrial protocol for generating lint-compliant, high-fidelity markdown documentation |
| Skill Factory | [`.agents/skills/skill_factory/SKILL.md`](.agents/skills/skill_factory/SKILL.md) | Industrial protocol for automated creation of "Skill-First" AI Agent skills with high fidelity |
| Rule-to-Skill Industrialization | [`.agents/skills/rule_to_skill_industrialization/SKILL.md`](.agents/skills/rule_to_skill_industrialization/SKILL.md) | User asks to transform a rule into a skill, perform gap analysis, or promote a rule to SSOT |
| MCP Server Management | [`.agents/skills/mcp-management/SKILL.md`](.agents/skills/mcp-management/SKILL.md) | Industrial protocol for adding, configuring, and verifying MCP servers |
| GitHub Secrets Bulk Set | [`.agents/skills/github_secrets/SKILL.md`](.agents/skills/github_secrets/SKILL.md) | Industrial protocol for setting GitHub repository (or environment) secrets in bulk from a local .env-style secrets file using the `gh` CLI |
| JSON Deep Sort | [`.agents/skills/json-deep-sort/SKILL.md`](.agents/skills/json-deep-sort/SKILL.md) | Alphabetically sorts primitive JSON arrays and recursively applies sort_keys=True for unified dictionary ordering safely natively |
| VS Code Extension Link Portability | [`.agents/skills/vscode_extension_portability/SKILL.md`](.agents/skills/vscode_extension_portability/SKILL.md) | Refactor non-portable extension-linked paths in settings.json to permanent, portable links using tilde |
| VS Code Settings Promotion | [`.agents/skills/vscode_settings_promotion/SKILL.md`](.agents/skills/vscode_settings_promotion/SKILL.md) | Automate migration of profile-specific settings to global scope with universal enforcement |
| Git Submodule Pointer Repair | [`.agents/skills/git_submodule_pointer_repair/SKILL.md`](.agents/skills/git_submodule_pointer_repair/SKILL.md) | Industrial protocol for surgically fixing invalid submodule pointers in parent repository history using the Synchronization Horizon algorithm |
| Git Submodule Removal | [`.agents/skills/git_submodule_removal/SKILL.md`](.agents/skills/git_submodule_removal/SKILL.md) | Industrial protocol for the atomic and complete removal of Git submodules, purging all tracking and meta-data |
| Git Submodule Addition | [`.agent/skills/git_submodule_addition/SKILL.md`](.agent/skills/git_submodule_addition/SKILL.md) | Automate adding Git submodules with standardized naming and initialization |
| Re-add Git Submodule | [`.agents/skills/readd_git_submodule/SKILL.md`](.agents/skills/readd_git_submodule/SKILL.md) | Industrial protocol for removing and re-adding Git submodules to standardize paths or repair configurations |
| Git Submodule Fork Sync | [`.agents/skills/git_submodule_fork_sync/SKILL.md`](.agents/skills/git_submodule_fork_sync/SKILL.md) | Automates the realignment of `.gitmodules` to track internal submodule forks while securing origin upstreams |
| Git Divergence Audit | [`.agents/skills/git_divergence_audit/SKILL.md`](.agents/skills/git_divergence_audit/SKILL.md) | Industrial protocol for surgical, unit-by-unit comparison of diverged local and remote branches |

## Conventions

- Underscore naming for author-chosen files and directories
- Kebab-case for files in `ai-agent-rules/` (per `ai-rule-standardization-rules.md`)
- See [README.md](README.md) for project overview
