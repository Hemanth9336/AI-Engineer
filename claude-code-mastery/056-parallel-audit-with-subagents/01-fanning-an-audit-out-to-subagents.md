---
type: lesson
title: "Fanning an audit out to subagents"
minutes: 19
---

Topic 023 fanned identical scouts over services. An audit is different: it needs **different specialists**, each with its own checklist, and a merged result you can act on.

## Specialists as definition files

```markdown
---
name: secrets-auditor
description: Finds hard-coded credentials in source files. Use for the secrets part of an audit.
tools: Read, Grep, Glob
model: haiku
---
Search app/ for hard-coded secrets (variables named *TOKEN*, *SECRET*, *PASSWORD*, *KEY* assigned string literals).
Reply with only a JSON array: [{"file": "...", "line": N, "kind": "secret", "severity": "high", "detail": "..."}].
Never include the secret value itself.
```

| Choice | Why |
|---|---|
| `tools: Read, Grep, Glob` | An auditor that can't write can't "helpfully" fix, delete, or leak anything. The allowlist is enforced, not a suggestion |
| `model: haiku` | Pattern searches are cheap work. Save the expensive model for the merge or the fix |
| JSON-only reply | The parent receives **only** the final message, so make it small and machine-readable |
| "Never include the value" | Findings get pasted into tickets and chats. Cite the location, not the secret |

## What goes where

```text
main context:     prompt → Agent(secrets-auditor) → [JSON findings] → Agent(deps-auditor) → [JSON findings] → write reports
subagent context: Grep app/ → Read app/config.py (file contents live here) → final JSON
```

Each subagent's file reads, grep hits, and dead ends stay in **its** transcript, `~/.claude/projects/<project>/<session>/subagents/agent-<id>.jsonl`. The main conversation pays only for the two arrays. Subagents run in the background by default and report back when done, so the two specialists can work at the same time.

## Merge deterministically

Don't ask the model to merge reports in prose. Save each specialist's array as a file and merge with code: dedupe, stamp each finding with its `source`, and sort by severity, then file, then line. The merge is then testable, and a rerun with the same reports gives byte-identical output.

## Commands this node introduces

Read-only specialist definitions in `.claude/agents/`, JSON-only subagent replies, `subagents/agent-*.jsonl` as proof of isolation, and a code merge of the reports.
