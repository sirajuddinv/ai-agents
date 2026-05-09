# Stash Preservation Rule (Repo-Scoped, Strict)

## Rule

NEVER drop, pop, clear, or expire a Git stash without explicit per-stash user authorization — even inside a "cleanup",
"tidy up", or "remove backups" instruction. Same gate applies to backup branches (`backup/*`, `bk-*`, `pre-*`), reflog
entries, and dangling commits reachable only via reflog.

## SSOT

- `ai-agent-rules/git-operation-rules.md` §5 — Stash Preservation (Authorization-Gated Destruction)
  - §5.1 Forbidden Without Explicit Authorization (lists `drop`/`pop`/`clear`/reflog expire/`gc --prune=now`)
  - §5.2 Required Pre-Drop Protocol — Inventory → Inspect → Diff → Authorize
  - §5.3 Recovery Window — `git stash store -m "..." <dangling-sha>` while object survives `gc.reflogExpireUnreachable`
    (default ~14 days)
  - §5.4 Same-Class Protections — backup branches, reflog, dangling commits

## Cross-Referenced From

- `.agents/skills/git-commit-edit/SKILL.md` Step 6 — Restore Stashed Work
- `.agents/skills/git-atomic-commit-construction/SKILL.md` §9f — Stash Workflow for Rebase

## Recovery Cookbook

```bash
# If drop SHA was logged in scrollback:
git stash store -m "<recovery message>" <dangling-sha>

# If SHA lost — search dangling commits:
git fsck --unreachable --no-reflogs | awk '/commit/ {print $3}' \
  | xargs -I{} git log -1 --format="%H %s" {} | grep -i "WIP\|stash\|<known-message>"
```

## Origin

Recorded after agent dropped `stash@{0}` (`6982616`) inside a "cleanup full" batch on 2026-05-10 without per-stash
authorization. User invoked recovery via `git stash store`; stash had no unique semantic content (formatting-only diff
vs current SKILL.md) and was subsequently dropped with explicit authorization.
