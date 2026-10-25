---
type: lesson
title: "Agent definition files"
minutes: 14
---

`--agents` is for one session. For a specialist the team should reuse, write a **definition file**: markdown with frontmatter, in an `agents/` folder.

| Location | Scope |
|---|---|
| `.claude/agents/<name>.md` | This project - commit it |
| `~/.claude/agents/<name>.md` | All your projects |
| `<plugin>/agents/<name>.md` | Wherever the plugin is enabled |
| `--agents` JSON | This session only |

When names collide, the more specific scope wins (project over user).

```markdown
---
name: security-reviewer
description: Reviews code for security issues. Use proactively after changes to authentication, payments, or SQL.
tools: Read, Grep, Glob
model: sonnet
---

You are a security reviewer. You never modify files.

Check for: hard-coded secrets, SQL built by string concatenation, weak password hashing,
missing authorization checks. Report each issue as:
FINDING: <file>:<line> - <issue>
If there are none, reply exactly: NO FINDINGS
```

## Frontmatter

| Field | Required | Notes |
|---|---|---|
| `name` | Yes | Lowercase with hyphens; what `subagent_type` and `--agent` use |
| `description` | Yes | When Claude should delegate - the trigger |
| `tools` | No | Allowlist; omit to inherit everything. `disallowedTools` removes specific ones |
| `model` | No | `haiku`, `sonnet`, `opus`, `inherit`, or a full id |
| `permissionMode`, `effort`, `skills`, `memory`, `isolation: worktree`, `hooks` | No | Advanced: mode, preloaded skills, own memory, own worktree, scoped hooks |

The body is the agent's **system prompt**. It does not see your conversation, so it must be complete on its own: role, checklist, output format.

## Tool restrictions are real

`tools: Read, Grep, Glob` is enforced by Claude Code, not requested of the model. A reviewer with that list **cannot** edit a file, whatever its prompt says. That is the reason to define read-only specialists instead of writing "please don't edit" in a prompt.

## Commands this node introduces

`/agents` in the console creates, edits, and lists agent files; `claude --agent <name>` runs one as the main agent.
