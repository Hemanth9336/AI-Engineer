---
type: lesson
title: "Instruction files: the CLAUDE.md pattern"
minutes: 6
---

Every session starts with zero knowledge of your project. You could paste "tests run with `./run-tests.sh --fast`, end answers with our sign-off, don't touch vendor/" into every prompt - or put it in a file the harness loads every time.

## How Claude Code loads CLAUDE.md

At the start of a session it reads instruction files and injects them into the context as project instructions (the system prompt work from topic 16, but per project):

| File | Scope | Shared? |
|---|---|---|
| `~/.claude/CLAUDE.md` | Every project, for you | No |
| `CLAUDE.md` in the project root | This project | Yes - commit it |
| `CLAUDE.md` in a subfolder | Loaded when work touches that folder | Yes |
| `CLAUDE.local.md` | This project, just you | No (git-ignored) |

Other harnesses have the same pattern under different names - `AGENTS.md`, `.cursor/rules`, `GEMINI.md`. The content rules are identical.

## What belongs in it

| Put in | Leave out |
|---|---|
| Exact commands: build, test, lint, run | Things the model can read from the code |
| Project-specific rules: "never call pytest directly" | Generic advice ("write clean code") |
| Where things live, non-obvious conventions | Secrets, tokens, internal URLs with credentials |
| Output conventions the team relies on | Long tutorials - link to docs instead |

## Writing rules that get followed

Topic 16's lessons apply directly:

- **Specific and checkable.** "Run tests with `./run-tests.sh --fast`. Never call pytest directly." beats "use the right test command".
- **Short.** It's loaded every session and competes for the window (topic 17). Aim for under a page.
- **Headings and bullets.** Easy to scan for the model and for the humans who maintain it.
- **Say why when it isn't obvious.** "pytest directly skips the database fixtures" helps the model generalize.

## Prove it

An instruction file is a prompt change - so treat it like one (topic 33). Pick a task where the rule should change behavior, run it **with** and **without** the file, and compare what the agent actually did: which commands ran, what the answer looked like. If nothing changes, the rule isn't doing anything.
