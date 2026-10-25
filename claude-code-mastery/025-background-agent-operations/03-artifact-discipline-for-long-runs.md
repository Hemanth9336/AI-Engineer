---
type: lesson
title: "Artifact discipline for long runs"
minutes: 12
---

Nobody watches a background run. Everything you need to know afterwards must be **on disk** in a place you chose.

## The contract to put in the prompt

1. **Where to write**: one artifacts folder - `artifacts/` - and nowhere else.
2. **Progress as it goes**: append one line per step to `artifacts/progress.log`, so a stuck run shows where it stopped.
3. **The deliverable**: `artifacts/report.md` in a fixed format.
4. **A completion marker, last**: write `artifacts/DONE` only after everything else. A report without `DONE` is a run that died part-way.
5. **No questions**: the run must not ask; if information is missing, say so in the report.

## Permissions decide whether it finishes

A background session that hits a permission prompt goes to `blocked` and waits - possibly all night. Before dispatching:

- Pre-approve exactly what it needs (an allow rule for writing `artifacts/`, the read-only commands it uses).
- Deny what it must never do (`git push`, deploy scripts, network tools).
- Choose the mode deliberately: `--permission-mode acceptEdits` for a run that only writes its own artifacts in this folder.

## Collecting results

```bash
state=$(claude agents --json --all | jq -r '.[] | select(.name == "audit-025") | .state')
[ "$state" = done ] && [ -f artifacts/DONE ] && cat artifacts/report.md
claude logs audit-025 > artifacts/session.log
```

Check the marker **and** the state. `done` with no `DONE` file means the agent finished talking but skipped part of the contract.

## Commands this node introduces

`jq -r '.[] | select(.name == "...") | .state'` reads one session's state from `claude agents --json`.
