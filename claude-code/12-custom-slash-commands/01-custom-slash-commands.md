---
type: lesson
title: "Custom slash commands"
minutes: 6
---

You'll notice yourself typing the same kind of prompt again and again: "review the diff for security issues", "write release notes for version X", "explain this error". A **custom slash command** saves that prompt as a Markdown file, so `/release-notes v1.4` does the whole thing.

## Where they live

| Location | Command available | Shared? |
|---|---|---|
| `.claude/commands/<name>.md` | In this project | Yes - commit it |
| `~/.claude/commands/<name>.md` | In every project | No - just you |

The file name is the command name: `.claude/commands/changelog.md` becomes `/changelog`. Subfolders group commands - `.claude/commands/db/migrate.md` shows up as `/migrate` with "(project:db)" next to it.

## Anatomy of a command file

```markdown
---
description: Turn changes/<version>.txt into a changelog entry
argument-hint: <version>
allowed-tools: Read
---
Read changes/$ARGUMENTS.txt and write the changelog entry for version $ARGUMENTS.
Output only the entry: the first line is ## $ARGUMENTS, then one "- " bullet per line.
```

| Part | What it does |
|---|---|
| `description` | Shown in the `/` menu so people know what it does |
| `argument-hint` | Shown while typing: `/changelog <version>` |
| `allowed-tools` | Tools the command may use without asking |
| `model` | Optional: run this command on a specific model |
| Body | The prompt itself |
| `$ARGUMENTS` | Everything typed after the command name |
| `$1`, `$2` | Individual arguments, if you need them separately |

## Pulling in live context

A command can include the output of shell commands, run before the prompt is sent - for example the current diff. Write the command inside backticks with a `!` in front, and allow it in `allowed-tools`:

```markdown
---
description: Review the uncommitted changes
allowed-tools: Bash(git diff:*)
---
Here is the diff: !`git diff`

Review it for bugs and missing tests. Report each finding as "- file:line - issue".
```

You can reference files too: `Follow the checklist in @docs/review.md`.

## Using them

- In the console, type `/` to see every command with its description.
- Headless: `claude -p "/changelog v1.4"` - perfect for scripts and CI.

## Commands vs skills

Claude Code also has **skills** (`.claude/skills/<name>/SKILL.md`), a richer format that can bundle scripts and reference files and that Claude can load on its own when a task matches. Simple commands are still the quickest way to save a prompt you type often - and the two share the same `/name` menu.

## What makes a good command

- One job, with a predictable output format.
- Written for any teammate, not just you: no assumptions that only live in your head.
- Arguments for the parts that change (`$ARGUMENTS`), fixed text for the parts that don't.
