---
type: lesson
title: "Scoping an MCP server to the job"
minutes: 14
---

The fastest way to wire an agent to data is a general server - a filesystem server, a SQL server - pointed at a directory or database. The fastest way to regret it is to stop there.

## The arguments are not the boundary

The filesystem server takes directories as arguments: `mcp-server-filesystem ./records`. But MCP clients can also send **roots**, and Claude Code does: it answers with the session's launch directory plus every `--add-dir`. The filesystem server then serves **those** directories instead of its arguments.

So started from the project folder, a server "scoped" to `./records` can read `config/db.env` next to it. Check what a server really allows - the filesystem server has a `list_allowed_directories` tool for exactly this.

## Layers that actually hold

| Layer | How | Stops |
|---|---|---|
| Tool choice | Allow only read tools: `mcp__records__read_text_file`, `..._list_directory`, `..._read_multiple_files` | Writes, moves, deletes |
| Deny rules | Deny `mcp__records__write_file`, `..._edit_file`, `..._move_file`, `..._create_directory` | Write tools, even if someone adds an allow later |
| Path guard | PreToolUse hook on `mcp__records__.*` that resolves every path argument and denies anything outside `records/` | Reads of neighbors, `../` tricks, symlinks |
| Server choice | A purpose-built server ("get_orders(month)") instead of raw files or SQL | Everything the job does not need |

The path guard is the one people skip, and the one that matters when the data folder sits next to credentials.

## Read-only by default

Agents that **report** on data should not be able to **change** it. Make the write tools impossible (deny), not just unmentioned. If a job really needs to write, give it a separate, narrower server.

## Commands this node introduces

MCP roots and `mcp__<server>__list_allowed_directories` for checking a server's real reach.
