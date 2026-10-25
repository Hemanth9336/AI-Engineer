---
type: lesson
title: "What persists between sessions"
minutes: 14
---

A session's conversation ends when the session does. What carries into the **next** session is only what is on disk and loaded at startup.

| Persists | How | Who writes it |
|---|---|---|
| `CLAUDE.md` files | Loaded in full at startup | You (or Claude when you ask) |
| **Auto memory** | `MEMORY.md` index loaded at startup (first 200 lines or 25 KB); topic files read on demand | Claude |
| The transcript | Saved to `~/.claude/projects/...`; only used if you `--resume` or `--continue` | Claude Code |
| Your files and git history | Read with tools when needed | Everyone |

Nothing else. A port number you mentioned in passing, a decision you agreed on, "don't use that library" - gone, unless one of the mechanisms above captured it.

## Auto memory

Auto memory is Claude's own notebook, on by default in local sessions. Each project gets a folder:

```text
~/.claude/projects/<project>/memory/
├── MEMORY.md             # index: one line per memory, loaded every session
├── staging_port.md       # one topic file per memory
└── feedback_testing.md
```

`<project>` comes from the git repository (so worktrees share one memory), or from the folder path outside git. Claude saves memories when you correct it or tell it something worth keeping - "remember that the API tests need a local Redis" - and you see "Saved 1 memory" or "Recalled 1 memory" in the console.

Memory is **machine-local**: not committed, not shared with teammates, not present in cloud sessions. Team knowledge belongs in `CLAUDE.md`.

## CLAUDE.md or memory?

| Fact | Where |
|---|---|
| "Run `make check` before finishing" (for everyone) | `CLAUDE.md` |
| "I prefer short answers" | Auto memory or `~/.claude/CLAUDE.md` |
| "Staging DB is on port 6543 on *my* setup" | Auto memory |

Toggle auto memory with `/memory`, or disable it with `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`.

## Commands this node introduces

`/memory` shows CLAUDE.md files and the auto memory folder, and toggles auto memory.
