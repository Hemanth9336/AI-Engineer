---
type: lesson
title: "Checkpoints and /rewind"
minutes: 12
---

Claude Code takes a **checkpoint** before every prompt that starts a turn: a snapshot of the files its editing tools are about to change. `/rewind` (or **Esc Esc** on an empty prompt) opens the list of your prompts and lets you go back.

| Action | Effect |
|---|---|
| Restore code and conversation | Files and chat both return to that point |
| Restore conversation | Chat goes back; files stay as they are |
| Restore code | Files go back; chat stays |
| Summarize from here / up to here | Compress part of the conversation, like a targeted `/compact` |

Checkpoints are saved with the session, so `/rewind` still works after `--resume`. Snapshots are kept for the 100 most recent checkpoints and swept after about 30 days.

## What /rewind cannot reach

Checkpoints track edits made through **Claude's file tools** (Edit, Write). That leaves real gaps:

| Change | Restored by /rewind? |
|---|---|
| A file Claude changed with Edit or Write | Yes |
| A file **only a Bash command** changed - `rm`, `mv`, `sed -i`, a code generator | **No** |
| Edits made by most subagents | No (except files Claude itself had already edited) |
| Your own edits in the editor, other sessions | No |
| Anything outside the filesystem - a database migration, a deploy, a sent email | No |

So `rm -rf legacy/` run through Bash is invisible to `/rewind`. So is a `git commit` or `git push`.

## Rewind is for the conversation too

Even when files are fine, rewinding the conversation is useful: you went down a wrong path, the context is full of failed attempts, and you want to re-ask from a clean point. Use **Restore conversation**, or `/branch` to keep both versions.

## Commands this node introduces

`/rewind` (aliases `/checkpoint`, `/undo`) and **Esc Esc** open the rewind menu; `/branch` forks the conversation.
