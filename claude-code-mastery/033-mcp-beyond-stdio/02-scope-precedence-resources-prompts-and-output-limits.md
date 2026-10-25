---
type: lesson
title: "Scope precedence, resources, prompts, and output limits"
minutes: 12
---

## When the same name is defined twice

Claude Code connects to a server **once**, using the definition from the highest-precedence source. The whole entry wins - fields are not merged.

1. **Local** (`~/.claude.json`, this project)
2. **Project** (`.mcp.json`)
3. **User** (`~/.claude.json`, top level)
4. Plugin-provided servers, then claude.ai connectors

`claude mcp get <name>` tells you which one is in force ("Scope: Local config"). This is how a developer points the team's `status` server at a staging URL without touching `.mcp.json` - and also how a stale local entry silently overrides the team's fix.

## Resources

Servers can publish **resources** - read-only documents with a URI such as `status://summary`. In the console, `@status:status://summary` attaches one to your prompt. Claude can also fetch them itself with the built-in `ListMcpResourcesTool` and `ReadMcpResourceTool`, which is how resources are used in headless runs.

## Prompts

Servers can publish **prompts** - templates that become slash commands: `/mcp__status__incident_brief checkout`. They work in `-p` too, and their text is injected into the conversation.

## Output limits

| Limit | Default | Change it |
|---|---|---|
| Warning | 10,000 tokens per tool result | Fixed |
| Maximum | 25,000 tokens | `MAX_MCP_OUTPUT_TOKENS=50000` |
| Text saved to a file | over 50,000 characters | The server sets `_meta["anthropic/maxResultSizeChars"]` |

An oversized result is **saved to a file** under the session's `tool-results/` folder and replaced by a short note with the path - Claude then reads it in pieces. If a tool reply looks cut off, it usually was not: look for that note, then make the tool return less (paging, filters) rather than raising limits.

## Tool search

With many servers, Claude Code loads only tool **names** at startup and fetches full definitions on demand. `/context` shows which tools are deferred; `"alwaysLoad": true` on a server keeps its few, always-needed tools loaded; `ENABLE_TOOL_SEARCH=false` turns deferral off.

## Commands this node introduces

`claude mcp get`, `ReadMcpResourceTool`, `/mcp__<server>__<prompt>`, `MAX_MCP_OUTPUT_TOKENS`, `alwaysLoad`, and `ENABLE_TOOL_SEARCH`.
