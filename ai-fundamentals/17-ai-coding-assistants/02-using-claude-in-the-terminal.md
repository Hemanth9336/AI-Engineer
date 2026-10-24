---
type: lesson
title: "Using claude in the terminal"
minutes: 8
---

You met `claude -p` in topic 04. Claude Code is a full coding agent that runs in your terminal; in this lab it talks to the gateway, so it uses the lab models.

## Two modes

```bash
claude                    # interactive session in the current directory
claude -p "question"      # print mode: one prompt, one answer, then exit
```

**Interactive** mode is for real work: it reads your project, proposes edits, runs commands, and asks before doing anything risky. Useful commands inside a session:

| Command | Does |
|---|---|
| `/help` | Lists commands |
| `/clear` | Starts a fresh conversation (cheaper, less confusion) |
| `/model` | Switches model, e.g. to `lab-smart` |
| `/init` | Writes a `CLAUDE.md` describing the project for future sessions |
| `Esc` | Interrupts the current action |

**Print** mode (`-p`) is for scripts and pipelines. Its output goes to stdout, so you can redirect or pipe it.

## Useful print-mode flags

```bash
claude -p --model lab-smart "..."           # choose a model
claude -p "..." --tools ""                  # no tools: just answer in text (prompt first)
claude -p --output-format json "..."        # machine-readable result with usage
cat error.log | claude -p "explain this"    # pipe input in
```

`--tools` accepts a list, so put the prompt **before** it - otherwise the prompt is read as a tool name. It matters when you want the code **printed** rather than written: with tools available, the agent may decide to create the file itself and only print a summary.

## Permissions

In interactive mode Claude Code asks before editing files or running commands. You can allow specific tools ahead of time (`--allowedTools "Bash(git diff:*)"`), and project settings live in `.claude/settings.json`. Avoid `--dangerously-skip-permissions` outside a throwaway machine.

## Project memory

A `CLAUDE.md` in the repo root is read at the start of every session. Put the things you'd tell a new teammate there: how to run tests, code style, what not to touch. Short and specific beats long.

## Ask for code that is easy to check

Ask for **only the code**, with no explanation and no Markdown fences, when you redirect into a file. Then always read it - `cat`, `bash -n` for syntax - before running it.
