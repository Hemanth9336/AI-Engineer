---
type: lesson
title: "Command files and where they live"
minutes: 14
---

A **custom slash command** is a markdown file whose name becomes a command. `.claude/commands/release-notes.md` gives you `/release-notes`.

| Location | Scope | Shows in `/` menu as |
|---|---|---|
| `.claude/commands/<name>.md` | This project - commit it for the team | `/name` (project) |
| `~/.claude/commands/<name>.md` | All your projects | `/name` (user) |
| `.claude/commands/<dir>/<name>.md` | Grouped in a subfolder | `/name`, with the folder shown as a label |
| `<plugin>/commands/<name>.md` | Wherever the plugin is enabled | `/plugin:name` |

The body is the prompt. When you run the command, Claude Code expands the file into the conversation:

```text
<command-name>/release-notes</command-name>
<command-args>2.4.0</command-args>
Write release notes for version 2.4.0 ...
```

## Commands are CLI tools too

Because `-p` accepts a slash command as the prompt, a command file is a reusable, versioned job you can script:

```bash
claude -p "/release-notes 2.4.0" --output-format json > notes.json
```

That is the main reason to write one: a task the team repeats - release notes, a changelog check, a migration review - stops being a paragraph people retype and becomes a single, identical command in CI, in a cron job, or at a terminal.

## Commands versus skills

Command files are the **older format**, and they still work. Skills are the newer, richer version of the same idea: a skill folder can hold supporting files and scripts, and Claude can choose to load it by its description. If a skill and a command share a name, **the skill wins**. For new work, prefer a skill; keep commands for short, prompt-only jobs - or when you want the simplest possible file.

## Commands this node introduces

`/release-notes 2.4.0` (any command file) runs it in the console; `claude -p "/name args"` runs it headlessly.
