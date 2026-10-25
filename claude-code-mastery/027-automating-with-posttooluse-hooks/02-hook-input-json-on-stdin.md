---
type: lesson
title: "Hook input: JSON on stdin"
minutes: 14
---

Every command hook gets one JSON object on **stdin** and answers with its **exit code** and, optionally, **one JSON object on stdout**.

## What arrives

```json
{
  "session_id": "4f1c...",
  "transcript_path": "/root/.claude/projects/-root-mastery-027-audit/4f1c....jsonl",
  "cwd": "/root/mastery/027-audit",
  "permission_mode": "acceptEdits",
  "hook_event_name": "PostToolUse",
  "tool_name": "Write",
  "tool_input": { "file_path": "/root/mastery/027-audit/notes/standup.md", "content": "..." },
  "tool_response": { "filePath": "/root/mastery/027-audit/notes/standup.md", "type": "create" },
  "tool_use_id": "toolu_01ABC...",
  "duration_ms": 12
}
```

- `tool_input` is the tool's arguments; file paths are **absolute**.
- `tool_use_id` links the event to the exact tool call in the transcript.
- `$CLAUDE_PROJECT_DIR` (an environment variable) is the project root - use it instead of `cwd`, which moves when Claude `cd`s.

## Reading it

```python
import json, os, sys
ev = json.load(sys.stdin)
proj = os.path.realpath(os.environ["CLAUDE_PROJECT_DIR"])
path = os.path.realpath(ev["tool_input"]["file_path"])
rel = os.path.relpath(path, proj)        # resolve both sides: symlinks make raw prefixes lie
```

```bash
jq -r '.tool_input.file_path'            # the same in a shell hook
```

## Answering

| Exit | Meaning |
|---|---|
| `0` | Success. If stdout is **one JSON object**, its fields apply |
| `2` | Blocking error: stderr goes to Claude (PreToolUse blocks the call; PostToolUse shows it next to the result) |
| anything else | Non-blocking error: a notice, and **the action goes ahead** |

A PostToolUse hook that wants Claude to know something prints:

```json
{ "hookSpecificOutput": { "hookEventName": "PostToolUse", "additionalContext": "audit: recorded notes/standup.md" } }
```

`additionalContext` lands in Claude's context next to the tool result. `decision: "block"` with a `reason` pushes back ("fix the lint errors"); `updatedToolOutput` replaces what Claude sees. Strings are capped at 10,000 characters, and stdout must hold **only** the JSON object - a stray `echo` breaks it.

## Commands this node introduces

`$CLAUDE_PROJECT_DIR` and the `additionalContext` hook output field.
