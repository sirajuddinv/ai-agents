# AGENTS.md (Unused Dependencies Audit & Removal)

Refer to [SKILL.md](./SKILL.md) for the active operational protocol for comprehensive
auditing of JavaScript/TypeScript dependencies, detecting actual code usage via import
scanning, identifying unused packages, and safely removing them with build validation.

## Mandates

- **Comprehensive Scanning**: All source directories must be scanned with
  multi-pattern import matching (ES6, CommonJS, dynamic imports).
- **One-by-One Removal**: Each unused candidate tested individually with lock file
  regeneration and build validation.
- **False-Positive Protection**: High-risk packages (webpack loaders, babel plugins,
  CLI tools) require manual investigation before removal.
- **Build Validation**: Successful build is the ONLY criterion for removal safety.
- **Atomic Commits**: Each package removal committed individually with clear rationale.
- **Audit Trail**: Complete traceability of what was removed and why.

## When to Invoke

- User asks: "find unused packages" or "remove unused dependencies"
- User specifies: "audit what packages are actually used"
- Project shows accumulated dependencies over many commits
- Dependency cleanup and modernization desired
- Install size/time optimization is a goal

## Success Criteria

✓ All source files scanned for import statements  
✓ Ambiguous packages manually reviewed before removal  
✓ Each unused candidate builds successfully after removal  
✓ No runtime or build-time errors introduced  
✓ Unused packages removed with atomic commits  
✓ Extraneous packages cleaned  
✓ node_modules size reduced  

## Related Skills

- [Package Version Correction](../package_version_correction/SKILL.md) — Pin dependencies to exact versions
- [NPM Overrides Audit](../npm_overrides_audit/SKILL.md) — Remove unnecessary override constraints
- [Git Atomic Commit](../git_atomic_commit/SKILL.md) — Ensure each removal is atomic
- [Markdown Generation](../markdown_generation/SKILL.md) — Document audit results
- [Skill Factory](../skill_factory/SKILL.md) — Reference for this skill's creation
