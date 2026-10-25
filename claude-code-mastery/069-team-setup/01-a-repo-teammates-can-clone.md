---
type: lesson
title: "A repo teammates can clone"
minutes: 19
---

The best agent setup is useless if it lives only on your laptop. Everything a teammate needs to get the same behaviour belongs **in the repository**. Everything personal stays out of it.

## What goes where

| File | Committed? | Holds |
|---|---|---|
| `CLAUDE.md` | Yes | What the project is, how to build and test it, the rules everyone follows. It can import more files with `@docs/conventions.md` |
| `docs/*.md` (imported) | Yes | Longer conventions, kept next to the code they describe |
| `.claude/settings.json` | Yes | Team permissions (`allow`, `ask`, `deny`), `env`, hooks, and `enabledPlugins` |
| `.claude/commands/*.md`, `.claude/skills/*/SKILL.md` | Yes | Shared slash commands and skills: `/review`, `/release-check` |
| `.claude/agents/*.md` | Yes | Shared subagents, such as a `test-writer` with a restricted tool list |
| `.mcp.json` | Yes | Project MCP servers. Each teammate approves them once |
| `.claude/settings.local.json` | **No** (gitignore) | Your own allow rules, your local env, your experiments |
| `CLAUDE.local.md` | **No** (gitignore) | Your own preferences: "I prefer terse answers", "my test DB is on port 5433" |
| `~/.claude/settings.json`, `~/.claude/CLAUDE.md` | Not in the repo | Settings and instructions for all your projects |
| `.env` and other secrets | **Never** | And deny the agent from reading them (`Read(./.env)`) |

Claude Code adds `settings.local.json` to the repo's git exclude file when it creates one, but put both local files in `.gitignore` too. Then the rule is visible to every teammate, and survives a fresh clone.

## How the levels combine

```text
managed settings  >  command line flags  >  .claude/settings.local.json  >  .claude/settings.json  >  ~/.claude/settings.json
```

- **Scalars** such as `model` and `defaultMode`: the highest level that sets one wins.
- **Permission rules** are combined from every level and evaluated as deny first, then ask, then allow. A deny in the team's `settings.json` can't be undone by an allow in someone's `settings.local.json`.
- **CLAUDE.md files** are all loaded (user, project, local, and nested ones in subfolders), so personal preferences add to the team's instructions rather than replacing them.

## Check it the way a teammate would

The only real test is a fresh clone with no personal configuration:

```bash
git clone -q "$PWD" /tmp/fresh && cd /tmp/fresh
HOME=$(mktemp -d) claude -p "What prefix do our ticket references use?" --output-format stream-json --verbose < /dev/null \
  | jq -c 'select(.type == "system" and .subtype == "init") | {slash_commands, agents}'
```

The `init` event lists the commands, skills and agents the session found. If `review` or `test-writer` is missing there, a teammate won't have it either.

`/team-onboarding` (in recent versions) and `/init` help bootstrap a `CLAUDE.md`. Review what they produce like any other change.

## Commands this node introduces

`@path` imports in `CLAUDE.md`, `.claude/settings.json` vs `.claude/settings.local.json`, `CLAUDE.local.md`, settings precedence, deny-first permission evaluation, and a fresh-clone check with an empty `HOME`.
