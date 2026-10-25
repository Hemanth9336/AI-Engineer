---
type: lesson
title: "Activity hooks and changelogs from git"
minutes: 23
---

## An activity log with PostToolUse

When agents run unattended, you need a record of what they *did*, not just what they said. A **PostToolUse** hook (topic 030) runs after every tool call and gets the call as JSON on stdin:

```json
{"session_id": "...", "cwd": "/repo", "tool_name": "Bash", "tool_input": {"command": "python3 release/check.py"}, "tool_response": {...}}
```

```json
// .claude/settings.json
{"hooks": {"PostToolUse": [{"matcher": "*", "hooks": [{"type": "command",
  "command": "python3 \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/activity.py"}]}]}}
```

| Rule | Why |
|---|---|
| **Append one JSON line per call** (`ts`, `session`, `tool`, `target`) | `jq` and `grep` can answer "what touched pricing.py?" |
| **Never block, never crash.** Bad input means exit 0 | An observability hook must not change behaviour |
| **Truncate targets** (for example, 200 characters) | Commands can be huge, and logs aren't data stores |
| **Use `$CLAUDE_PROJECT_DIR`** | Hooks run from wherever the session is; anchor paths to the project |
| **Log targets, not contents** | File contents and tool responses can contain secrets |

## A changelog from git history

Conventional commits (`type(scope)!: description`) make the changelog a parsing job, not a writing job:

| Commit subject | Section |
|---|---|
| `feat!: ...`, or a body with `BREAKING CHANGE:` | Breaking changes |
| `feat: ...` / `feat(api): ...` | Features (with a scope: `**api:** ...`) |
| `fix: ...` | Fixes |
| `docs:`, `perf:`, `refactor:`, or a non-conventional subject | Other |
| `chore:`, `ci:`, `build:`, `style:`, `test:` | Left out |

```bash
git describe --tags --abbrev=0                       # the latest tag, e.g. v1.0.0
git log v1.0.0..HEAD --format='%s%x1f%b%x1e'         # subject, body, with record separators
```

Use separators (`%x1f` between fields, `%x1e` between records) because commit bodies contain newlines. List the entries oldest first within each section. Without any tag, fall back to the whole history.

## Commands this node introduces

The PostToolUse activity log, `$CLAUDE_PROJECT_DIR`, conventional-commit grouping, `git describe --tags --abbrev=0`, and `git log A..B --format` with separators.
