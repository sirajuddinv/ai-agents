---
name: redaction-portability
description: Industrial protocol for addressing, redacting, and relativizing sensitive/absolute information in workspace artifacts — covers paths, identities, network topology, organizational identifiers, file-naming hygiene, and a canonical placeholder vocabulary so every produced artifact is safe to publish and portable across machines.
category: Security-Standards
---

# Redaction & Portability Skill (v2)

This skill is the **single source of truth (SSOT)** for sanitising any
workspace artifact before it leaves the author's machine — be it a
committed skill `SKILL.md`, a conversation log under `docs/conversations/`,
a case study under `docs/cases/`, a commit message body, a generated
report, or a pull-request description.

It exists because:

1. AI-agent sessions naturally capture **machine-specific, identity-bearing,
   and organization-specific** strings (paths, usernames, proxy hosts,
   internal repository URLs, vendor product codenames, license keys,
   email addresses, ticket IDs).
2. Those strings have a strong bias toward leaking into committed
   artifacts because agents are trained to be *faithful* to the
   transcript — fidelity is a virtue inside the working session but a
   liability once the artifact is published.
3. Manual redaction is error-prone; this skill provides a **mechanical,
   audit-friendly** procedure that any agent can re-apply to any
   artifact at any time.

---

## 0. Scope

This skill applies to:

- Every file under `.agents/skills/**/SKILL.md`, `AGENTS.md`, `docs/`
- Every file under `ai-agent-rules/**/*.md`
- Every commit message body (subject, body, trailers)
- Every PR / issue description authored by the agent
- Every generated report (markdown, JSON, CSV) intended for publication

It does NOT apply to:

- Per-developer local config (`~/.m2/settings.xml`,
  `~/.ssh/config`, IDE preferences) — these are intentionally
  machine-specific and never committed.
- Files explicitly gitignored.
- Build outputs / logs that are not committed.

---

## 1. The Three Sensitivity Tiers

Every string the agent emits falls into one of three tiers. The required
treatment differs per tier.

### Tier A — Identity & Credentials (always redact)

| Class | Examples | Replacement |
|---|---|---|
| Personal name (human author) | real human names | `<author>` or `[REDACTED_NAME]` |
| Username on a developer machine | OS account names | `<user>` |
| Email address | `firstname.lastname@example.com` | `<author-email>` |
| Auth token, API key, password | any opaque secret string | `<redacted-secret>` (NEVER leave plaintext) |
| Personal IP address / MAC | `10.x.y.z`, `aa:bb:cc:dd:ee:ff` | `<host-ip>`, `<mac>` |
| Personal SSH public-key fingerprint | `SHA256:…` | `<ssh-fingerprint>` |
| Cloud account / subscription ID | UUIDs in URLs / tooling output | `<account-id>` |

### Tier B — Machine & Organization Topology (redact unless universally true)

| Class | Examples | Replacement |
|---|---|---|
| Absolute filesystem path on author's machine | `C:\Users\<user>\…`, `/home/<user>/…` | `<workspace-root>`, `<user-home>`, `~/…` |
| Drive letter or mount point | `C:\<shared-tool-root>\…`, `/mnt/build/…` | `<toolbase>`, `<build-mount>` |
| Corporate proxy host & port | internal proxy FQDN + port | `<corp-proxy-host>:<corp-proxy-port>` |
| Corporate domain / TLD | `*.<corp>.com`, `*.<corp-cloud>.com` | `<corp-domain>`, `<corp-cloud-domain>` |
| Internal repository URL | `https://<internal-vcs>/<team>/<repo>` | `<internal-vcs>/<team>/<repo>` |
| Internal artifact repository | `https://<internal-nexus>/…` | `<internal-artifact-repo>` |
| Internal CI/CD endpoint | `https://<internal-ci>/job/…` | `<internal-ci>` |
| Internal ticketing | `https://<ticket-system>/browse/PROJ-1234` | `<ticket-system>/<TICKET-ID>` |
| VPN / network zone names | `corp-vpn-east`, `dmz-build-net` | `<vpn>`, `<network-zone>` |
| Internal SMTP / chat hosts | internal mail/chat FQDNs | `<internal-mail>`, `<internal-chat>` |
| Vendor product codename (internal) | unreleased project names, NDA codenames | `<product-codename>` |
| Customer / client name | external customer names | `<customer>` |
| License key / dongle ID | opaque license strings | `<license-key>` |

### Tier C — Public / Universal (keep verbatim)

These are universally true; redacting them harms reproducibility:

- Public domain names: `repo.maven.apache.org`, `github.com`,
  `central.sonatype.com`
- Open-source project / artifact names: `commons-io`, `Eclipse Orbit`,
  `Apache Tycho`, `Adoptium Temurin`
- Open-source bundle symbolic names: `org.apache.commons.commons-io`
- Standard tool flags, JVM options, OSGi headers
- Standard local-machine reserved names: `127.0.0.1`, `localhost`,
  `0.0.0.0`
- Standard env var names: `HTTP_PROXY`, `JAVA_HOME`, `USERPROFILE`
- Standard CLI commands

The rule of thumb: **if a competent reader on a different machine /
different organization would benefit from the literal string, keep it.
Otherwise, redact.**

---

## 2. Canonical Placeholder Vocabulary

A controlled vocabulary makes redaction *predictable* and *searchable*
(future agents can grep for `<workspace-root>` to find every site that
needs a per-machine substitution).

### 2.1 Path placeholders

| Placeholder | Meaning |
|---|---|
| `<workspace-root>` | Root of the workspace this agent is inspecting |
| `<workspace-root-21>`, `<workspace-root-N>` | Disambiguate when multiple workspaces appear in one document |
| `<user-home>` | The author's home directory (`~`) |
| `<toolbase>` | Organization-shared tool installation root |
| `<product-host>` | Vendor product directory inside `<toolbase>` (codenamed) |
| `<eclipse-install>` | Eclipse installation directory |
| `<jdk-install>` | JDK installation directory |
| `<m2-repo>` | `~/.m2/repository` |
| `<dir-1>`, `<dir-N>` | Disambiguated directory placeholders inside scripts |

### 2.2 Identity placeholders

| Placeholder | Meaning |
|---|---|
| `<author>` | The human author of a commit / session |
| `<user>` | OS username on a specific machine |
| `<author-email>` | Email of a commit author |
| `<reviewer>` | Reviewer of a PR / commit |
| `[REDACTED_NAME]` | Legacy form, kept for backwards compatibility — prefer `<author>` |
| `[REDACTED]` | Generic redaction, last resort when no specific placeholder fits |

### 2.3 Network & organization placeholders

| Placeholder | Meaning |
|---|---|
| `<corp-proxy-host>` | Corporate HTTP/HTTPS proxy hostname |
| `<corp-proxy-port>` | Corporate proxy port |
| `<corp-domain>` | Corporate primary domain (`*.example.com`) |
| `<corp-cloud-domain>` | Corporate cloud-hosted secondary domain |
| `<internal-vcs>` | Internal Git/VCS server base URL |
| `<internal-artifact-repo>` | Internal Maven/Nexus/Artifactory |
| `<internal-ci>` | Internal CI/CD endpoint |
| `<ticket-system>` | Jira / Azure DevOps / similar |
| `<TICKET-ID>` | Single ticket reference (`PROJ-1234`) |
| `<customer>` | External customer / client name |
| `<product-codename>` | Internal / unreleased product codename |

### 2.4 Generic disambiguation suffixes

When the same placeholder type appears multiple times in one document
with **different** values, suffix with letters: `<consumer-plugin-A>`,
`<consumer-plugin-B>`. When the count exceeds the alphabet, switch to
numeric: `<consumer-plugin-1>`, `<consumer-plugin-N>`.

### 2.5 The general rule of placeholder formation

`<lower-case-hyphenated-noun>` — angle-bracketed, lower-case,
hyphen-separated. This visually signals "placeholder, replace with
real value" and is consistent with HTML/XML/markdown convention. Do
not use snake_case (`<work_space_root>`) or PascalCase
(`<WorkspaceRoot>`).

---

## 3. Path Handling Protocol

### 3.1 Absolute → relative

Any `C:\…` or `/Users/…` path in a workspace artifact MUST be
converted to one of:

- A workspace-relative path: `.agents/skills/<skill>/SKILL.md`
- A user-home-relative path with `~`: `~/.m2/settings.xml`
- A placeholder if neither applies: `<workspace-root>/<plugin>/MANIFEST.MF`

**Why placeholders, not real anonymous paths**: a `C:\…\com.example.plugin\…`
still leaks the drive letter and operating system. A placeholder is OS-agnostic.

### 3.2 Cross-workspace references

When a document spans two workspaces (e.g., a session log that started
in one workspace and migrated to another), disambiguate explicitly:

```text
Source:      <workspace-root-source>
Target:      <workspace-root-target>
Skill repo:  <ai-agents-root>
```

Never write two real absolute paths side-by-side.

### 3.3 The fileLinkification carve-out

Links to other files in the **same repository** are NOT redacted — they
are relativized per the markdown-generation rules
([fileLinkification section](../../../ai-agent-rules/markdown-generation-rules.md)).

```markdown
✅ [SKILL.md](../SKILL.md)               # relative, portable
✅ [SKILL.md](.agents/skills/x/SKILL.md) # workspace-relative
❌ [SKILL.md](C:\work\ai-agents\…)        # absolute path — never
❌ [SKILL.md](file:///C:/…)              # file:// scheme — never
```

Also: **angle-bracket placeholders inside `[text](target)` link
targets MUST be replaced with inline-code form** because they produce
non-navigable broken links:

```markdown
❌ [<plugin>/<file>.target](../../../<plugin>/<file>.target)
✅ Workspace file (symbolic): `<plugin>/<file>.target`
```

### 3.4 Path-like strings inside code fences

Code fences are NOT exempt from redaction. A bash snippet showing
`cd C:\Users\<user>\…` is just as leaky as the same path in prose.

Acceptable forms:

```powershell
cd <workspace-root>
git -C <workspace-root> status
Get-ChildItem '<toolbase>\<product>\plugins'
```

If the literal example value is **load-bearing** for understanding
(e.g., demonstrating a proxy URL format), keep it but mark with a
parenthetical: `http://<corp-proxy-host>:<corp-proxy-port>`
*(literal example: `http://proxy.example.com:8080`)*.

---

## 4. Identity Handling Protocol

### 4.1 Commit-author trailers

In documentation that quotes a commit, redact the author line:

```diff
- Author: Full Personal Name <firstname.lastname@example.com>
+ Author: <author> <<author-email>>
```

Keep the commit SHA — SHAs are content-addressed and reveal nothing about identity.

### 4.2 Reported names in transcripts

When a session log says `the user, <Real Name>, asked …`, redact to
`the user asked …`. The author's identity is not load-bearing for the
technical content.

### 4.3 Username paths

Anywhere a developer's OS username appears in a path, redact to
`<user-home>` or `~`.

### 4.4 Reviewer / approver names

PR descriptions citing approvers MUST redact to `<reviewer-1>`,
`<reviewer-2>`, etc.

---

## 5. Network & Organization Handling Protocol

### 5.1 Proxy hosts

If the document explicitly teaches *how to configure* a proxy, keep
**both** the placeholder and one literal anonymized example:

```text
host: <corp-proxy-host>   # e.g., proxy.example.com
port: <corp-proxy-port>   # e.g., 8080
```

This satisfies pedagogy (reader knows what shape of value goes there)
without leaking the actual corporate proxy address.

### 5.2 Internal domain names

Replace organization-specific domains with placeholders:

```diff
- nonProxyHosts>127.0.0.1|localhost|*.<corp>.com|*.<corp-cloud>.com</nonProxyHosts>
+ nonProxyHosts>127.0.0.1|localhost|*.<corp-domain>|*.<corp-cloud-domain></nonProxyHosts>
```

### 5.3 Internal repository URLs

```diff
- https://<internal-vcs-real>/scm/<team>/<repo>.git
+ <internal-vcs>/<team>/<repo>.git
```

### 5.4 Ticket / issue references

```diff
- See <Ticket System> PROJ-12345 for the original report
+ See <ticket-system>/<TICKET-ID> for the original report
```

### 5.5 Customer / project codenames

Internal product codenames and customer names MUST be redacted:

```diff
- The <Internal-Product> customer-specific build for <Customer>
+ The <product-codename> customer-specific build for <customer>
```

### 5.6 IPv4 / IPv6 addresses

- `127.0.0.1`, `::1`, `0.0.0.0` → keep (universally meaningful)
- `192.168.x.x`, `10.x.x.x`, `172.16-31.x.x` (private ranges) → redact (`<host-ip>`)
- Public routable IPs from session output → redact unless it's a
  documented public service IP

---

## 6. File Naming Hygiene

Filenames themselves are artifacts. Apply redaction to the file path
just as to file contents.

### 6.1 Conversation log naming

```text
.agents/skills/<skill>/docs/conversations/YYYY-MM-DD-<topic>.md
```

✅ `2026-05-10-jdk17-to-jdk21-and-ide-fixes.md` — topic only
❌ `2026-05-10-<author>-<corp>-jdk-fix.md` — name + organization leak

### 6.2 Case-study naming

```text
.agents/skills/<skill>/docs/cases/<topic>.md
```

✅ `apache-commons-io-symbolic-name-aliasing.md` — public technology
✅ `m2e-enterprise-proxy-resolution.md` — generic infrastructure
❌ `<corp>-<proxy-product>-fix.md` — organization leak

### 6.3 Path placeholders in filenames

A filename should NOT contain `<placeholder>` syntax — angle brackets
break on many filesystems. Instead, encode the abstraction in words:

- `<corp-proxy>` topic → filename `enterprise-proxy-resolution`
- `<workspace-root-21>` topic → filename `jdk21-workspace-migration`

---

## 7. Code Examples — Special Cases

### 7.1 Diffs

Diffs included for pedagogy MUST be redacted just like prose. The
public technical content (GAV, bundle names, OSGi headers) is
universal (kept verbatim); the surrounding path is redacted:

```diff
- <location path="C:\<shared-tool>\<product>\<version>\eclipse\plugins" .../>
+ <location path="<toolbase>\<product-orbit>\eclipse\plugins" .../>
```

### 7.2 Shell snippets

Replace the user's working directory in prompts:

```diff
- PS C:\Users\<user>\work_2026\<workspace>> git status
+ PS <workspace-root>> git status
```

### 7.3 Log output / stack traces

Stack traces often leak local paths in `at com.example.Foo(Foo.java:42)`
*if* the stack frame format includes file URIs (rare). Frame text
itself is normally safe. The path-revealing lines are usually:

- `Working Directory: …`
- `Configuration file: …`
- `Local repository: …`

Redact these; keep the substantive trace.

### 7.4 PowerShell `$env:USERPROFILE` is safe

`$env:USERPROFILE` is a portable reference — it expands per-machine at
runtime. It is the *recommended* way to write user-home paths in
PowerShell examples:

```powershell
Get-ChildItem "$env:USERPROFILE\.m2\repository"  # ✅ portable
Get-ChildItem 'C:\Users\<user>\.m2\repository'   # ❌ leaky
```

Likewise `~` in POSIX shells.

---

## 8. Implementation Workflow

When applying this skill to existing artifacts:

### Step 1 — Inventory

```powershell
# Find every absolute Windows path
Select-String -Path '<artifact-glob>' -Pattern '[A-Z]:\\[\w\\]+' -AllMatches

# Find every absolute POSIX path
Select-String -Path '<artifact-glob>' -Pattern '/(?:Users|home|opt|mnt)/[\w\-./]+'

# Find every email address
Select-String -Path '<artifact-glob>' -Pattern '[\w\.\-]+@[\w\.\-]+\.\w+'

# Find every IPv4
Select-String -Path '<artifact-glob>' -Pattern '\b(?:\d{1,3}\.){3}\d{1,3}\b'

# Find every internal-looking hostname (heuristic)
Select-String -Path '<artifact-glob>' -Pattern '[\w\-]+\.(?:<corp1>|<corp2>|example)\.(?:com|net|local)'
```

### Step 2 — Classify

For each match, decide Tier A / B / C per §1.

### Step 3 — Substitute

Apply the canonical placeholder vocabulary per §2. Use bulk
`multi_replace_string_in_file` operations for high-volume substitution.

### Step 4 — Verify (mandatory)

After substitution, re-run the inventory scans. The terminal output
should be empty (or show only Tier-C universally-true matches).

```powershell
# A passing verification looks like this:
Select-String -Path '<artifact>' -Pattern '<real-name>|<real-corp-domain>' -SimpleMatch
# (no output)
```

### Step 5 — Encoding sanity-check

Redaction edits frequently mangle non-ASCII (em-dashes, ellipses,
emoji). After substitution, scan for mojibake markers:

```powershell
Select-String -Path '<artifact>' -Pattern 'Ã|â€|Â|ï¿½'
# (no output expected)
```

If matches appear, fix encoding before considering redaction complete.

### Step 6 — Re-render check

Open the rendered markdown in a previewer. Look for:

- Broken links (placeholders used in `[text](path)` link targets
  produce non-navigable links — see §3.3)
- Broken tables (extra `|` from incomplete substitution)
- Wide tables overflowing (placeholders are often longer than the
  values they replaced; consider line-wrapping cells)

---

## 9. Compositional Use by Other Skills

This skill is invoked passively by many composers:

- [`skill-factory`](../skill-factory/SKILL.md) — applies §1–§8 during
  the final audit of every generated `SKILL.md` and conversation log
- [`git-atomic-commit-construction`](../git-atomic-commit-construction/SKILL.md) —
  applies §4 to commit-message bodies that quote author trailers
- [`code-explanation`](../code-explanation/SKILL.md) — applies §7 to
  code excerpts copied into explanation documents
- [`work-log-processing`](../work-log-processing/SKILL.md) — applies
  §4 to log entries naming individuals

Composers MUST cite this skill explicitly when their output contains
content from §1's redaction targets.

---

## 10. Prohibited Behaviors

- **DO NOT** commit a personal email address to a tracked artifact
  even as a "for-attribution" courtesy. Attribution lives in the
  commit's Git author field, not in the artifact body.
- **DO NOT** invent fake-looking real values to satisfy redaction
  (e.g., replacing `<corp>.com` with `myveryreal.com`). Use canonical
  placeholders. The placeholder *is* the contract.
- **DO NOT** leave half-redacted strings (`<corp-proxy-host>.<corp>.com`)
  — they leak the suffix.
- **DO NOT** redact public open-source identifiers (Apache Commons,
  Eclipse, Maven Central). This is forbidden *over*-redaction —
  removing them harms reproducibility for future readers.
- **DO NOT** create new placeholder forms ad-hoc — extend §2's
  vocabulary first via a separate skill update.
- **DO NOT** rely on Git history to "hide" a redaction — once
  committed unredacted, the value is permanently in the object
  database. Reach for `git-filter-repo` or BFG if a hard scrub is
  required, but prevention is the only reliable strategy.

---

## 11. Quick-Reference Substitution Recipe

For one-shot bulk edits, the master substitution recipe (apply in
order; do not skip):

1. Absolute filesystem paths → `<workspace-root>` / `<user-home>` / `<toolbase>`
2. Per-machine drive letters → tier-2 placeholder
3. Email addresses → `<author-email>`
4. Personal names → `<author>`
5. OS usernames → `<user>`
6. Internal hostnames → `<corp-proxy-host>` / `<internal-vcs>` / etc.
7. Internal domains → `<corp-domain>` / `<corp-cloud-domain>`
8. Ticket IDs → `<ticket-system>/<TICKET-ID>`
9. Customer / codename strings → `<customer>` / `<product-codename>`

Per-organization concrete patterns (specific FQDNs, specific user
names) belong in **organization-specific extensions** (e.g.,
`bosch_ai_agents/.agents/skills/`) — never in this SSOT.

---

## 12. Related Skills & Rules

- [markdown-generation-rules.md](../../../ai-agent-rules/markdown-generation-rules.md) —
  authoritative link syntax; fileLinkification section
- [`skill-factory`](../skill-factory/SKILL.md) — primary consumer
- [`project-structure`](../project-structure/SKILL.md) — where
  redacted artifacts belong on disk
- [`vscode-extension-portability`](../vscode-extension-portability/SKILL.md) —
  analogous portability protocol for VS Code extension paths

---

## 13. Versioning

| Version | Date | Change |
|---|---|---|
| v1 | (initial) | Path relativization + basic name redaction (Tiers A/B not separated) |
| v2 | 2026-05-10 | Introduced three-tier model, canonical placeholder vocabulary, network/organization protocol, file-naming hygiene, encoding sanity-check, quick-reference recipe, prohibited behaviors, broken-link carve-out (§3.3) |
