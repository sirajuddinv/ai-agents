---
name: Git Submodule Commit Details
description: Extract complete commit metadata from a Git submodule — parent SHA(s), commit message, file changes with add/modify/delete classification, author, and committer — for use in parent commit messages or audit reports.
category: Git & Repository Management
---

# Git Submodule Commit Details Skill

> **Skill ID:** `git_submodule_commit_details`
> **Version:** 1.0.0
> **Standard:** [Agent Skills (agentskills.io)](https://agentskills.io)

## Description

A self-contained extraction primitive that retrieves full commit metadata
from a Git submodule at a given SHA. It produces a structured record
containing every field required by industrial submodule commit message
formats:

- Submodule path and target commit SHA
- Parent commit(s) — with merge detection
- Full commit message body
- File changes — additions, deletions, and per-file classification
  (added / modified / deleted)
- Author name, email, and timestamp
- Committer name, email, and timestamp
- Registration URL (from `.gitmodules`)

This skill is a **reusable primitive**. It is called by:

- [`git_submodule_commit_reword`](../git_submodule_commit_reword/SKILL.md)
  — to compose amended commit messages
- [`git_atomic_commit`](../git_atomic_commit/SKILL.md)
  — to compose descriptive submodule sync commit messages

## Prerequisites

| Requirement | Minimum |
| :--- | :--- |
| VCS | Git 2.x+ |
| Shell | Bash 4+ |
| Tools | `GIT_PAGER=cat` to suppress pager output |
| Access | Read access to the submodule repository |

## When to Apply

Apply this skill when:

- Composing a parent-repo commit message that syncs a submodule pointer
- Rewording a submodule addition commit to include full metadata
- Auditing what a submodule commit contains before accepting a pointer advance
- Any consumer skill needs structured submodule commit data

Do NOT apply when:

- The submodule path is not initialized — run `git submodule update --init` first
- The target SHA does not exist locally — fetch the submodule first

---

## Step-by-Step Procedure

### Step 1 — Resolve Submodule Path and Target SHA

#### 1a — Discover the Current Pointer (if not already known)

Use `git ls-tree` to obtain the submodule path and the SHA it currently
points to in the parent repository's tree:

```bash
GIT_PAGER=cat git -C <parent-repo-path> ls-tree HEAD <submodule-name>
```

**Output format:**

```
160000 commit <submodule-sha>    <submodule-name>
```

**Pedagogical Breakdown:**

- `ls-tree HEAD`: reads the tree object at HEAD — the current committed
  state of the working tree, not the index
- `160000`: the gitlink mode, signalling this entry is a submodule
  pointer, not a regular file or directory
- `commit`: confirms the object type is a commit reference

#### 1b — Accept an Explicit SHA Override

If the caller provides an explicit target SHA (e.g., to inspect a
not-yet-committed pointer advance), use that SHA directly and skip
Step 1a.

---

### Step 2 — Extract Core Commit Metadata

Run the following single command against the submodule repository. It
retrieves all metadata fields in a deterministic order:

```bash
GIT_PAGER=cat git -C <submodule-path> log \
  --format=format:"%P%n%an <%ae>%n%ad%n%cn <%ce>%n%cd%n%B" \
  <submodule-sha> -1
```

**Pedagogical Breakdown — Format Placeholders:**

| Placeholder | Field | Notes |
| :--- | :--- | :--- |
| `%P` | Parent SHA(s) | Space-separated; two SHAs = merge commit |
| `%an <%ae>` | Author name + email | Human who wrote the change |
| `%ad` | Author date | When the change was authored |
| `%cn <%ce>` | Committer name + email | Who applied the commit (may be GitHub, CI) |
| `%cd` | Committer date | When the commit was recorded in history |
| `%B` | Full commit message body | Title + blank line + body paragraphs |

**Pedagogical Breakdown — Flags:**

- `git -C <submodule-path>`: executes inside the submodule repo without
  a shell `cd`. Mandatory in stateless environments where `cd` does not
  persist across invocations.
- `--format=format:"..."`: uses the "tformat" (terminator format) —
  every record is terminated, not separated, avoiding a trailing newline
  difference with `-format`.
- `-1`: limits output to exactly one commit — the target SHA. Without
  this flag the command would walk the full ancestry.

**Merge Commit Detection:**

If `%P` returns two SHAs (space-separated), the commit is a merge.
Record both parents as:

```
Submodule commit parent: <sha1> (merge: <sha1> <sha2>)
```

---

### Step 3 — Extract File Changes with Line Counts

```bash
GIT_PAGER=cat git -C <submodule-path> diff-tree \
  --no-commit-id -r --numstat <submodule-sha>
```

**Pedagogical Breakdown:**

- `diff-tree`: compares the tree of the given commit against its
  parent(s). For a merge commit it diffs against the first parent.
- `--no-commit-id`: suppresses the leading commit SHA line, keeping
  output to one line per changed file.
- `-r`: recurse into subdirectories so nested file paths appear fully
  qualified.
- `--numstat`: emits tab-separated `<additions>\t<deletions>\t<filepath>`
  — machine-readable line counts without ANSI colour codes.

**For merge commits** — use the two-parent diff instead:

```bash
GIT_PAGER=cat git -C <submodule-path> diff <parent1> <parent2> --stat
```

**Output example:**

```
17    0    .classpath
1     1    .gitignore
11    0    .project
2     0    .settings/org.eclipse.jdt.apt.core.prefs
11    0    .settings/org.eclipse.jdt.core.prefs
```

---

### Step 4 — Classify Each File as Added / Modified / Deleted

For every file returned by Step 3, determine its change type by checking
whether it existed in the **parent commit's tree**:

```bash
GIT_PAGER=cat git -C <submodule-path> ls-tree -r <parent-sha> \
  | grep <filename>
```

**Pedagogical Breakdown:**

- `ls-tree -r <parent-sha>`: lists every tracked file in the parent
  commit's tree recursively.
- Pipe through `grep <filename>`: isolates the target file entry.

**Classification Rules:**

| Condition | Classification |
| :--- | :--- |
| File found in parent tree | `modified` |
| File NOT found in parent tree | `added` |
| File in parent tree but NOT in current commit | `deleted` |

**For merge commits** — compare against `<parent1>` (the base branch).

---

### Step 5 — Resolve Registration URL

Read `.gitmodules` in the **parent repository** to obtain the remote URL
for the submodule:

```bash
GIT_PAGER=cat git -C <parent-repo-path> config \
  --file .gitmodules submodule.<submodule-name>.url
```

**Pedagogical Breakdown:**

- `--file .gitmodules`: targets the submodule configuration file
  explicitly rather than the global or local git config.
- `submodule.<submodule-name>.url`: the key path for the remote URL of
  the named submodule.

---

### Step 6 — Assemble the Structured Record

Combine all extracted fields into the canonical output format used by
consumer skills:

```
Submodule: <submodule-name> -> <submodule-sha>
Submodule commit parent: <parent-sha>
  (merge: <parent1> <parent2>  ← only if merge commit)
Submodule commit msg: <title-line>

<body-paragraphs-if-multiline>

Submodule commit changes:
  <filepath> | <additions> insertions(<classification>)
  <filepath> | <additions> insertions, <deletions> deletions(<classification>)
  ...
Submodule commit author: <author-name> <author-email>
Submodule commit author time: <author-date>
Submodule commit committer: <committer-name> <committer-email>
Submodule commit committer time: <committer-date>

Register <submodule-name> submodule pointing to <registration-url>
```

**Formatting Rules:**

- Use `(added)`, `(modified)`, or `(deleted)` as the classification
  suffix — never abbreviate.
- For merge commits, list `(merge: <sha1> <sha2>)` inline after the
  parent SHA.
- If the commit message body is multi-line, preserve all paragraphs
  verbatim between `Submodule commit msg:` and
  `Submodule commit changes:`.
- Do NOT summarize the commit body — **Zero Omission** is mandatory.

---

## Output Contract

This skill MUST produce one structured record per submodule SHA
requested. The record is consumed verbatim by the caller — no further
transformation is applied by this skill.

---

## Prohibited Behaviors

The agent **IS BLOCKED** from:

- Summarizing or paraphrasing the submodule commit message body
- Omitting parent SHA information for any commit type
- Skipping the file classification step (add / modify / delete)
- Confusing author timestamp with committer timestamp
- Using `cd` instead of `git -C` for directory targeting
- Running `git log` without `-1` and accidentally reading multiple commits

---

## Common Pitfalls

| Pitfall | Solution |
| :--- | :--- |
| Merge commit shows wrong file list | Use `diff <parent1> <parent2> --stat` instead of `diff-tree --numstat` |
| `%P` returns empty | The commit is a root commit with no parent — document as `(root commit)` |
| Submodule not initialized | Run `git submodule update --init <submodule-name>` in parent repo |
| `git -C` path wrong | Verify path with `git -C <path> rev-parse --show-toplevel` |
| Timestamps differ between author and committer | Both MUST be recorded separately — GitHub merges set committer to GitHub |

---

## Related Skills

- [`git_submodule_commit_reword`](../git_submodule_commit_reword/SKILL.md)
  — Uses this skill's output to amend existing commits
- [`git_atomic_commit`](../git_atomic_commit/SKILL.md)
  — Uses this skill's output to compose submodule sync commit messages
- [`git_submodule_pointer_repair`](../git_submodule_pointer_repair/SKILL.md)
  — Uses submodule commit metadata to validate synchronization horizons

---

## Traceability

- **Industrialized from:** Session `be162a56-7f60-4923-bc7c-f2ef1ae96510`
  — atomic commit construction for `oleovista-acers` where submodule
  metadata extraction was needed outside the reword context (Steps 3b–3e
  of `git_submodule_commit_reword` applied verbatim to compose sync
  commit messages for `git_atomic_commit`).
- **Rule source:** [`ai-rule-standardization-rules.md`](../../../ai-agent-rules/ai-rule-standardization-rules.md)
- **Factory protocol:** [`skill_factory/SKILL.md`](../skill_factory/SKILL.md)
