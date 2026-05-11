---
name: git-github-auth-fallback
description: Industrial protocol for recovering from git push / fetch authentication failures against GitHub (HTTP 401 / 403) when credentials are missing, stale, or bound to the wrong identity — covers Credential Manager reset, Personal Access Token re-issue, SSH remote swap, and gh CLI re-authentication.
category: Git-Auth
---

# Git / GitHub Auth Fallback Skill (v1)

This skill defines the recovery protocol when a Git operation against a GitHub remote fails with an
authentication or authorization error — typically `remote: Permission to <owner>/<repo>.git denied to <user>`
or `fatal: ... The requested URL returned error: 403` on `git push`, `git fetch`, or `git ls-remote`.

The root cause is almost never "the repo is wrong"; it is one of:

1. No credentials cached for the remote at all (401).
2. Credentials cached for the **wrong GitHub identity** (the most common cause on shared / work machines —
   surfaces as 403 even though the URL is correct).
3. PAT scope insufficient or PAT expired / revoked.
4. SSH key not loaded into the agent or not associated with the active GitHub account.
5. `gh` CLI authenticated under a different account than the credential helper.

***

## 1. Environment & Dependencies

```powershell
git --version
git config --get credential.helper
git config --global --get user.email
```

Identify the credential helper in use:

- **`manager-core` / `manager`** — Git Credential Manager (default on Windows; also on macOS / Linux via install).
- **`osxkeychain`** — macOS native keychain.
- **`libsecret`** / **`store`** / **`cache`** — Linux options.
- **(empty)** — No helper; Git will prompt every time or fail in non-TTY contexts (e.g., VS Code tasks per
  [Terminal Fallback via VS Code Tasks](../terminal-fallback-via-vscode-tasks/SKILL.md) §4.4).

If the helper is empty AND the agent is running inside a VS Code task (no TTY), the agent MUST stop and surface
the situation to the user — auth fixes for `manager-core` / `osxkeychain` REQUIRE an interactive UI.

***

## 2. Diagnosis (MUST run before any fix)

Before attempting any remediation, classify the failure exactly:

### 2.1 Capture the remote and the exact error

```powershell
git -C <repo> remote -v
git -C <repo> push <remote> <branch> 2>&1 | Out-File .auth_probe.txt -Encoding utf8
```

Inspect `.auth_probe.txt` for one of these signatures:

| Signature | Classification |
| :--- | :--- |
| `fatal: Authentication failed` | 401 — no credentials, or credentials rejected. |
| `remote: Permission to <owner>/<repo>.git denied to <other-user>` | 403 — wrong identity cached. **Most common on work machines.** |
| `remote: Write access to repository not granted` | 403 — correct identity, missing write scope or collaborator role. |
| `ERROR: Repository not found` (with SSH) | SSH key not associated with the account, OR repo is private and the key has no access. |
| `Could not resolve host: github.com` | Not auth — network / proxy. Out of scope for this skill. |

### 2.2 Identify which GitHub identity Git is offering

For HTTPS remotes via Credential Manager:

```powershell
# Credential Manager GUI on Windows — list stored entries:
git credential-manager get
# Paste the following on stdin, then hit Enter twice:
#   protocol=https
#   host=github.com
# The helper returns the username it would use.
```

For SSH remotes, ask the SSH agent which key would be offered:

```bash
ssh -T git@github.com -v 2>&1 | head -40
```

The verbose output includes `Hi <username>! You've successfully authenticated...` if a key is found, or
`Permission denied (publickey)` if not.

***

## 3. Remediation Paths (Pick One)

Each path is a complete, standalone fix. The agent MUST present the options to the user, recommend one based on
the diagnosis, and proceed only after the user confirms.

### 3.1 Path A — Reset Credential Manager and re-authenticate (RECOMMENDED for "wrong identity" 403)

> [!CAUTION]
> This path is interactive — it requires the user to run the commands in a real terminal, not inside a VS Code
> task. The agent MUST surface the commands and wait for confirmation.

```powershell
# Windows
git credential-manager erase
# Paste on stdin:
#   protocol=https
#   host=github.com
# (Enter twice)

# Then trigger the next push, which will open the GCM browser prompt:
git -C <repo> push <remote> <branch>
# Sign in as the correct account in the browser window that opens.
```

```bash
# macOS (osxkeychain helper)
git credential-osxkeychain erase <<EOF
protocol=https
host=github.com
EOF

# Linux (libsecret / store)
git credential-libsecret erase <<EOF
protocol=https
host=github.com
EOF
```

After re-auth, re-probe with `git push` and verify the captured output shows success.

### 3.2 Path B — Personal Access Token in the remote URL (NON-INTERACTIVE)

When the agent must complete the push inside a non-TTY environment (e.g., CI, VS Code task), embed a PAT
directly. The token MUST come from an environment variable and MUST NEVER be committed.

```powershell
$env:GITHUB_PAT = '<user-paste-pat-here>'
git -C <repo> remote set-url <remote> "https://$env:GITHUB_PAT@github.com/<owner>/<repo>.git"
git -C <repo> push <remote> <branch>
# IMMEDIATELY revert the URL so the PAT does not persist in .git/config:
git -C <repo> remote set-url <remote> "https://github.com/<owner>/<repo>.git"
```

> [!CAUTION]
> The PAT lives in `.git/config` between the `set-url` and the revert. The agent MUST execute the revert in the
> same task / same shell session as the push to minimize exposure. NEVER capture the URL form with the PAT
> embedded into a log file, commit message, or session note — this is a Tier-A redaction violation per
> [Redaction & Portability](../redaction-portability/SKILL.md) §1.

The PAT must have scope:

- **`repo`** — for write access to private repos and to public repos when you are not a collaborator.
- **`workflow`** — for pushing changes that modify `.github/workflows/*`.

### 3.3 Path C — Switch the remote to SSH

When the user has an SSH key already associated with the correct GitHub account, swap the protocol:

```powershell
git -C <repo> remote set-url <remote> "git@github.com:<owner>/<repo>.git"
git -C <repo> push <remote> <branch>
```

Verify the key is loaded:

```bash
ssh-add -L                   # Lists keys currently held by the agent.
ssh -T git@github.com        # Prints "Hi <user>!" on success.
```

If `ssh-add -L` reports "The agent has no identities", load the key:

```bash
ssh-add ~/.ssh/id_ed25519
```

For permanent SSH key registration on GitHub, see <https://github.com/settings/keys>.

### 3.4 Path D — Re-authenticate via `gh` CLI

When `gh` is installed, it can manage credentials for both itself and for Git (via `gh auth setup-git`):

```bash
gh auth status
gh auth login                # Interactive — browser or token paste.
gh auth setup-git            # Configures git's credential helper to defer to gh.
git -C <repo> push <remote> <branch>
```

If `gh` is absent, install it via [System-Wide Tool Management](../system-wide-tool-management/SKILL.md), or
fall back to Path A / B / C.

### 3.5 Path E — Validate a PAT without git (REST API probe)

Before retrying a push, the agent can validate a candidate PAT via the GitHub REST API:

```powershell
$Headers = @{
  'User-Agent'    = 'copilot-agent'
  'Authorization' = "Bearer $env:GITHUB_PAT"
}
Invoke-RestMethod -Uri 'https://api.github.com/user' -Headers $Headers `
  | ConvertTo-Json -Depth 3 | Out-File .pat_probe.txt -Encoding utf8
```

The response object's `login` field is the GitHub username the PAT belongs to. If `login` does NOT match the
account that owns / has write access to the target repo, the PAT is wrong — go back to step 1 of the chosen
path. For full REST patterns, defer to [GitHub REST API Fallback](../github-rest-api-fallback/SKILL.md).

***

## 4. Decision Matrix

| Scenario | Recommended Path | Rationale |
| :--- | :--- | :--- |
| Work laptop, Credential Manager cached a corp / coworker identity, push to personal repo → 403 | A (reset & re-auth) | Cleanest; future pushes auto-resolve. |
| CI / VS Code task / non-TTY environment, must push now | B (PAT in URL, immediately reverted) | Only non-interactive option. |
| User already has SSH keys, hates browser prompts | C (SSH remote) | No credentials in HTTPS layer at all. |
| User wants `gh`-managed flow for `pr create`, `issue`, etc. anyway | D (`gh auth login`) | Single helper for both git push and GitHub API. |
| Uncertain whether the PAT has the right scope | E first, then B or A | Cheap pre-flight check before mutating remote URL. |

***

## 5. Verification

After remediation, the push MUST produce visible success output:

```powershell
git -C <repo> push <remote> <branch> 2>&1 | Out-File .auth_verify.txt -Encoding utf8
# Inspect .auth_verify.txt for one of:
#   "Everything up-to-date"  (no commits to push but auth worked)
#   "To <url>"                followed by ref update lines
```

Additionally, confirm the working tree's tracking branch is in sync:

```powershell
git -C <repo> status -sb
# Expect: ## <branch>...<remote>/<branch>   (no [ahead N])
```

***

## 6. Composition by Higher-Level Skills

| Composer | Role | Reuses From This Skill |
| :--- | :--- | :--- |
| [`git-submodule-fork-reconfigure`](../git-submodule-fork-reconfigure/SKILL.md) | When `git push` to an upstream fails with 403, distinguish "needs forking" from "wrong identity cached". | §2 diagnosis matrix, §3 remediation paths. |
| [`git-submodule-fork-sync`](../git-submodule-fork-sync/SKILL.md) | Push to the realigned `origin` may surface a 401 / 403. | §2 classification before forking or reconfiguring further. |
| [`git-submodule-orphan-gitlink-recovery`](../git-submodule-orphan-gitlink-recovery/SKILL.md) | Auth failures while reconfiguring orphan gitlinks. | §2 classification, §3 remediation. |
| [`git-branch-promotion`](../git-branch-promotion/SKILL.md) | Force-push step blocked by auth. | §3 paths to restore push capability before §4 force-push. |
| [`github-secrets-bulk-set`](../github-secrets-bulk-set/SKILL.md) | `gh secret set` fails with 401 / 403. | §3.4 / §3.5 PAT validation. |
| [`jira-acli-operations`](../jira-acli-operations/SKILL.md) | `gh pr create` fails on the PR step. | §3.4 `gh auth login` flow. |

***

## 7. Related Skills

- [Terminal Fallback via VS Code Tasks](../terminal-fallback-via-vscode-tasks/SKILL.md) — §4.4 explicitly
  forbids running interactive credential-manager commands inside a task. This skill defers to that constraint
  by surfacing interactive paths back to the user.
- [GitHub REST API Fallback](../github-rest-api-fallback/SKILL.md) — Used for Path E (PAT validation) and any
  follow-up GitHub operation once auth is restored.
- [System-Wide Tool Management](../system-wide-tool-management/SKILL.md) — Use to install `gh`, `git`, or SSH
  key tooling if missing.
- [Redaction & Portability](../redaction-portability/SKILL.md) — Mandatory: PATs, account usernames, and
  internal-org email addresses are all Tier-A and MUST be redacted before any artifact is committed.

***

## 8. Traceability

- Originating session: May 2026 — `git push` of `ai-agent-rules` failed with `HTTP 403` because Git Credential
  Manager on a work laptop was supplying credentials for the corp identity instead of the personal GitHub
  account that owns the fork. The resolution required identifying the cached identity, then switching to a
  fork-based remote (per [Git Submodule Fork Reconfigure](../git-submodule-fork-reconfigure/SKILL.md)) under
  the correct account.
