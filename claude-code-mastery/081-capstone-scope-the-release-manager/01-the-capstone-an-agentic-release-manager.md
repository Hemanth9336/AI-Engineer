---
type: lesson
title: "The capstone: an agentic release manager"
minutes: 23
---

For the last eight steps you'll build one real tool, end to end, with everything this course covered: an **agentic release manager** for a small pricing app. Given the current commit, it decides whether the app can ship and prepares everything a human needs to press the button.

## What you will build

```text
                   ┌──────────────────────── coordinator (script) ────────────────────────┐
 tests/ ──► check.py ──► verdict.json ──► triage worker (agent) ──► triage.json ─┐        │
 git log ─► changelog.py ─► CHANGELOG.md ─► notes worker (agent) ─► notes-draft.md ─► merge ──► RELEASE_NOTES.md
            │                                                                              │
            └── activity hook (PostToolUse) ──► activity.jsonl    guard (PreToolUse) ──► guard.jsonl
 verdict.json ──► serve.py on 127.0.0.1:8787 (GET /verdict), run as a transient systemd unit
```

| Step | You build | Course skills it exercises |
|---|---|---|
| 081 | The spec: what "done" means | Specs and acceptance criteria |
| 082 | The design doc: which parts are scripts and which are agents | Tool choice, cost and reliability |
| 083 | The release check runner and its verdict file | Headless automation, exit codes |
| 084 | The activity hook and the changelog generator | Hooks, git |
| 085 | The triage and notes subagents, and the coordinator | Subagents, `--agent`, fan-out, artifacts |
| 086 | The guard, and a seeded regression fixed by the agent | PreToolUse guardrails, verification |
| 087 | The verdict over HTTP | Operating a service |
| 088 | The README and the retro | Documentation, judgement |

## The rules of the build

1. **Exact things are scripts.** Running tests, counting failures, grouping commits, merging files, blocking commands and serving JSON never need a model.
2. **Agents get the judgement jobs**, explaining failures and writing for customers, with the smallest tool set that works.
3. **Everything leaves a file** in `release/out/`, so every step can be inspected and tested on its own.
4. **Publishing stays human.** The release manager never tags or pushes.

Each step's folder starts from the reference solution of all the earlier steps. Do them in order, but a mistake in one never blocks the next.

## Commands this node introduces

The capstone architecture, `release/out/` as the artifact folder, and the script-vs-agent rule.
