---
name: git-lfs-selective-clone
description: Industrial protocol for cloning a Git LFS repository (and its
    submodules) without downloading any LFS blobs, then selectively pulling
    only the LFS objects the user actually needs via include/exclude globs.
category: Git & Repository Management
---

# Git LFS Selective Clone Skill

> **Skill ID:** `git-lfs-selective-clone`
> **Version:** 1.0.0
> **Standard:** [Agent Skills (agentskills.io)](https://agentskills.io)

## Description

Clone a Git LFS repository while skipping **all** LFS blob downloads, then
materialize only the LFS objects the user asks for. The skill covers:

1. **Bullet-proof skip** of LFS at clone time — defeating the silent
   `filter.lfs.process` long-running filter that bypasses
   `GIT_LFS_SKIP_SMUDGE` and `filter.lfs.smudge` alone.
2. **Verification** that LFS was *actually* skipped (pointer files are
   ~130 B; real blobs are MB–GB).
3. **Recursive submodule initialization** under the same skip regime —
   submodules that ship LFS objects must inherit the skip, otherwise the
   first `submodule update --init` silently pulls gigabytes.
4. **Selective post-clone pull** via `git lfs pull --include / --exclude`
   with brace-list globs, applied per-repo and per-submodule.

The clone history, tree contents, and pointer files are preserved
bit-for-bit; only the LFS object cache (`.git/lfs/objects/`) is left
empty until the user opts in to specific files.

## Source Conversations

| Date | Topic |
|---|---|
| 2026-05-12 | Selective LFS clone of a large LFS repo on Windows / PowerShell — diagnosed `GIT_LFS_SKIP_SMUDGE` failure on PowerShell `set`, identified the `filter.lfs.process` bypass, and built the three-filter override + per-path `git lfs pull` flow |

***

## 1. Environment & Dependencies

The agent MUST verify the following before executing this skill:

| Requirement | Minimum | Verification |
|---|---|---|
| Git | 2.20+ (long-running filter protocol stable) | `git --version` |
| Git LFS | 2.5+ (supports `filter.lfs.process`) | `git lfs version` |
| Shell | Windows PowerShell 5.1+ / PowerShell Core 7+ / Bash 4+ / Zsh | `$PSVersionTable.PSVersion` or `bash --version` |
| Network | Reachability to the host (e.g., `github.com`, internal `<internal-vcs>`) | `git ls-remote <url>` |

If `git lfs` is missing, install per the standard package manager:

```bash
# macOS
brew install git-lfs

# Debian / Ubuntu
sudo apt-get install -y git-lfs

# RHEL / Fedora
sudo yum install -y git-lfs

# Windows (winget / choco)
winget install Git.GitLFS
```

After install, run `git lfs install` **once per user** to register the
default filter hooks (does **not** force LFS on every repo — it is a
prerequisite for the filter overrides below to take effect).

***

## 2. When to Apply

Apply this skill when:

- The user asks to clone an LFS repository **without** the LFS blobs.
- The user complains the clone "hangs" or downloads many GB unexpectedly
  on a repo that has `.gitattributes` declaring `filter=lfs`.
- The user wants a subset of LFS files materialized (e.g., one `.zip`
  but not the 5 GB of `.mp4` companions).
- The repo contains submodules that themselves ship LFS objects and the
  user wants those submodules initialized **without** their LFS payload.

Do **NOT** apply when:

- The user wants the **full** LFS payload — use a plain
  `git clone --recurse-submodules <url>` instead.
- The user wants a shallow clone (`--depth=1`) primarily — that is a
  different size-control axis; the two can be combined but the shallow
  protocol is out of scope here.
- The repository has no `.gitattributes` `filter=lfs` entries — there
  are no LFS pointers to skip; a normal clone is sufficient.

***

## 3. Step-by-Step Procedure

### Step 0 — Pre-Flight Inspection

Confirm the target repo actually uses LFS before applying the overrides
(over-engineering a non-LFS clone is a "Greater-Than-Before" violation —
do not add ceremony where none is needed).

#### 0a — Probe `.gitattributes` Remotely (no clone yet)

```bash
git ls-remote --heads <repo-url>           # confirms reachability + auth
git archive --remote=<repo-url> HEAD .gitattributes 2>/dev/null | tar -xO
```

The agent MAY skip Step 0a if the user has already confirmed the repo
uses LFS. If `.gitattributes` shows `filter=lfs diff=lfs merge=lfs`
entries (typical pattern: `*.zip filter=lfs ...`), proceed.

#### 0b — Pick a Local Destination

Default per the
[Git Repository Management Rules §2](../../../ai-agent-rules/git-repo-management-rules.md#2-high-fidelity-cloning-protocol):
`~/sample/path/<repo-name>/` (or `~/Lab_Data/<repo-name>/` per
[Repo Discovery Rules](../../../ai-agent-rules/repo-discovery-rules.md)).
The agent MUST confirm the destination is empty.

***

### Step 1 — Clone Without LFS Blobs (Three-Filter Override)

This is the **only** clone form the agent MUST use for an LFS-skip
workflow. Single-flag attempts (env var alone, or
`filter.lfs.smudge=` alone) silently fail because modern Git LFS
installs a **long-running `process` filter** that bypasses the smudge
hook.

#### 1a — Canonical Command

POSIX (Bash / Zsh / Git Bash):

```bash
GIT_LFS_SKIP_SMUDGE=1 git clone \
    -c filter.lfs.smudge= \
    -c filter.lfs.process= \
    -c filter.lfs.required=false \
    --recurse-submodules=no \
    --progress \
    <repo-url> <dest>
```

PowerShell (5.1+ / Core 7+):

```powershell
$env:GIT_LFS_SKIP_SMUDGE = "1"
git clone `
    -c filter.lfs.smudge= `
    -c filter.lfs.process= `
    -c filter.lfs.required=false `
    --recurse-submodules=no `
    --progress `
    <repo-url> <dest>
```

Windows CMD:

```cmd
set GIT_LFS_SKIP_SMUDGE=1
git clone -c filter.lfs.smudge= -c filter.lfs.process= -c filter.lfs.required=false --recurse-submodules=no --progress <repo-url> <dest>
```

> [!IMPORTANT]
> Submodules are handled **separately** in Step 3 under the same skip
> regime. Passing `--recurse-submodules` here would clone submodules
> with the **default** filter set and silently download their LFS
> blobs. The agent MUST use `--recurse-submodules=no` (or omit it; it
> is the default) and run Step 3 explicitly afterwards.

#### 1b — Deep Command Explanation (Pedagogical)

Per the Deep Command Explanation Mandate, every flag is justified
below:

- **`GIT_LFS_SKIP_SMUDGE=1`** — Tells the `git-lfs smudge` driver to
  emit the **pointer text** instead of fetching the blob when Git
  asks it to materialize a file during checkout. Necessary but
  **not sufficient** on its own — modern installs use the
  long-running `process` filter (added in Git LFS 2.2) which is a
  separate code path and ignores this env var on some builds /
  versions.
- **`-c filter.lfs.smudge=`** — Sets the smudge command to the
  empty string for *this clone only* (the `-c` is a one-shot
  override; it is **not** written into `.git/config`). When the
  smudge command is empty, Git skips the smudge step entirely and
  writes the pointer to the working tree as-is. This belt-and-
  suspenders the `GIT_LFS_SKIP_SMUDGE` env var.
- **`-c filter.lfs.process=`** — The critical override. Setting
  the `process` filter to empty disables the long-running filter
  protocol entirely for this clone. Without this, Git LFS streams
  every LFS blob during checkout regardless of the smudge override.
  **This is the single flag most "skip LFS" instructions on the
  internet omit, and it is the most common reason a "skipped" clone
  still downloads gigabytes.**
- **`-c filter.lfs.required=false`** — Tells Git not to fail the
  checkout if the LFS filters are absent / empty / non-functional.
  Without this, the empty filters above can cause `error: external
  filter '...' failed` at checkout time and abort the clone with a
  half-populated working tree.
- **`--recurse-submodules=no`** — Explicit opt-out of submodule
  recursion at clone time so the LFS-skip regime is not bypassed by
  the submodule clones. Step 3 reapplies the same overrides for
  submodules.
- **`--progress`** — Forces progress output to stderr even when the
  output is not a terminal (e.g., when redirected to a log file or
  piped through `Start-Process`). Critical for diagnosing hangs.

#### 1c — PowerShell Pitfall: `set` Is Not `$env:`

A frequent failure mode on Windows:

```powershell
# WRONG — `set` is an alias for `Set-Variable` in PowerShell.
# Creates a PowerShell variable that child `git.exe` cannot read.
set GIT_LFS_SKIP_SMUDGE=1

# CORRECT — exports a process-environment variable.
$env:GIT_LFS_SKIP_SMUDGE = "1"
```

The agent MUST detect the active shell (`$PSVersionTable.PSVersion`
present → PowerShell; otherwise CMD/POSIX) and emit the correct
syntax.

***

### Step 2 — Verify LFS Was Actually Skipped

The agent MUST run all three verifications before declaring success.
A "clone completed without errors" message is **not** evidence that
LFS was skipped — corrupted skips silently download everything.

```bash
cd <dest>

# (a) Total working-tree size (should be tiny relative to known LFS payload)
du -sh .   # POSIX
```

```powershell
# (a-pwsh) PowerShell equivalent
(Get-ChildItem -Recurse -Force | Measure-Object Length -Sum).Sum / 1MB
```

```bash
# (b) LFS object inventory — the marker column MUST be `-` (dash), NOT `*`
#     `-` = pointer only (blob NOT in local cache)
#     `*` = blob downloaded into .git/lfs/objects/
git lfs ls-files
```

```bash
# (c) Spot-check one known LFS file — MUST be ~130 B and start with
#     "version https://git-lfs.github.com/spec/v1"
head -3 <one-lfs-tracked-file>
```

```powershell
# (c-pwsh) PowerShell equivalent
Get-Content <one-lfs-tracked-file> -TotalCount 3
```

If any check fails (size matches the real blob, `*` markers in
`ls-files`, or binary content instead of `version https://...`), the
agent MUST:

1. Kill any running `git` / `git-lfs` processes.
2. Delete the destination directory.
3. Retry Step 1 — most commonly the `filter.lfs.process=` override
   was forgotten.

***

### Step 3 — Initialize Submodules Without LFS (Recursive)

Per the Recursive Submodule Mandate (defined in
[AI Rule Standardization Rules §4](../../../ai-agent-rules/ai-rule-standardization-rules.md#4-content-philosophy-ultra-lean-industrial))
all submodule operations MUST use the recursive form so nested LFS
submodules also inherit the skip.

```bash
cd <dest>
GIT_LFS_SKIP_SMUDGE=1 git \
    -c filter.lfs.smudge= \
    -c filter.lfs.process= \
    -c filter.lfs.required=false \
    submodule update --init --recursive --progress
```

```powershell
$env:GIT_LFS_SKIP_SMUDGE = "1"
git -c filter.lfs.smudge= -c filter.lfs.process= -c filter.lfs.required=false `
    submodule update --init --recursive --progress
```

**Pedagogical breakdown:**

- The same three `-c` overrides MUST be re-supplied here. Git
  configuration is **per-repo**, not inherited across the
  submodule boundary. A submodule clones into `.git/modules/<name>/`
  using its **own** default filter set, so without these overrides
  it would silently pull every LFS blob it ships.
- `--init` creates the working tree for each registered submodule.
- `--recursive` descends into nested submodules so any deeper LFS
  pointers also stay as pointers.
- `--progress` again surfaces progress to stderr — important for
  diagnosing hangs in the submodule phase.

After this step, re-run Step 2's verifications **inside each
submodule directory** (`git lfs ls-files` should show `-` markers).

***

### Step 4 — Selective LFS Pull (Include / Exclude Globs)

Once the skeleton is in place, the agent materializes only the LFS
objects the user actually requested.

#### 4a — Locate the LFS Tracking Inventory

```bash
git lfs ls-files
```

This is the canonical surface of LFS-tracked paths. The agent MUST
use these literal paths (or globs over them) — guessing at extensions
is forbidden because a repo can track arbitrary patterns via
`.gitattributes`.

> [!NOTE]
> `git lfs ls-files -- <subdir>` is **NOT** a supported pathspec
> filter — it interprets the argument as a revision and fails with
> `fatal: bad revision`. To restrict by directory, post-filter with
> `grep` / `Select-String` instead.

#### 4b — Pull Selected Files

The `--include` and `--exclude` flags accept comma-separated brace-
glob lists, evaluated against the paths emitted by `git lfs ls-files`.

```bash
# Pull every zip under ats/ and sample_ats/ in the top-level repo
git lfs pull --include="ats/*.zip,sample_ats/*.zip"

# Inside a submodule: pull every .7z except one specific file
cd <submodule-path>
git lfs pull --include="*.7z" --exclude="NanoPVER_6Cores2_230617_READWRITE.7z"
```

**Pedagogical breakdown:**

- `git lfs pull` — fetches LFS objects referenced by the current
  checkout and replaces pointer text with real blob content. It is
  the **post-clone** equivalent of the smudge step that Steps 1–3
  deliberately bypassed.
- `--include="<glob1>,<glob2>"` — comma-separated, **no spaces**.
  Spaces around commas break the parser silently and you will pull
  everything. Globs are matched against repo-relative paths from
  `git lfs ls-files`.
- `--exclude="<glob>"` — applied AFTER `--include`. The
  evaluation order is: (include == empty OR matches include) AND
  NOT matches exclude. To pull *everything except one file*, use
  `--include="*"` with `--exclude="<file>"`.
- `git lfs pull` operates on the **current submodule scope only** —
  it does NOT recurse. Run it once per repository / submodule that
  contains files of interest.

#### 4c — Brace-Glob Compatibility

Some `git lfs` versions on Windows do not expand `{a,b}` brace
syntax. Prefer the comma-separated `--include` list (which is the
LFS-native multi-pattern syntax) over brace expansion to stay
portable.

***

### Step 5 — Final Audit

```bash
git lfs ls-files                # `*` for downloaded, `-` for pointer
du -sh .                        # POSIX
```

```powershell
(Get-ChildItem -Recurse -Force | Measure-Object Length -Sum).Sum / 1MB
```

Present a before / after table to the user:

| Item | Before pull | After pull |
|---|---|---|
| Total working-tree size | `<X> MB` | `<Y> MB` |
| LFS files downloaded | 0 | `<N>` of `<M>` |
| LFS files still pointer-only | `<M>` | `<M-N>` |

The agent MUST flag any LFS file the user did **not** request that
nevertheless flipped from `-` to `*` — that indicates the
`--include` / `--exclude` glob matched too broadly and the cache
ate disk the user did not authorize.

***

## 4. Scope Coverage

| Concern | Convention |
|---|---|
| Clone-time blob skip | `GIT_LFS_SKIP_SMUDGE=1` **AND** `-c filter.lfs.smudge=` **AND** `-c filter.lfs.process=` **AND** `-c filter.lfs.required=false` |
| Submodule init | Same four overrides on `git submodule update --init --recursive` |
| Selective pull | `git lfs pull --include="<csv-globs>" --exclude="<csv-globs>"` |
| Verification | `git lfs ls-files` marker column + per-file pointer header check |
| Shell portability | Detect PowerShell vs CMD vs POSIX and emit matching env-var syntax |
| Submodule recursion | `--recursive` mandatory (Recursive Submodule Mandate) |

***

## 5. Prohibited Behaviors

The agent is **BLOCKED** from:

- **Relying on `GIT_LFS_SKIP_SMUDGE` alone.** The `filter.lfs.process`
  override is mandatory; without it, LFS streams every blob through
  the long-running filter regardless of the env var.
- **Using PowerShell `set FOO=1` to export an env var.** That is an
  alias for `Set-Variable` and the child `git.exe` will not see it.
  Use `$env:FOO = "1"`.
- **Cloning with `--recurse-submodules`** in this workflow without
  re-supplying the four overrides on the recursive command path.
  Submodule defaults will silently fetch all LFS objects.
- **Declaring success based on "clone completed" alone.** Step 2
  verification (`ls-files` markers + pointer-file header check) is
  mandatory.
- **Spaces around commas in `--include` / `--exclude` lists.**
  `"a.zip, b.zip"` matches only `a.zip` and the literal pattern
  ` b.zip` (with leading space) — silently wrong.
- **Pulling LFS with `--include="*"` without a matching
  `--exclude`** when the user asked for "everything except X". The
  agent MUST surface the explicit exclude.
- **Using `git lfs ls-files -- <subdir>`** as a pathspec filter — it
  is interpreted as a revision and fails. Use `grep` / `Select-String`
  on the full listing instead.

***

## 6. Common Pitfalls

| Pitfall | Solution |
|---|---|
| `set GIT_LFS_SKIP_SMUDGE=1` in PowerShell silently no-ops | Use `$env:GIT_LFS_SKIP_SMUDGE = "1"` |
| `-c filter.lfs.smudge=` alone still downloads blobs | Add `-c filter.lfs.process=` — the long-running filter is a separate code path |
| `error: external filter 'git-lfs filter-process' failed` at checkout | Add `-c filter.lfs.required=false` so empty filters are non-fatal |
| Submodule init pulls gigabytes despite parent skipping LFS | Re-supply the four overrides on `git submodule update --init --recursive` — submodules don't inherit parent's per-command `-c` config |
| Brace glob `{a,b}.zip` doesn't expand on Windows `git lfs` | Use comma-separated `--include="a.zip,b.zip"` (LFS-native syntax) |
| `git lfs ls-files -- ats` → `fatal: bad revision 'ats'` | `ls-files` doesn't accept pathspecs; post-filter with `grep ^.*\bats/` |
| Pointer files look like binary in `cat` output | They start with `version https://git-lfs.github.com/spec/v1` and are ~130 B; check with `head -3` not `file` |
| `git clone` "hangs" with no progress | `--progress` not passed; or LFS download is in progress (size grows). Inspect the destination tree size to disambiguate |
| Clone succeeded but later `git pull` re-pulls everything | The four `-c` overrides are clone-only (not written to `.git/config`). For persistent skip, either re-supply them on every fetch, or `git config --local filter.lfs.smudge ""` etc. after clone |

***

## 7. Persistent vs One-Shot Skip

The Step 1 command uses one-shot `-c` overrides that **do not** persist
into `.git/config`. Subsequent `git pull` / `git fetch` operations
will use the user's default filters and **may** re-fetch LFS objects
during merge / checkout.

If the user wants persistent skip on the cloned repo:

```bash
cd <dest>
git config --local filter.lfs.smudge ''
git config --local filter.lfs.process ''
git config --local filter.lfs.required false
```

Repeat inside every submodule. To restore default LFS behavior later:

```bash
git config --local --unset filter.lfs.smudge
git config --local --unset filter.lfs.process
git config --local --unset filter.lfs.required
git lfs install --local
```

The agent MUST ask the user which mode (one-shot vs persistent) they
want before writing into `.git/config`.

***

## 8. Related Skills

- [`git-repo-storage-minimization`](../git-repo-storage-minimization/SKILL.md) —
  complementary skill for shrinking `.git/` after LFS pointers are in
  place (deinit unused submodules, `gc --aggressive`).
- [`git-submodule-uninitialized-handler`](../git-submodule-uninitialized-handler/SKILL.md) —
  remediation for submodule pointers stuck in uninitialized state, can
  consume the output of this skill's Step 3 verification.
- [`git-github-auth-fallback`](../git-github-auth-fallback/SKILL.md) —
  if the clone in Step 1 fails with 401/403 before LFS even runs.

## 9. Related Rules

- [Git Repository Management Rules §2 — High-Fidelity Cloning Protocol](../../../ai-agent-rules/git-repo-management-rules.md#2-high-fidelity-cloning-protocol)
- [Repo Discovery Rules — Cloning Workflow](../../../ai-agent-rules/repo-discovery-rules.md)
- [AI Rule Standardization Rules §4 — Recursive Submodule Mandate](../../../ai-agent-rules/ai-rule-standardization-rules.md#4-content-philosophy-ultra-lean-industrial)

***

## 10. Traceability

Source conversation logs MUST be sanitised via the
[Redaction & Portability Skill](../redaction-portability/SKILL.md)
before being committed under `ai-agent-rules/docs/conversations/`.
Specifically: internal LFS host names (e.g., `<internal-vcs>`), customer
product codenames embedded in LFS file names, and absolute Windows /
POSIX paths in shell transcripts MUST be replaced with the canonical
placeholder vocabulary before commit.
