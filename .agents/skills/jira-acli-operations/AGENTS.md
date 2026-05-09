# Jira acli Operations

Companion skill for automating Jira ticket creation and PR link commenting
via the `acli` CLI.

## Quick Reference

- **Skill SSOT:** [SKILL.md](./SKILL.md)
- **Scripts:** (none yet)

## When to Apply

Use this skill when:
- Creating new Jira work items under an epic
- Commenting GitHub PR URLs on Jira tickets
- Automating repetitive Jira operations via `acli`
- Standardizing Jira ticket descriptions across a project

## Key Standards

- Always include PR Link, Project, and Epic sections in descriptions
- Always comment PR URLs on corresponding Jira tickets for traceability
- Authentication must be verified before any operation
- Description templates use Atlassian Wiki Format (h2., h3., [Link|URL])
