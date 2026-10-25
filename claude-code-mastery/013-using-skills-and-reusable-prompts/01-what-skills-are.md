---
type: lesson
title: "What skills are"
minutes: 14
---

A **skill** is a folder with a `SKILL.md` file: a description of when to use it, plus instructions (and optionally scripts and reference files) that Claude loads **only when the skill is needed**.

That last part is the point. Every session already carries the system prompt, tools, and `CLAUDE.md`. Skills add almost nothing until used: only each skill's short **description** sits in context. When a request matches a description - or you type `/skill-name` - Claude Code loads the full instructions.

## Two ways a skill runs

| How | Example |
|---|---|
| You invoke it | Type `/summarize-changes` (or `claude -p "/summarize-changes"`) |
| Claude invokes it | You ask "what did I change?"; Claude matches the description and calls the Skill tool |

A skill can opt out of either: `disable-model-invocation: true` makes it manual-only, `user-invocable: false` hides it from the `/` menu.

## Skills your build may bundle

Claude Code ships **bundled skills** - prompt-based workflows rather than fixed logic - such as `/doctor` (setup checkup), `/code-review`, `/debug`, `/batch`, `/loop`, and `/claude-api`. Which ones you have depends on your version and enabled features; type `/` in the console to see the list. `disableBundledSkills` turns them off.

## Where skills live

| Location | Loads in |
|---|---|
| `~/.claude/skills/<name>/SKILL.md` | All your projects on this machine |
| `.claude/skills/<name>/SKILL.md` | This repository - commit it for the team |
| `<plugin>/skills/<name>/SKILL.md` | Wherever the plugin is enabled, as `/plugin:name` |
| Managed settings directory | Every user in the organization |

With the same name in several places: enterprise beats personal, personal beats project, and a skill beats a same-named command file. Plugin skills never collide - they are namespaced.

## Skills versus CLAUDE.md

`CLAUDE.md` is for facts every session needs. A skill is for a **procedure** needed sometimes: a release checklist, a review rubric, a report format. If you catch yourself pasting the same long instructions, it is a skill.

## Commands this node introduces

`/` in the console lists commands and skills; `/skill-name [args]` runs one, interactively or with `claude -p`.
