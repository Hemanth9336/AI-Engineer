---
type: lesson
title: "Plan mode"
minutes: 14
---

**Plan mode** is the permission mode for thinking before touching anything. Claude reads files and runs read-only commands, then writes a plan - and edits stay blocked until you approve it.

## Entering it

| Where | How |
|---|---|
| Console | **Shift+Tab** until the status bar shows plan mode, or prefix one prompt with `/plan` |
| Launch | `claude --permission-mode plan` |
| Headless | `claude -p "..." --permission-mode plan` |
| Project default | `"permissions": { "defaultMode": "plan" }` in `.claude/settings.json` |

## What it allows

- Reads, searches, and the built-in read-only commands (`ls`, `cat`, `grep`, `git log`, `git diff`, ...).
- Other shell commands go to the auto-mode classifier where auto mode is available, and otherwise prompt.
- Writing **the plan file itself** - Claude keeps its plan in `~/.claude/plans/<name>.md`.
- Nothing else. No edits to your source, no commits, no installs.

## Why it is worth the extra step

- **You review the approach, not 400 lines of diff.** A wrong approach is cheap to fix in a plan and expensive in code.
- **The plan is an artifact.** It survives compaction (it is re-injected from disk), it can be saved next to the code, and a teammate can review it.
- **It forces exploration first.** In plan mode Claude is instructed to read the relevant code and reuse what exists before proposing anything new.

## What a good plan contains

1. The goal in one sentence.
2. The files to change and what changes in each.
3. The order of steps.
4. How to verify - the exact test command.
5. Risks or open questions.

## Commands this node introduces

`/plan <prompt>` plans one request; `--permission-mode plan` starts a planning session; `Ctrl+G` opens a proposed plan in your editor.
