# AGENTS.md — Git / GitHub Auth Fallback

This directory hosts the **Git / GitHub Auth Fallback** skill. The active SSOT is [`SKILL.md`](SKILL.md).

## Passive Context

- **When to engage**: `git push`, `git fetch`, or `git ls-remote` returns HTTP 401 / 403 against a GitHub
  remote, OR `gh` operations fail with `Bad credentials`.
- **Inputs**: The failing remote URL, the captured error text, the user's intended GitHub identity.
- **Outputs**: Restored push / fetch capability under the correct identity.
- **Key risks**: Embedding a PAT in `.git/config` and forgetting to revert it; committing a PAT-bearing URL to
  history; running interactive credential-manager commands inside a no-TTY task (will hang).

For full operational logic, defer to [`SKILL.md`](SKILL.md).
