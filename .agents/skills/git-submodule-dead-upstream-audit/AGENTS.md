# git-submodule-dead-upstream-audit

This skill audits a Git submodule whose upstream URL is suspected to be unreachable. It probes the remote, inspects
local cached history under `.git/modules/<PATH>`, and searches GitHub (authenticated) for forks or mirrors that
still hold the recorded commit SHA, then issues a removal-or-recovery verdict.

It should be invoked whenever a submodule operation fails with `404`, `not found`, `repository unavailable`, when
`git submodule update --init` hangs across many dead URLs, or when the user asks to verify whether a submodule's
upstream still exists before removing it.

- **Primary Entry Point**: [.agents/skills/git-submodule-dead-upstream-audit/SKILL.md](./SKILL.md)
- **Verdict Engine**: §5 *Verdict Matrix* — five-row decision table mapping probe results to the next skill.
- **Downstream Skills**:
    - [`git-submodule-removal`](../git-submodule-removal/SKILL.md) — when the verdict is **Unrecoverable**.
    - [`git-submodule-fork-reconfigure`](../git-submodule-fork-reconfigure/SKILL.md) — when a fork or mirror
      validates the recorded SHA.
