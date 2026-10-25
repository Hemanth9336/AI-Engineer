---
type: lesson
title: "Manifest fields, user config, LSP, and monitors"
minutes: 10
---

`.claude-plugin/plugin.json` is optional, but a shared plugin should always have one.

```json
{
  "name": "team-kit",
  "version": "1.0.0",
  "description": "Review checklist and .env guard for the platform team",
  "author": {"name": "Platform Team", "email": "platform@example.com"},
  "license": "MIT",
  "userConfig": {
    "ticket_prefix": {"type": "string", "title": "Ticket prefix", "description": "Prefix for ticket IDs in review notes", "default": "ENG"}
  }
}
```

| Field | Notes |
|---|---|
| `name` | Letters, digits, `.`, `_`, `-`. It is the `team-kit` in `team-kit:review-checklist` |
| `version` | Semver. Updates compare it, so bump it on every release. If `plugin.json` and the marketplace entry both set it, `plugin.json` wins |
| `description`, `author`, `license`, `homepage`, `repository`, `keywords` | Shown in listings. `--strict` validation fails on missing license or metadata |
| `skills`, `commands`, `agents`, `hooks`, `mcpServers`, `lspServers`, `outputStyles` | Override default locations. Paths must start with `./` and stay inside the plugin. `commands` and `agents` **replace** the default folder, `skills` **adds** to it, and `hooks` and `mcpServers` **merge** |
| `dependencies` | Other plugins that must be enabled too |
| `defaultEnabled` | Whether it starts enabled (default `true`) |

Claude Code ignores unknown keys, so a typo such as `"descripton"` loads silently. `claude plugin validate --strict` makes it fail.

## userConfig: ask instead of making people edit settings

Each option has a `type` (`string`, `number`, `boolean`, `directory`, or `file`), a `title`, a `description`, and optionally `default`, `required`, `options` (a fixed picker), `multiple`, `min`/`max`, and `sensitive`.

- Values are set at install time (`--config ticket_prefix=OPS`) or later in `/plugin configure`. They are stored under `pluginConfigs` in user settings.
- **`sensitive: true`** masks input and stores the value in the OS credential store instead of `settings.json`. Use it for tokens.
- Reference a value as `${user_config.KEY}` in MCP and LSP config, exec-form hook `args`, and skill or agent text (non-sensitive values only). Hooks also get `CLAUDE_PLUGIN_OPTION_KEY` in their environment.
- **Shell-form hook commands, monitor commands, and `headersHelper` reject `${user_config.*}`**, because a shell would re-parse the value. Read the environment variable or use exec form instead.

## LSP servers: code intelligence

```json
{"lspServers": {"go": {"command": "gopls", "args": ["serve"], "extensionToLanguage": {".go": "go"}}}}
```

`command` and `extensionToLanguage` are required. After edits, diagnostics are pushed into context (`diagnostics: true` by default). The binary itself must be installed on the machine; the plugin only wires it up.

## Monitors: background watchers

```json
{"experimental": {"monitors": [{"name": "deploy-status", "command": "\"${CLAUDE_PLUGIN_ROOT}\"/scripts/poll-deploy.sh",
  "description": "Deployment status changes", "when": "on-skill-invoke:deploy"}]}}
```

A monitor is a persistent process whose output becomes notifications. It runs `always` (from session start) or only after a given skill first runs. Monitors don't receive user options.

## Commands this node introduces

`plugin.json` fields, `userConfig` (including `sensitive`), `${user_config.KEY}`, `CLAUDE_PLUGIN_OPTION_<KEY>`, `lspServers`, and `experimental.monitors`.
