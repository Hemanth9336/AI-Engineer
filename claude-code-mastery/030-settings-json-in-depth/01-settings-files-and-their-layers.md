---
type: lesson
title: "Settings files and their layers"
minutes: 14
---

Everything you have configured so far - permissions, hooks, the status line, env vars - lives in `settings.json` files. There are five layers, and knowing which one wins saves hours.

| Layer | File | Who it is for | In git? |
|---|---|---|---|
| Managed | `managed-settings.json` (or MDM / server-managed) | The organization | Deployed by IT |
| Command line | `--settings <file or json>`, `--permission-mode`, ... | This one run | - |
| Project local | `.claude/settings.local.json` | You, in this project | **No** |
| Project | `.claude/settings.json` | Everyone on the repo | **Yes** |
| User | `~/.claude/settings.json` | You, everywhere | - |

**Precedence, highest first:** managed, command line, project local, project, user. A key set higher overrides the same key lower down.

## Merging, not replacing

- **Permission lists merge** across layers: an `allow` in your user file and a `deny` in the project file both apply - and deny always wins.
- **Hooks** from every layer run (an identical handler runs once).
- **Plain keys** (`model`, `statusLine`, `editorMode`) take the highest layer's value.
- `env` blocks are merged key by key: a local `LOG_LEVEL` overrides the project's `LOG_LEVEL` and leaves its `APP_ENV` alone.

## Local settings stay local

`.claude/settings.local.json` is for personal overrides - a different model, a noisier log level, approvals you clicked. When Claude Code creates it, it adds it to your global git excludes; when **you** create it, add it to `.gitignore` yourself.

## See what is in force

`/config` edits common settings, `/permissions` lists every rule with its source file, `/hooks` lists hooks, and `/status` shows which settings sources loaded. Add `"$schema": "https://json.schemastore.org/claude-code-settings.json"` and your editor validates the file as you type.

## Commands this node introduces

`--settings`, `/config`, `/status`, and the `$schema` line.
