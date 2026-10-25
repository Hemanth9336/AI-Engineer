---
type: lesson
title: "Arguments, frontmatter, and commands versus skills"
minutes: 14
---

## Arguments

| Placeholder | Expands to |
|---|---|
| `$ARGUMENTS` | Everything typed after the command |
| `$0`, `$1`, ... | One positional argument - **0-based**, so `$0` is the first |
| `$ARGUMENTS[1]` | Same as `$1` |

If the file uses no placeholder, Claude Code appends `ARGUMENTS: <value>` to the end instead. Using `$1` for the first argument is the classic mistake: with a single argument, `$1` stays literally `$1`.

## Frontmatter

Command files accept the same frontmatter as skills (except `name` and `paths`):

```markdown
---
description: Write release notes for one version from CHANGELOG.md
argument-hint: <version>
allowed-tools: Read
model: haiku
---

Write release notes for version $ARGUMENTS using only the matching section of CHANGELOG.md.
Format: a one-line headline, then one bullet per change, user-facing language.
```

- `description` shows in the `/` menu (and lets Claude use the command on its own).
- `argument-hint` shows in autocomplete.
- `allowed-tools` pre-approves what the command needs.
- `model` runs the command on a cheaper or stronger model for that turn.

Injected `` !`command` `` lines work here too.

## Choosing

| Need | Use |
|---|---|
| A short prompt with an argument | Command file |
| Supporting files, scripts, or examples | Skill folder |
| Claude should apply it unprompted | Skill (with a good description) |
| Share across many repos | Plugin (next topic) |

## Commands this node introduces

`argument-hint`, `$ARGUMENTS`, and `$0` - the parts that make a command take input.
