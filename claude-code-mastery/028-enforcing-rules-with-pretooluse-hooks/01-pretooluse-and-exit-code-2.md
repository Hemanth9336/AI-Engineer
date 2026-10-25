---
type: lesson
title: "PreToolUse and exit code 2"
minutes: 14
---

`PreToolUse` runs **before** a tool call, with the same JSON a PostToolUse hook sees minus the result. It is where you turn a rule like "never touch the production config" from a sentence in CLAUDE.md into something that **cannot** happen.

## Three ways to answer

| Your hook | Effect |
|---|---|
| exit `0`, no output | No opinion - the normal permission flow decides |
| exit `2`, reason on **stderr** | The call is **blocked**; Claude gets the reason as the tool's error |
| exit `0`, JSON `permissionDecision` | `deny`, `ask`, `allow`, or `defer`, with a reason (next topic) |

What Claude receives for an exit-2 block looks like:

```text
PreToolUse:Edit hook error: [python3 .../protect.py]: protected: config/prod.yaml matches 'config/prod.yaml' in .claude/protected.txt
```

Claude reads that and adapts - it does not retry the same edit blindly, it does what the message tells it.

## The exit-code trap

Exit `1` - the normal Unix "failure" - is a **non-blocking** error. The tool call **goes ahead**. So does a hook whose script path is wrong, or that crashes on bad input. A guard written with `sys.exit(1)` protects nothing.

Use exit `2` to block, and for hooks that must fail closed add `"onFailure": "block"` to the handler: then a crash, timeout, or missing script blocks the call too.

## Hooks and permission rules together

A hook can block what a rule allows - deny always wins. A hook's `allow` cannot override a `deny` or `ask` rule from settings. So: rules for the simple yes/no lists, hooks for logic rules cannot express ("this file pattern list", "only on Fridays", "only if tests pass").

## Commands this node introduces

`PreToolUse` with exit code 2, and `onFailure: "block"`.
