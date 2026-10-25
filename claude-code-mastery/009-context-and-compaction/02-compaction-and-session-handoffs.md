---
type: lesson
title: "Compaction and session handoffs"
minutes: 14
---

When the window approaches its limit, Claude Code **compacts**: it replaces the conversation with a structured summary and keeps going. You can also compact on purpose.

```text
/compact focus on the slugify change and the open test question
```

Focus instructions decide what the summary keeps instead of leaving it to the automatic pass. `/autocompact 500k` sets how full the window gets before the automatic pass runs.

## What survives compaction

| Mechanism | After compaction |
|---|---|
| System prompt, output style | Still apply |
| Project-root `CLAUDE.md`, auto memory | Re-injected from disk |
| A plan written in plan mode | Re-injected from disk |
| Files the agent read or edited | Up to five, most recently modified, are re-read |
| Nested `CLAUDE.md` and path-scoped rules | Reloaded only when a matching file is touched again |
| Everything else said in the conversation | Only what made it into the summary |

The lesson: **anything important that lives only in the conversation is at risk.** If it matters, put it on disk.

## Handoffs: compaction you control

A handoff file is a short document a session writes for the *next* session. It is better than relying on compaction or `--continue` when you want a clean window, a different person, or a different machine to pick up the work.

```markdown
## Goal
Ship slugify() with tests.

## Done
- slugify implemented in text.py (lowercase, spaces/underscores to hyphens, punctuation dropped)

## Next
- Add test_text.py with unittest cases for slugify

## Files
- text.py
```

Write it **from the session that did the work** - it has the context - by resuming that session:

```bash
claude -p "Write HANDOFF.md ..." --resume "$SESSION_ID"
```

Then start the next task in a **fresh** session that reads only the handoff: `claude -p "Read HANDOFF.md and complete the Next section"`. If the fresh session finishes the work, the handoff carried everything that mattered.

## Commands this node introduces

`/compact [focus]` summarizes now; `/autocompact <tokens>` moves the automatic threshold; `--resume <id>` continues a specific session headlessly.
