---
type: lesson
title: "SKILL.md anatomy"
minutes: 14
---

A skill is a folder; `SKILL.md` is its entry point.

```text
.claude/skills/standup/
├── SKILL.md          # required: frontmatter + instructions
├── template.md       # optional: a format Claude fills in
└── scripts/
    └── stats.sh      # optional: a script the skill runs
```

## Frontmatter

YAML between `---` markers, **on the very first line** - otherwise the whole file is treated as content.

```yaml
---
description: Writes a standup report from the last day of git commits. Use when the user asks for a standup or daily update.
argument-hint: "[since]"
allowed-tools: Bash(git log *)
---
```

| Field | Purpose |
|---|---|
| `description` | **The trigger.** What it does and when to use it; the key use case first. Truncated at 1,536 characters in the listing |
| `name` | Command name; defaults to the folder name |
| `argument-hint` | Shown in autocomplete |
| `allowed-tools` | Tools pre-approved while the skill runs |
| `disable-model-invocation` | `true` = only you can run it, with `/name` |
| `context: fork` | Run in an isolated subagent |
| `model`, `effort` | Override for the turn the skill runs |
| `paths` | Only auto-load when working on matching files |

Unknown field names are ignored silently, so a typo such as `allowed_tools` simply does nothing.

## The body

Plain markdown instructions, plus two powerful substitutions:

- **Arguments**: `$ARGUMENTS` is everything after the command; `$0`, `$1` are positional (0-based).
- **Dynamic context**: a line `` !`git log --since="1 day ago" --pretty=format:"%h %s"` `` runs **before** Claude sees the skill and is replaced with the command's output. The instructions arrive with real data already inlined.

Injected commands never prompt. Read-only commands pass; anything a permission rule would not allow aborts the skill with `Shell command permission check failed` - pre-approve it with `allowed-tools`.

## Commands this node introduces

`/standup` (any skill folder name) runs the skill; `${CLAUDE_SKILL_DIR}` in the body points at the skill's own folder for bundled scripts.
