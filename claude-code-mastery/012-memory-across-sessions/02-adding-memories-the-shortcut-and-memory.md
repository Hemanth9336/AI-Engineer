---
type: lesson
title: "Adding memories: the # shortcut and /memory"
minutes: 14
---

There are three ways to put a fact into memory on purpose.

## 1. Ask

The current way is plain language:

```text
remember that the staging database listens on port 6543
```

Claude writes a topic file to the auto memory folder and adds a one-line pointer to `MEMORY.md`. Headless runs work the same way:

```bash
claude -p "Remember for future sessions: the staging database listens on port 6543."
```

To put a rule in `CLAUDE.md` instead, say so: "add this to CLAUDE.md: ...".

## 2. The # shortcut

Earlier Claude Code builds treated a prompt starting with `#` as "save this line to memory" and asked which memory file to put it in. Current builds have removed that shortcut, so a leading `#` is just text. If you see `# always use pnpm` in older guides, the modern equivalent is "remember: always use pnpm", or adding the line through `/memory`.

## 3. /memory

`/memory` lists every instruction file in effect (user, project, local), including ones that do not exist yet, and opens the one you pick in your editor - selecting a missing file creates it. It also toggles auto memory and opens the auto memory folder, where every memory is a plain markdown file you can edit or delete.

## Prove recall properly

A memory test is only meaningful if the answer cannot come from anywhere else:

1. Save the fact in **one** session.
2. Ask in a **new** session - no `--resume`, no `--continue`.
3. Make sure the fact is not in the project files, so the agent cannot just grep for it.

If recall fails, check `MEMORY.md` has the pointer line, the topic file holds the fact, and you started the second session in the same project (memory is per project).

## Commands this node introduces

`claude -p "Remember ..."` saves a fact headlessly; `ls ~/.claude/projects/*/memory/` shows what was saved.
