---
type: lesson
title: "Local plugin layout"
minutes: 10
---

Topic 016 installed and loaded a finished plugin. Here you build one from loose parts and run it through its whole life.

## The standard layout

Only the manifest lives inside `.claude-plugin/`. Every component sits at the plugin root:

```text
team-kit/
├── .claude-plugin/
│   └── plugin.json         # name, version, description, author, license, userConfig, ...
├── skills/
│   └── review-checklist/
│       └── SKILL.md        # loads as team-kit:review-checklist
├── agents/                 # subagent Markdown files
├── commands/               # older flat command files; prefer skills/
├── hooks/
│   └── hooks.json          # same schema as settings.json "hooks"
├── scripts/
│   └── block-env.sh        # called by the hook
├── bin/                    # on the Bash tool's PATH while the plugin is enabled
├── .mcp.json               # MCP servers the plugin starts
├── .lsp.json               # language servers (code intelligence)
├── monitors/monitors.json  # background watchers (experimental)
├── settings.json           # agent / subagentStatusLine defaults
└── evals/                  # claude plugin eval cases (results/ git-ignored)
```

A common mistake is putting `skills/` or `hooks/` inside `.claude-plugin/`. Nothing there loads except the manifest.

## Paths and variables

| Variable | Resolves to | Use for |
|---|---|---|
| `${CLAUDE_PLUGIN_ROOT}` | The installed copy of the plugin | Bundled scripts and config. It changes on every update, so never write state there |
| `${CLAUDE_PLUGIN_DATA}` | `~/.claude/plugins/data/<id>/`, kept across updates | Caches, installed dependencies, generated files |
| `${CLAUDE_PROJECT_DIR}` | The project root | Project-local files |

Hook commands receive all three as environment variables, plus `CLAUDE_PLUGIN_OPTION_<KEY>` for each user option. The Bash tool doesn't get them, so in skill content write `${CLAUDE_PLUGIN_ROOT}` literally and Claude Code substitutes the path when the skill loads. In a shell-form hook, **quote** the variable so a path with spaces stays one word:

```json
{"type": "command", "command": "\"${CLAUDE_PLUGIN_ROOT}\"/scripts/block-env.sh"}
```

`claude plugin validate` warns about an unquoted one.

## Commands this node introduces

The standard plugin layout, `${CLAUDE_PLUGIN_ROOT}`, `${CLAUDE_PLUGIN_DATA}`, and `${CLAUDE_PROJECT_DIR}`.
