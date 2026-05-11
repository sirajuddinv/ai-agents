# AGENTS.md — GitHub REST API Fallback

This directory hosts the **GitHub REST API Fallback** skill. The active SSOT is [`SKILL.md`](SKILL.md).

## Passive Context

- **When to engage**: `gh` CLI is missing / unauthenticated / failing, but the agent still needs to query or
  mutate GitHub resources.
- **Inputs**: An endpoint path, optional PAT in `$env:GITHUB_TOKEN`, an output capture file (when chained with
  the terminal-fallback skill).
- **Outputs**: JSON response captured to a workspace-relative file, ready for `read_file`.
- **Key risks**: Missing `User-Agent` header (403), rate-limit exhaustion, accidentally embedding a PAT in
  committed artifacts, untrusted TLS on older Windows PowerShell.

For full operational logic, defer to [`SKILL.md`](SKILL.md).
