---
type: lesson
title: "The three instruction levels"
minutes: 14
---

Instructions can come from several files, and Claude Code loads **all** of them - they are concatenated, not replaced.

| Level | Location | Shared with | Typical content |
|---|---|---|---|
| **Managed policy** | `/etc/claude-code/CLAUDE.md` (Linux), `/Library/Application Support/ClaudeCode/CLAUDE.md` (macOS) | Everyone on the machine, set by IT | Security and compliance rules |
| **User** | `~/.claude/CLAUDE.md` | Only you, every project | Your personal style and tooling habits |
| **Project** | `./CLAUDE.md` or `./.claude/CLAUDE.md` | The team, via git | Build commands, conventions, architecture |
| **Local** | `./CLAUDE.local.md` (gitignored) | Only you, this project | Your sandbox URLs, test accounts |

## Load order

Files load from the broadest scope to the most specific: managed, then user, then the project files from the filesystem root down to your working folder, with each folder's `CLAUDE.local.md` after its `CLAUDE.md`. Instructions closer to where you launched are read **last**.

## Who wins a conflict

There is no hard override. All the files reach the model, and the docs are blunt: if two instructions contradict each other, Claude may pick one arbitrarily. In practice, later and more specific instructions tend to win, but "tend to" is not a guarantee.

So resolve conflicts on purpose:

- Make the specific rule say that it overrides: "In this project, end summaries with `Reviewed-by: release-bot` **instead of any personal signature**."
- Keep user-level rules about **you** (tone, editor habits) and project rules about **the code**, so they rarely collide.
- Things that must hold everywhere - company policy - go in the **managed** file, or better, in managed settings and hooks that are enforced.

## Commands this node introduces

`/memory` lists every instruction file in effect - user, project, and local - and opens any of them.
