# AGENTS.md (Package Version Correction)

Refer to [SKILL.md](./SKILL.md) for the active operational protocol for auditing,
extracting, and correcting package version specifications in `package.json` to use
exact, pinned versions from lock files.

## Mandates

- **Exact Versions Only**: Replace all range specifiers (`^`, `~`, `>=`, etc.) with
  exact pinned versions extracted from the authoritative lock file.
- **Lock File Authority**: The lock file (`package-lock.json`, `yarn.lock`,
  `pnpm-lock.yaml`) is the single source of truth for version extraction.
- **Zero Package Changes**: Correction MUST NOT add new packages or modify package names.
  Only version specifications are updated.
- **Lock File Regeneration**: After updating `package.json`, regenerate the lock file
  to ensure consistency and catch any potential conflicts.
- **Reproducible Builds**: Exact versions guarantee that `npm install` (or equivalent)
  produces identical environments across all systems and deployments.

## When to Invoke

- User specifies: "use exact versions," "pin all dependencies," "replace `^` with exact"
- Command: `git commit ... # after fixing package versions`
- Working tree contains `package.json` with version ranges and a valid lock file
- Post-dependency addition validation is required

## Success Criteria

✓ All packages in `dependencies` and `devDependencies` use exact versions  
✓ Lock file regenerated without adding new packages  
✓ Optional linting passes  
✓ Changes ready for git commit  

## Related Skills

- [Git Atomic Commit](../git_atomic_commit/SKILL.md) — Commit corrected dependencies
- [Markdown Generation](../markdown_generation/SKILL.md) — Document version audit results
- [Skill Factory](../skill_factory/SKILL.md) — Reference for this skill's creation
