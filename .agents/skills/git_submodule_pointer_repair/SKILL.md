---
name: Git Submodule Pointer Repair
description: Industrial protocol for surgically fixing invalid submodule pointers in parent repository history using the Synchronization Horizon algorithm.
category: Git & Repository Management
---

# Git Submodule Pointer Repair Skill (v1)

This skill provide surgical, high-fidelity repair of invalid submodule pointers within a parent repository's history. It implements the **Synchronization Horizon** algorithm to autonomously identify the correct architectural alignment point between parent mandates and modular history.

***

## 1. Environment & Dependencies

The agent MUST verify the following tools are available before execution:

- **Git**: Mandatory for repository operations.
- **Python 3**: Mandatory for the `repair.py` synchronization engine.

```bash
# Verify environment
which git && git --version
which python3 && python3 --version
```

***

## 2. Operational Logic: The Synchronization Horizon

This algorithm identifies the exact architectural alignment point ($s_p$) where parent repository mandates are satisfied by submodule history.

### 2.1 Detection & Backtracking (The Discovery)
1. **Identify Target**: Locate submodules with invalid pointers in the input Parent SHA.
2. **Verify Validity**: For every invalid pointer, backtrack in the parent history to find the **Last Known Valid SHA**.
3. **Isolate Intro Commit**: The commit that changed the last known valid SHA to the first invalid SHA is the **Invalid Reference Introduction Commit**.

### 2.2 Cumulative Synchronization Scan (Mapping)
1. **Extract Mandates**: Retrieve the commit message of the **Invalid Reference Introduction Commit**.
2. **Successor Analysis**: Identify the successor commits ($s_1, s_2, \dots, s_n$) of the Last Known Valid SHA in the submodule repository.
3. **Iterative Alignment**: Analyze the cumulative changes $\{s_1 \dots s_i\}$. 
4. **Identify Boundary $s_p$**: The loop stops at $s_p$ where the cumulative changes correctly and completely satisfy the parent's mandates ($s_{p+1}$ MUST be unrelated drift).

### 2.3 Surgical Repair (Execution)
1. **Safety Backup**: MUST create a backup tag before modification (e.g., `backup-pointer-repair-<timestamp>`).
2. **Pointer Swap**: Surgically edit the **Invalid Reference Introduction Commit**, replacing the invalid hash with $s_p$.
3. **Propagation**: Propagate the fix across subsequent history using a non-interactive rebase or equivalent transformation.

***

## 3. Cleanup Protocol

The safety backup tag MUST be managed with 100% human-in-the-loop fidelity.

1. **Verification**: Confirm `ls-tree` at the sync point reflects $s_p$.
2. **Authorization**: Explicitly ask the user: *"History repair verified. May I delete the safety backup tag <tag_name>?"*
3. **Execution**: Delete the tag ONLY upon explicit "yes" confirmation.

***

## 4. Automation Engine

The surgical logic is encapsulated in the industrial Python engine:
[scripts/repair.py](./scripts/repair.py)

```bash
# Example Usage:
python3 .agents/skills/git_submodule_pointer_repair/scripts/repair.py --parent <SHA> --submodule <PATH>
```

***

## 5. Mass Pointer Reconciliation (Full History Rewrite Recovery)

Use this protocol when the **entire submodule history has been rewritten** (e.g., linearized, rebased, pruned), making **every historical pointer** in the parent repository invalid.

### 5.1 Scope Assessment

```bash
# List ALL parent commits touching the submodule pointer, oldest → newest
git log --reverse --format="%H | %as | %s" -- <submodule-path>
```

Save this list. Each entry has an invalid pointer that needs a verified replacement.

### 5.2 Build the Verified Mapping

For each invalid pointer SHA, find its counterpart in the refined submodule history using **high-fidelity metadata extraction** (per the `git_commit_metadata_extraction` skill):

**Match criteria (ALL must agree):**
- `%an <%ae>` — Author name and email
- `%ad` — Author date (exact timestamp)
- `%cn <%ce>` — Committer name and email
- `%cd` — Committer date (exact timestamp)
- `%s` — Commit subject line
- `diff-tree --numstat` file list (sorted, space-separated)

**Indexing the new history for fast lookups:**

```bash
git -C <submodule-path> log --format="%H|%an <%ae>|%ad|%cn <%ce>|%cd|%s" <new-branch> > new_index.txt
```

**For each old pointer:**

```bash
old_title=$(git -C <submodule-path> log -1 --format=%s <old-sha>)
old_date=$(git -C <submodule-path> log -1 --format=%ad <old-sha>)
# Match by date + title
new_sha=$(grep -F "|$old_date|$old_title" new_index.txt | cut -d'|' -f1 | head -n 1)
```

**If old SHA not in local store — fetch from remote:**

```bash
git -C <submodule-path> fetch origin <old-sha>
```

**Output:** A clean `old_sha new_sha` mapping file, one pair per line.

### 5.3 Verify the Mapping (Extensive Check)

Generate a Markdown verification report comparing all metadata fields side-by-side:

```bash
while read -r line; do
    suite_sha=$(echo "$line" | cut -d'|' -f1 | xargs)
    sub_sha=$(echo "$line" | cut -d'|' -f2 | xargs)
    old_info=$(git -C <submodule-path> log -1 --format="%an <%ae>|%ad|%s" "$sub_sha")
    o_files=$(git -C <submodule-path> diff-tree --no-commit-id -r --numstat "$sub_sha" | awk '{print $3}' | sort | tr '\n' ' ' | xargs)
    match_line=$(grep -F "|$o_adate|$o_title" new_index.txt | head -n 1)
    # Compare: author, date, files — emit ✅ or ❌ per field
done < mapping.txt | tee verification_report.md
```

All mappings MUST show ✅ for Author, Author Date, Committer, Committer Date, Commit Message, and Files before proceeding.

### 5.4 Backup Before Rewrite

```bash
# Create a timestamped local + remote backup branch
git branch backup/pre-submodule-repair-$(date +%Y%m%d%H%M)
git push origin backup/pre-submodule-repair-<timestamp>
```

### 5.5 Rewrite via git-filter-repo Python API

> **Why `git-filter-repo` not `git replace`?** The old pointer SHAs are unreachable (not present as valid objects in the parent's object store), so `git replace` fails with "null type" errors. The `commit_callback` approach via the Python API rewrites tree entries directly.

The automation engine for this mass repair is located at:
[scripts/mass_repair.py](./scripts/mass_repair.py)

```bash
cd <parent-repo-path> && python3 scripts/mass_repair.py
```

> **Critical:** Run from inside the parent repository directory. The script must be separate from the submodule path.

> **Note on `commit_callback` signature:** When using `--partial`, git-filter-repo passes two arguments: `(commit, metadata)`. Using only `(commit)` will raise a `TypeError`.

### 5.6 Final Validation Audit

After the rewrite, verify every pointer is a valid `commit` object in the submodule:

```bash
git log --reverse --format="%H | %as | %s" -- <submodule-path> | \
while IFS=' | ' read -r sha date msg; do
    ptr=$(git ls-tree "$sha" <submodule-path> 2>/dev/null | awk '{print $3}')
    vtype=$(git -C <submodule-subpath> cat-file -t "$ptr" 2>/dev/null)
    if [ "$vtype" != "commit" ]; then
        echo "INVALID: $sha | $date | $ptr | $msg"
    fi
done
echo "Audit complete. Silence = 100% valid."
```

**Zero INVALID lines = safe to push.**

### 5.7 Force-Push

**Do NOT push automatically.** Offer to push and wait for explicit human authorization.

```bash
# Only run after user explicitly says yes
git push --force-with-lease origin main
```

***

## 6. Traceability & Related Conversations

- **Rule Source**: Promotion of **[Git Submodule History Repair Rules](../../../ai-agent-rules/git-submodule-history-repair-rules.md)**.
- **Session Log (Single Pointer)**: Industrialized from the 110-commit surgical repair walkthrough.
- **Session Log (Mass Reconciliation)**: Industrialized from session `aab2c817-85cf-41bf-9db6-e200f8b4275e` — 51-pointer mass repair after full linearization of `ai-agent-rules` history.
