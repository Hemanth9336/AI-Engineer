---
type: lesson
title: "Structured run logs"
minutes: 14
---

Topic 066 wrote one rolling log. When many tasks and many people run agents, a second layout pays off: **one envelope file per run, filed by task**.

```text
runs/
  label-issues/
    2026-10-25T07-30-02Z.json
    2026-10-25T09-12-44Z.json
  summarize-pr/
    2026-10-25T08-01-10Z.json
```

| Property | Why it helps |
|---|---|
| The task is the folder name | No field to forget. `ls runs/` lists every task that ever ran |
| One file per run | Never appended to concurrently, so it's safe with parallel runs and easy to copy or archive per task |
| The raw envelope, unmodified | Nothing lost. Fields you didn't think you'd need (`modelUsage`, `duration_api_ms`, `permission_denials`) are still there |
| Timestamped names that sort | `ls` order is time order, and `runs/<task>/2026-10-*` selects a month |

Name files with `date -u +%Y-%m-%dT%H-%M-%SZ` (no colons, so they're safe on every filesystem and in zip files). Add a counter or the session id if two runs can start in the same second.

## What a ledger is

A ledger is the derived table: one row per task, with runs, total cost, average cost, tokens and turns, plus a total row. Rebuild it from the run files whenever you like. The run files are the source of truth, and the ledger is a view.

```text
task,runs,cost_usd,avg_cost_usd,input_tokens,output_tokens,avg_turns
label-issues,2,0.0142,0.0071,2790,10,2
summarize-pr,1,0.0081,0.0081,1501,40,2
TOTAL,3,0.0223,0.0074,4291,50,2
```

## Bad files are data too

A run that crashed may leave an empty or truncated file. The ledger builder must **skip it and say so** on stderr. One corrupt file shouldn't make the whole ledger fail, and it shouldn't silently vanish either.

## Commands this node introduces

`runs/<task>/<timestamp>.json`, `date -u +%Y-%m-%dT%H-%M-%SZ`, and a ledger as a derived view.
