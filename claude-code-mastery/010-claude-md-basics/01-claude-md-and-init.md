---
type: lesson
title: "CLAUDE.md and /init"
minutes: 14
---

`CLAUDE.md` is a markdown file of standing instructions that Claude Code loads into **every session** started in that project. It is how you stop repeating "use pytest", "never touch the migrations folder", and "run make lint before you finish" in every prompt.

## Where the project file lives

`./CLAUDE.md` or `./.claude/CLAUDE.md` at the project root, committed so the whole team shares it. Claude Code also loads `CLAUDE.md` files from **every parent directory** of where you start it, and loads `CLAUDE.md` files in **subdirectories** on demand, when the agent first reads or edits a file there.

When it loads, the content is injected at the top of the conversation as instructions:

```text
Contents of /root/mastery/010-house/CLAUDE.md (project instructions, checked into the codebase):
...
```

## /init: a generated starting point

In the console, `/init` asks Claude to analyse the codebase and write a starter `CLAUDE.md`: build and test commands, layout, conventions it can see. If a `CLAUDE.md` exists, `/init` suggests improvements instead of overwriting it. With `CLAUDE_CODE_NEW_INIT=1` set, `/init` runs an interactive flow that can also set up skills, hooks, and a personal `CLAUDE.local.md`.

Treat the output as a draft. `/init` can only write down what the code shows; the most valuable lines are the ones it cannot discover - "staging deploys are frozen on Fridays", "every new module needs an owner header".

## Context, not configuration

`CLAUDE.md` is read by the model; nothing enforces it. Claude usually follows clear instructions, but a rule that **must** hold - never edit `.env`, always run the linter - belongs in a permission rule or a hook (topics 006 and 027). Use `CLAUDE.md` for guidance, and a deterministic mechanism for guarantees.

## Commands this node introduces

`/init` drafts a CLAUDE.md; `/memory` lists and opens the instruction files; `/context` confirms which ones loaded.
