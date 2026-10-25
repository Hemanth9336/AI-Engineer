---
type: lesson
title: "Permission callbacks and SDK hooks"
minutes: 12
---

The CLI asks a human before a risky tool call. An SDK program has no human, so it asks **your code**.

## `can_use_tool`

```python
from claude_agent_sdk import PermissionResultAllow, PermissionResultDeny

async def gate(tool_name, tool_input, context):
    if tool_name == "Bash" and "rm " in tool_input.get("command", ""):
        return PermissionResultDeny(message="destructive commands are not allowed")
    return PermissionResultAllow(updated_input=tool_input)     # you may also rewrite the input

opts = ClaudeAgentOptions(can_use_tool=gate)
```

- A deny reaches the model as a tool result with `is_error: true` and your `message`. The model reads it and adapts, so make the message say what *is* allowed.
- `PermissionResultDeny(interrupt=True)` stops the whole run instead.
- `updated_input` lets you rewrite a call before it runs: clamp a limit, force a path inside a folder, add `--dry-run`.

## The order rules are checked in

```text
PreToolUse hooks → deny rules → allow rules / permission mode → can_use_tool → the tool runs
```

**Anything an allow rule already approves never reaches `can_use_tool`.** For example, `allowed_tools=["mcp__jobs__cancel_job"]` auto-approves every cancel. The callback you wrote to check who owns the job is silently skipped. Recent SDKs warn about it: `CanUseToolShadowedWarning: can_use_tool will not be invoked for: ...`.

- Put a tool in `allowed_tools` only when *every* call to it is fine.
- Leave a tool out when the callback must decide each call.
- Settings files can add allow rules too, which is one more reason the SDK doesn't load them by default.

## Hooks in code

The hook events from topics 019-022 are available as Python callbacks:

```python
from claude_agent_sdk import HookMatcher

async def audit(input_data, tool_use_id, context):
    log.write(json.dumps({"tool": input_data["tool_name"], "session": input_data["session_id"]}) + "\n")
    return {}                                           # {} = no opinion; continue

opts = ClaudeAgentOptions(hooks={"PreToolUse": [HookMatcher(matcher=None, hooks=[audit])],
                                 "PostToolUse": [HookMatcher(matcher="Bash", hooks=[record_exit])]})
```

A PreToolUse hook runs for **every** call, including ones an allow rule approves. That makes it the right place for an audit log, or for a hard block. To block, return `{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": "..."}}`.

Use `can_use_tool` for decisions about calls that need approval, and hooks for things that must see everything.

## Commands this node introduces

`can_use_tool`, `PermissionResultAllow(updated_input=...)`, `PermissionResultDeny(message=..., interrupt=...)`, `CanUseToolShadowedWarning`, `hooks={...}`, and `HookMatcher`.
