---
type: lesson
title: "Auditing and narrowing MCP access"
minutes: 14
---

Before an MCP server touches production data, answer four questions - and keep the answers in the repository.

## 1. What can it do?

`claude mcp get records` shows how it starts; `/mcp` lists its tools. Write the tool list down and mark each one **needed** or **not**.

## 2. What may Claude call?

```json
"permissions": {
  "allow": ["mcp__records__list_directory", "mcp__records__read_text_file", "mcp__records__read_multiple_files"],
  "deny":  ["mcp__records__write_file", "mcp__records__edit_file", "mcp__records__move_file", "mcp__records__create_directory"]
}
```

Allow what is needed, deny the dangerous rest explicitly. A deny rule on an MCP tool removes it from Claude's tool list altogether - a call to it fails with `No such tool available`.

## 3. Where may it reach?

A PreToolUse hook with matcher `mcp__records__.*` that collects every path-like argument (`path`, `paths`, `source`, `destination`), resolves it with `realpath`, and denies anything not under `records/`:

```python
allowed = os.path.join(proj, "records")
bad = [p for p in paths if os.path.commonpath([allowed, os.path.realpath(os.path.join(proj, p))]) != allowed]
```

`commonpath` on resolved paths catches `records/../config` and symlinks that point outside. Set `onFailure: "block"`.

## 4. What did it do?

Every MCP call is in the session transcript (`mcp__records__...` tool uses and their results). Add a PostToolUse audit hook (topic 027) on the same matcher if you need a separate log.

## Scope choice

A server holding production credentials belongs in **local** or **user** scope on the machines that need it - not in a committed `.mcp.json` that every clone, fork, and CI job picks up.

## Commands this node introduces

`claude mcp get`, deny rules on MCP tools, and an MCP path-guard hook.
