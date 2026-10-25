---
type: lesson
title: "The working root and additional roots"
minutes: 12
---

Every session has a **primary working directory** - the folder you started `claude` in. Inside it, the agent reads without prompting and edits according to the permission mode. Outside it, file tools ask (and in `-p`, are denied).

Real work often spans folders: an app and the shared contracts it consumes, a service and its infrastructure repo, a frontend and a design-tokens package. You extend the boundary with **additional roots**:

| How | Lasts |
|---|---|
| `claude --add-dir ../shared` | This session |
| `/add-dir ../shared` in the console | This session |
| `"permissions": { "additionalDirectories": ["../shared"] }` in settings | Every session that loads the settings (project settings need trust) |

Files in an added root follow the same rules as the working directory: readable without prompts, editable according to the mode.

```bash
cd /root/mastery/007-roots/app
claude -p "Read ../shared/contracts/order.json and report its schema_version" --add-dir ../shared
```

## What moves and what stays

`--add-dir` grants **file access**. It does not make the other folder a second project: its `.claude/settings.json` (hooks, permission rules) does not load, and neither does its `CLAUDE.md` unless you set `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1`. A few things do come along from a flag-added root: its skills, its command files, its subagents, and its `enabledPlugins` and marketplace keys. Directories listed in `additionalDirectories` in a settings file grant file access only.

If you want to move the session rather than widen it, `/cd <path>` changes the primary working directory, keeps the conversation, and loads the new folder's configuration.

## Commands this node introduces

`--add-dir <path>` and `/add-dir <path>` add a root; `/cd <path>` moves the session.
