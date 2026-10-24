---
type: lesson
title: "claude mcp add and claude mcp list"
minutes: 8
---

Claude Code manages MCP servers with the `claude mcp` commands.

## Adding a server

```bash
# remote server over HTTP
claude mcp add --transport http <name> <url>

# with an auth header
claude mcp add --transport http github https://api.githubcopilot.com/mcp/ \
  --header 'Authorization: Bearer ${GITHUB_PAT}'

# local server started as a process (everything after -- is the command)
claude mcp add files -- npx -y @modelcontextprotocol/server-filesystem /srv/docs
```

Options go **before** the server name.

## Scopes: who gets the server

| Scope | Stored in | Who sees it |
|---|---|---|
| `local` (default) | Your user config, for this project only | Just you, in this directory |
| `project` | `.mcp.json` in the project root | Everyone who clones the repo |
| `user` | Your user config | You, in every project |

**Project scope** is how teams share a standard set of servers: commit `.mcp.json`, and everyone gets them. Because it is committed, it must **never** contain a real token.

## Environment variables in .mcp.json

Claude Code expands `${VAR}` in `.mcp.json` when it starts the server, so each person supplies their own secret:

```json
{
  "mcpServers": {
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp/",
      "headers": {"Authorization": "Bearer ${GITHUB_PAT}"}
    }
  }
}
```

Note the **single quotes** in the `claude mcp add` command above: they stop your shell from expanding `${GITHUB_PAT}` itself, so the literal placeholder is saved - not your token.

## Inspecting servers

```bash
claude mcp list            # every server and whether it connects
claude mcp get github      # details of one server
claude mcp remove github   # delete it (add -s project for project scope)
```

Inside an interactive session, `/mcp` shows server status and lets you authenticate OAuth servers.

## Project servers need approval

The first time you run `claude` in a project with a new `.mcp.json`, it asks whether to trust those servers. Until then they show as **pending approval** - a protection against a cloned repo silently connecting you to something.
