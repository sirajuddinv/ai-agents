# AGENTS.md — Terminal Fallback via VS Code Tasks

This directory hosts the **Terminal Fallback via VS Code Tasks** skill. The active SSOT is [`SKILL.md`](SKILL.md).

## Passive Context

- **When to engage**: The agent's primary `run_in_terminal` tool is unavailable, but `create_and_run_task` is.
- **Inputs**: A shell command + an absolute workspace folder path.
- **Outputs**: Captured stdout/stderr in a workspace-relative dot-prefixed file that the agent reads through
  `read_file`.
- **Key risks**: Truncated task display masking real errors, PowerShell quoting hostility, task-shell reuse
  bleeding output across calls, and the no-TTY constraint blocking interactive commands.

For full operational logic, defer to [`SKILL.md`](SKILL.md).
