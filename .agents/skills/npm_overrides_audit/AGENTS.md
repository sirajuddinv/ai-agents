# AGENTS.md (NPM Overrides Audit & Correction)

Refer to [SKILL.md](./SKILL.md) for the active operational protocol for auditing,
testing, and correcting unnecessary overrides in `package.json` to simplify
dependency resolution and reduce hidden constraints.

## Mandates

- **Individual Testing**: Each override MUST be tested in isolation by removing it
  and regenerating the lock file independently.
- **Atomic Commits**: Each override removal (or retention decision) is committed
  individually with clear rationale.
- **Lock File Authority**: Lock file regeneration success/failure is the sole
  criterion for override necessity determination.
- **Zero Data Loss**: Original package.json and lock files are backed up before
  any testing begins.
- **Simplified Resolution**: Remove unnecessary overrides to give npm full flexibility
  in dependency resolution and reduce implicit project constraints.

## When to Invoke

- User specifies: "audit overrides" or "are these overrides needed?"
- User asks: "test each override" or "clean up overrides"
- Working tree contains `package.json` with `overrides` field
- Project wants to simplify dependency resolution
- Post-dependency-pinning audit and cleanup

## Success Criteria

✓ Each override tested individually one-by-one  
✓ Lock file regenerates cleanly for each test  
✓ Unnecessary overrides removed with individual commits  
✓ Rationale documented for any retained overrides  
✓ Empty overrides section removed from package.json  
✓ Git history shows clear audit trail  

## Related Skills

- [Package Version Correction](../package_version_correction/SKILL.md) — Pin all dependencies to exact versions
- [Git Atomic Commit](../git_atomic_commit/SKILL.md) — Ensure each override change is atomic
- [Markdown Generation](../markdown_generation/SKILL.md) — Document override audit results
- [Skill Factory](../skill_factory/SKILL.md) — Reference for this skill's creation
