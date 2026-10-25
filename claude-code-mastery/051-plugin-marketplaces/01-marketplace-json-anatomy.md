---
type: lesson
title: "marketplace.json anatomy"
minutes: 14
---

A **marketplace** is a catalog: a `.claude-plugin/marketplace.json` that lists plugins and says where to fetch each one. The folder that contains `.claude-plugin/` is the **marketplace root**, and relative plugin paths resolve from there, not from `.claude-plugin/`.

```json
{
  "name": "acme-tools",
  "owner": {"name": "Acme Platform Team", "email": "platform@acme.example"},
  "description": "Plugins reviewed by the platform team",
  "plugins": [
    {"name": "team-kit", "source": "./plugins/team-kit", "description": "Review checklist and .env guard"},
    {"name": "lint-kit", "description": "Lint helpers",
     "source": {"source": "github", "repo": "acme/lint-kit", "ref": "v1.0.0", "sha": "a1b2...40 hex"}}
  ]
}
```

| Top-level field | Notes |
|---|---|
| `name` | Required. Users type it after `@`: `team-kit@acme-tools`. Letters, digits, `.`, `_`, `-` |
| `owner` | Required, with `name` (and optional `email`, `url`) |
| `plugins` | Required. Each entry is validated separately, so one bad entry doesn't sink the catalog |
| `description` | Strongly recommended; validate warns without it |
| `metadata.pluginRoot` | Lets entries use bare names: `"source": "team-kit"` resolves to `<pluginRoot>/team-kit` |
| `forceRemoveDeletedPlugins`, `renames` | Maintenance: uninstall plugins you dropped, or redirect a renamed plugin |
| `allowCrossMarketplaceDependenciesOn` | Marketplaces whose plugins may be pulled in as dependencies |

An entry needs `name` and `source`, and may also carry any `plugin.json` field (`description`, `version`, `author`, `category`, `tags`, `dependencies`, `defaultEnabled`, ...). When the fetched plugin has its own `plugin.json`, that file is the manifest. With the default `strict: true`, extra component fields on the entry are appended to it. With `strict: false`, an entry that declares components conflicts with the manifest and the plugin fails to load.

## Names Claude Code refuses

Official names such as `claude-plugins-official`, impersonations such as `official-claude-plugins`, other spellings of those names, non-ASCII names, and internal names (`inline`, `skills-dir`, `builtin`, `synced`, `npm`, `github`, ...) are all rejected. The rule exists so no one can publish a catalog that looks like Anthropic's.

## How users get it

```bash
claude plugin marketplace add ./acme-market                  # a local folder: "directory" source
claude plugin marketplace add acme/claude-plugins           # GitHub owner/repo
claude plugin marketplace add https://git.acme.example/tools.git
claude plugin marketplace list / update acme-tools / remove acme-tools
```

With `--scope project`, the catalog is declared in `.claude/settings.json` as `extraKnownMarketplaces`, so every clone of the repo knows about it.

## Commands this node introduces

`marketplace.json` top-level and entry fields, `strict`, reserved names, `claude plugin marketplace add / list / update / remove`, and `extraKnownMarketplaces`.
