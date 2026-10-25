---
type: lesson
title: "Extension seams compared"
minutes: 10
---

Every way you have extended Claude Code in this course has a Codex counterpart. The ideas map one to one; the file formats and the enforcement model do not.

| Seam | Claude Code | Codex CLI |
|---|---|---|
| Config file | `.claude/settings.json` (JSON, layered: managed, CLI, local, project, user) | `~/.codex/config.toml`, project `.codex/config.toml` (TOML), profiles with `-p` |
| Guardrails | `permissions.allow / ask / deny` rules per tool | `sandbox_mode` + `approval_policy`, plus `.rules` files with `prefix_rule` |
| Hooks | `hooks` in settings | `hooks.json` or `[hooks]` in `config.toml` - similar events, `PreToolUse` through `Stop` |
| Skills | `.claude/skills/<name>/SKILL.md` | `.agents/skills/<name>/SKILL.md` (from your directory up to the repo root), `~/.agents/skills` |
| Subagents | `.claude/agents/<name>.md` with tools and model in the frontmatter | `.codex/agents/<name>.toml` with `name`, `description`, `developer_instructions` |
| MCP servers | `claude mcp add`, stored in `.mcp.json` / `~/.claude.json` | `codex mcp add`, stored as `[mcp_servers.<name>]` in `config.toml` |
| Plugins | `/plugin`, marketplaces | `codex plugin add`, `codex plugin marketplace` |
| Trusting a folder | Trust dialog; project allow rules wait for it | Project `.codex/` layer (config, hooks, rules) loads only once the project is trusted |

## Two enforcement models

**Claude Code** checks each tool call against your rules: `Bash(git push *)` in `deny` stops the call before it runs, and `Edit(...)` rules govern which files change. You can add OS sandboxing for Bash on top.

**Codex** leans on the operating-system sandbox first. In `workspace-write` mode commands can write inside the workspace only, **network is off**, and `.git`, `.codex`, and `.agents` stay read-only even inside it. `approval_policy` decides when Codex asks before stepping outside the sandbox (`on-request`), or never asks (`never`, for CI). `.rules` files then decide individual command prefixes:

```python
# .codex/rules/default.rules - Starlark, Python-like
prefix_rule(
    pattern = ["git", "push"],
    decision = "forbidden",            # allow | prompt | forbidden; the strictest match wins
    justification = "Never push; open a pull request instead.",
    match = ["git push origin main"],  # examples checked when the rules load
    not_match = ["git status"],
)
```

`codex execpolicy check --pretty --rules .codex/rules/default.rules -- git push origin main` prints the decision without running anything.

## Mapping one guardrail

"The agent must never push" becomes `"deny": ["Bash(git push *)"]` in `.claude/settings.json`, and a `forbidden` `prefix_rule` plus a `workspace-write` sandbox (no network) in Codex. Write both, test both, and commit them together, the same way you share `AGENTS.md`.

## Differences that bite

- Codex custom agents **inherit the parent's sandbox, approvals, and MCP servers**; a custom agent file cannot loosen them. A Claude subagent can be given a narrower `tools` list.
- Codex asks you to review and **trust each hook by its hash** (`/hooks`) before it runs; changing the script means trusting it again. Claude Code runs project hooks from settings once the folder's settings load.
- Both documents say the same thing about hooks: a useful guardrail, not a complete security boundary.

## Commands this node introduces

`.codex/config.toml`, `sandbox_mode`, `approval_policy`, `prefix_rule`, `codex execpolicy check`, and `codex mcp add`.
