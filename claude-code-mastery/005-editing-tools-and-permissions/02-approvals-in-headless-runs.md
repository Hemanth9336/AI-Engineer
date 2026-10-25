---
type: lesson
title: "Approvals in headless runs"
minutes: 14
---

A headless run has nobody to answer a prompt. Since Claude Code v2.1.302, `claude -p` with no permission mode starts in **Manual** mode (config value `default`): reads inside the working folder run, and **every call that would prompt is denied**. The model sees the denial as the tool result and either works around it or gives up.

You can see the denials in the envelope:

```bash
claude -p "Fix apply_discount in prices.py" --output-format json | jq .permission_denials
```

```json
[
  { "tool_name": "Edit", "tool_use_id": "toolu_01...", "tool_input": { "file_path": "/root/.../prices.py", ... } }
]
```

The run "succeeds" (`subtype: success`) but nothing changed. **A successful exit is not proof of work** - always check `permission_denials`, or the files themselves.

## Pre-approving what a run may do

| Flag | Effect in `-p` |
|---|---|
| `--permission-mode acceptEdits` | File edits and common filesystem commands (`mkdir`, `touch`, `rm`, `rmdir`, `mv`, `cp`, `sed`) inside the working folder run without asking |
| `--allowedTools "Bash(python3 -m unittest *)"` | Exactly the commands that match the rule run; others are still denied |
| `--permission-mode dontAsk` | Only pre-approved tools run, everything else is denied - the locked-down CI setting |
| `--permission-mode auto` | A classifier model reviews each call instead of you |
| `--dangerously-skip-permissions` | Everything runs - only inside a disposable container or VM |

`acceptEdits` covers edits, not arbitrary commands: running the tests still needs its own allow rule. Writes to **protected paths** such as `.git`, `.vscode`, `.husky`, and most of `.claude` are never auto-approved by `acceptEdits` either.

A good headless fix grants the least that works:

```bash
claude -p "Fix apply_discount in prices.py, then run the tests" \
  --permission-mode acceptEdits \
  --allowedTools "Bash(python3 -m unittest *)" \
  --output-format json > fixed.json
```

## Commands this node introduces

`jq .permission_denials` lists what a headless run was refused.
