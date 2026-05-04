# AGENTS.md (Python Virtual Environment Repair)

Refer to [SKILL.md](./SKILL.md) for the active operational protocol for detecting,
diagnosing, and repairing broken Python virtual environments.

## Mandates

- **Diagnose Before Acting**: MUST audit ALL symlinks, `pyvenv.cfg`, and available
  interpreters before proposing any fix.
- **Zero Omission**: MUST NOT skip any layer of the 5-layer protocol.
- **User Decision Gate**: MUST present repair options with priority ordering and wait
  for user confirmation before modifying any venv.
- **Relative Symlinks Only**: MUST use `ln -s python3` (relative) — never absolute
  paths that will break on Homebrew upgrades.
- **Redaction & Portability**: Apply the [Redaction & Portability Skill](../redaction_portability/SKILL.md)
  to all generated artifacts.
