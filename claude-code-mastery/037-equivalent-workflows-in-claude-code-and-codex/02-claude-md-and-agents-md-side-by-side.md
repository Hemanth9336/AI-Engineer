---
type: lesson
title: "CLAUDE.md and AGENTS.md side by side"
minutes: 10
---

Project instructions are the first thing to share between tools, and the easiest to let drift.

## How each tool finds instructions

| | Claude Code | Codex CLI |
|---|---|---|
| Personal | `~/.claude/CLAUDE.md` | `~/.codex/AGENTS.md` (or `AGENTS.override.md`) |
| Project | `./CLAUDE.md` or `./.claude/CLAUDE.md`, plus every parent directory | `AGENTS.md` in each directory from the repo root down to where you started |
| Personal, per project | `CLAUDE.local.md` (git-ignored) | `AGENTS.override.md` wins over `AGENTS.md` in the same directory |
| Subdirectories | Loaded on demand when Claude works there | Only directories between the root and your start directory |
| Imports | `@path/to/file` expands inline | No import syntax |
| Size | Keep it short, it costs tokens every turn | Stops adding files at `project_doc_max_bytes` (32 KiB by default) |
| Check what loaded | `/memory` | Ask: `codex --ask-for-approval never "Summarize the current instructions."` |

## Claude Code reads AGENTS.md - with one condition

Since v2.1.277 Claude Code reads `AGENTS.md` by itself, but by default **only when there is no `CLAUDE.md`, `.claude/CLAUDE.md`, or `CLAUDE.local.md`** in your working directory or above it. The moment someone adds a `CLAUDE.md` for one Claude-only tip, Claude stops reading `AGENTS.md` and silently loses every shared rule.

## The portable pattern

Make `AGENTS.md` the one place shared rules live, and give Claude a `CLAUDE.md` that imports it:

```markdown
@AGENTS.md

## Claude Code only
- Use the Edit tool for code changes; do not rewrite files with shell redirection.
```

- Codex reads `AGENTS.md`. It has no import syntax, so the import belongs in `CLAUDE.md`, not the other way round.
- Claude expands `@AGENTS.md` inline and reads your Claude-only additions after it. The import never loads the file twice.
- Every shared rule exists exactly once. Copying the text into both files is how a payments rule ends up updated in one and stale in the other.

A symlink (`ln -s AGENTS.md CLAUDE.md`) also works, but Windows clones check it out as a one-line text file, and Claude's Edit tool refuses to write through a symlink. Prefer the import.

## Write rules any agent can follow

Plain, testable statements in tool-neutral words: "Run the tests with `python3 -m unittest -q`", "Money is integer cents", "Never push; open a pull request". Leave tool-specific advice (Claude's Edit tool, Codex's `$skill` mentions) in the tool's own file.

## Commands this node introduces

`@AGENTS.md` imports, `/memory`, `AGENTS.override.md`, and `project_doc_max_bytes`.
