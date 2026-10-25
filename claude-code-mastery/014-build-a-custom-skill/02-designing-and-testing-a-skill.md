---
type: lesson
title: "Designing and testing a skill"
minutes: 14
---

A skill that does the right thing but never triggers is useless; one that triggers on everything is worse.

## Write the description for the matcher

- Lead with **what it produces**: "Writes a standup report from git commits."
- Then **when**: "Use when the user asks for a standup, daily update, or what they did yesterday."
- Use the words people actually type. If nobody says "synchronous status digest", do not write it.

## Keep the body procedural

- Numbered steps and an exact output format beat prose.
- Put the most important instructions at the **top**: after compaction, long skill bodies are truncated from the end.
- Inline the data with `` !`command` `` rather than asking Claude to go find it - it is faster, cheaper, and grounded.

## Test it three ways

1. **By name**: `claude -p "/standup"` - proves the file loads and the injected command works.
2. **By description**: `claude -p "what did I do yesterday?"` - proves Claude chooses it.
3. **On edge cases**: no commits in the window, a huge diff, a detached HEAD.

## When it never triggers

| Symptom | Likely cause |
|---|---|
| `/standup` is unknown | Wrong folder (`.claude/skill/`), or `SKILL.md` misnamed |
| Loads but ignores frontmatter | `---` is not the first line, or the YAML does not parse |
| Never chosen automatically | Vague description, or `disable-model-invocation: true` |
| Aborts on start | An injected command is not allowed - add it to `allowed-tools` |

Edits to `SKILL.md` apply live in a running session; a brand-new skills folder needs a restart.

## Commands this node introduces

`claude -p "/name args"` tests a skill headlessly; the envelope's `result` is its output.
