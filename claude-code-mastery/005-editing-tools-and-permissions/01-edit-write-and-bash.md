---
type: lesson
title: "Edit, Write, and Bash"
minutes: 14
---

Three tools let the agent change the machine. Each has its own contract, and knowing them explains most of what you see in a transcript.

| Tool | What it does | Contract |
|---|---|---|
| **Edit** | Replaces an exact string in an existing file | The file must have been **Read** in this session first; `old_string` must match exactly once (or set `replace_all`) |
| **Write** | Creates a file, or overwrites one completely | Overwriting an existing file also requires a prior Read |
| **Bash** | Runs a shell command in a persistent shell | Output (stdout and stderr) comes back as the tool result; long-running commands can time out |

## Why Edit wants a Read first

Edit is a surgical string replacement. If the agent had not read the current file, it could be replacing text that no longer exists - or that a teammate changed a minute ago. Requiring a Read first keeps edits anchored to what is really on disk. You will see the pattern constantly in transcripts: `Read prices.py` then `Edit prices.py`.

## What a change looks like in the console

When the agent wants to edit in Manual mode, Claude Code shows the proposed diff and asks:

```text
Edit file prices.py
 - return total - pct
 + return round(total * (1 - pct / 100), 2)

Do you want to make this edit?
❯ 1. Yes
  2. Yes, allow all edits during this session (shift+tab)
  3. No, and tell Claude what to do differently (esc)
```

Bash prompts the same way, showing the exact command. Choosing "Yes, and don't ask again" for a command writes an allow rule so that command stops prompting.

## Read-only Bash is different

Not every Bash call prompts. Claude Code recognizes a built-in set of read-only commands - `ls`, `cat`, `grep`, `find`, `git status`, `git diff` and similar - and runs them without asking. Anything that could change state, such as `python3 -m unittest`, `npm install`, or `git commit`, asks first.

## Commands this node introduces

In the console, **Shift+Tab** cycles permission modes; the prompt's "allow all edits" option does the same for edits.
