---
type: lesson
title: "The coordinator and its workers"
minutes: 23
---

The release manager has two text jobs. Each becomes a **worker**: a project agent with a narrow brief, the smallest tool set, and one output file. A **coordinator** script runs the deterministic steps, starts the workers, checks what they left, and merges.

## Workers as project agents

```markdown
---
name: triage
description: Read the release check output and say whether the release can go and what is failing.
tools: Read, Write
---
You are the release triage worker. Read release/out/verdict.json and release/out/test-output.txt.
Write release/out/triage.json as {"status": ..., "failing": [...], "summary": "..."}. Do not edit any other file.
```

Run a worker headless **as** that agent. Its body becomes the system prompt and its `tools:` list is enforced:

```bash
claude -p "Triage the release check." --agent triage --permission-mode acceptEdits --max-turns 6 --output-format json
```

Inside an interactive session, the same file is a subagent that Claude can delegate to (topic 024). Defining workers once in `.claude/agents/` gives you both.

## The coordinator's job

1. Run the scripts (`check.py`, `changelog.py`). If the check *couldn't run* (exit 2), stop there.
2. Start both workers **in parallel** (`&`) and `wait` on each.
3. **Verify every artifact** (valid `triage.json`, non-empty `notes-draft.md`). A missing file means exit 2, with no notes.
4. **Merge deterministically.** The verdict in the release notes comes from `verdict.json`, **never from a worker**. If triage disagrees, the release check wins and the notes say so.

| Exit | Meaning |
|---|---|
| 0 | go, and the notes are written |
| 1 | no-go (or the workers disagree with the check). The notes are still written, for the humans |
| 2 | The pipeline broke. No notes |

## Commands this node introduces

`claude --agent <name>`, `tools:` in agent frontmatter, worker artifacts and envelopes, parallel workers with `wait`, and a deterministic merge where the check outranks the workers.
