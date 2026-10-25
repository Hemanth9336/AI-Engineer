---
type: lesson
title: "A background team with artifacts"
minutes: 14
---

Messaging is great when *you* are around to steer. For unattended work (nightly audits, CI fan-out) a simpler pattern is more robust: **independent helpers that each leave an artifact, and a deterministic step that merges them**.

```text
team.sh
  ├── claude -p "<api-audit task>"  --name api-audit  &   → team/api-audit.json   + team/status/api-audit.json (envelope)
  ├── claude -p "<docs-audit task>" --name docs-audit &   → team/docs-audit.json  + team/status/docs-audit.json
  ├── wait for each PID, check its exit code, envelope, and artifact
  └── merge.py team/api-audit.json team/docs-audit.json   → team/REPORT.json (+ REPORT.md)
```

| Rule | Why |
|---|---|
| **One artifact per helper, with a fixed name and schema** | The merge step reads files, not chat. Each helper's output is inspectable on its own |
| **Run helpers in parallel** (`&`, then `wait $pid`) | Wall time is the slowest helper, not the sum |
| **Give helpers only what they need** | Read tools plus Write for their own artifact, `--max-turns`, no Bash. A helper that can only read and write one file can't wander |
| **Name each helper** (`--name`) | It shows up by name in `/list-agents` and session lists while it runs |
| **Check every helper three ways** | The exit code, `is_error` in its envelope, and a valid artifact. Any failure fails the team. Don't merge partial results silently |
| **Merge with code** | Set operations on two JSON files need no model. They're exact, cheap and testable |
| **Clean the artifact folder first** | A stale artifact from yesterday must never pass as today's output |

### When to use what

| Situation | Pattern |
|---|---|
| One task that needs a few focused sub-investigations | Subagents inside one session |
| Several people's sessions coordinating interactively | Cross-session messaging, or agent teams |
| Unattended fan-out whose results must be exact | Background helpers, artifacts and a deterministic merge |

## Commands this node introduces

`claude -p ... &`, `wait "$pid"`, `--name` for helpers, per-helper artifacts and envelopes, and the deterministic merge.
