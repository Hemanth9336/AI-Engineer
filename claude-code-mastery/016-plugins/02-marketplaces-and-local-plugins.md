---
type: lesson
title: "Marketplaces and local plugins"
minutes: 14
---

A **marketplace** is a catalog: a `.claude-plugin/marketplace.json` listing plugins and where to fetch each one. It can be a GitHub repo, any git URL, or a local folder.

```json
{
  "name": "acme-tools",
  "owner": { "name": "Acme platform team" },
  "description": "Internal Claude Code plugins",
  "plugins": [
    { "name": "team-tools", "source": "./plugins/team-tools", "description": "Release helpers" }
  ]
}
```

Relative `source` paths resolve from the **marketplace root** (the folder containing `.claude-plugin/`), not from `.claude-plugin/` itself. Names such as `claude-plugins-official`, or anything impersonating them, are reserved.

## Installing

```bash
claude plugin marketplace add ./acme-market          # or owner/repo, or a git URL
claude plugin install team-tools@acme-tools --scope project
```

| Scope | Effect |
|---|---|
| `user` (default) | You, in every project |
| `project` | Recorded in `.claude/settings.json` - teammates are prompted to install it |
| `local` | You, this project only |

In the console, `/plugin` opens the same flow with a review panel before anything is installed.

## Trust before you install

A plugin can contain **hooks and MCP servers - code that runs on your machine** with your permissions, outside the sandbox. Treat installing one like adding a dependency:

- Know the publisher; prefer your organization's marketplace or the official one.
- Read `hooks/hooks.json` and `.mcp.json` before enabling.
- Pin versions for anything shared, and review updates.
- Admins can restrict marketplaces with managed settings (`strictKnownMarketplaces`).

## Commands this node introduces

`claude plugin marketplace add <source>`, `claude plugin install <plugin>@<marketplace>`, and `/plugin`.
