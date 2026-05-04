# GitHub Secrets Bulk Set — Agent Companion Bridge

This file is the **passive context bridge** for the GitHub Secrets Bulk Set skill.

For all active instructions, tooling, and operational logic, defer entirely to:

**[SKILL.md](./SKILL.md)**

***

## When to Activate This Skill

The agent MUST activate the **GitHub Secrets Bulk Set** skill when ANY of the following is detected:

- User asks to set, update, or sync GitHub repository secrets.
- A `.env`, `.env.local`, `act.secrets`, or similar secrets file is referenced alongside a GitHub repository.
- User mentions `gh secret set`, `--env-file`, or GitHub Actions secret management.
- User wants to mirror local secrets into a GitHub repository or environment.

***

## Quick Reference

```bash
# Bulk set repository secrets from a .env-style file
gh secret set --repo <OWNER>/<REPO> --env-file <PATH_TO_SECRETS_FILE>

# Verify secrets were written
gh secret list --repo <OWNER>/<REPO>
```

> [!IMPORTANT]
> Keys starting with `GITHUB_` are rejected by the GitHub API (HTTP 422). Always rename such keys
> before running the bulk import. See [SKILL.md](./SKILL.md) §3 for full naming constraints.
