---
type: lesson
title: "Matchers and inspecting the payload"
minutes: 14
---

Before you write the logic, look at what the hook will really receive.

## Capture real payloads

A throwaway hook that dumps its input is the fastest way to learn a tool's shape:

```json
{ "matcher": "*", "hooks": [ { "type": "command", "command": "cat >> /tmp/hook-payloads.jsonl" } ] }
```

Run one task, then `jq -c '{tool_name, tool_input}' /tmp/hook-payloads.jsonl`. You will see that:

- `Write` and `Edit` carry `tool_input.file_path` (absolute).
- `Bash` carries `tool_input.command` - one string, possibly with `&&`, pipes, and subshells.
- MCP tools are named `mcp__<server>__<tool>` and carry whatever arguments that server defines (`path`, `paths`, ...).

## Choose the narrowest matcher

| Goal | Matcher | Then in the script |
|---|---|---|
| Protect files | `Edit|Write` | Check `file_path` |
| Police shell commands | `Bash` | Parse `command` |
| Police one MCP server | `mcp__records__.*` | Check its path arguments |

A matcher keeps the hook from running at all for other tools, which is faster and leaves fewer surprises. The `if` field narrows further with a permission rule, but it is best-effort for complex Bash - keep the real decision in the script.

## Normalize before you compare

`config/../config/prod.yaml`, `./config/prod.yaml`, and a symlink to it are all the same file. Resolve with `realpath`, make the path relative to `$CLAUDE_PROJECT_DIR`, and only then compare with your patterns.

## Test without Claude

A hook is a program with JSON input - test it directly:

```bash
echo '{"tool_name":"Write","tool_input":{"file_path":"'"$PWD"'/config/prod.yaml"},"cwd":"'"$PWD"'"}' \
  | CLAUDE_PROJECT_DIR=$PWD python3 .claude/hooks/protect.py; echo "exit $?"
```

## Commands this node introduces

A payload-dump hook and piping hand-written events into a hook to test it.
