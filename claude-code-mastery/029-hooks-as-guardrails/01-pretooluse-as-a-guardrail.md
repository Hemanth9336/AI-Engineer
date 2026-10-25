---
type: lesson
title: "PreToolUse as a guardrail"
minutes: 19
---

A guardrail is a hook whose job is to stop one class of harm **no matter what the prompt, the model, or the allow list says**. The classic one: secrets leaving the machine.

## Why a hook, not a rule

Your team allows `Bash(curl *)` because health checks and API calls are daily work. A deny rule cannot say "curl is fine, curl **with** `.env` is not" - a hook can, because it sees the whole command.

## Return a decision, not just an exit code

Exit 2 blocks. JSON gives you more control and a clean message:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "blocked: possible secret exfiltration (curl with .env)"
  }
}
```

| `permissionDecision` | Effect |
|---|---|
| `deny` | Call blocked; Claude sees the reason |
| `ask` | Forces a prompt (in `-p`, nobody can answer, so it is refused) |
| `allow` | Skips the prompt - but deny and ask **rules** still apply |
| `defer` | `-p` only: end the turn so the call can be resumed later |

With several hooks, the strictest wins: `deny` > `defer` > `ask` > `allow`. `updatedInput` can rewrite the call instead of refusing it (for example, adding `--dry-run`).

## Fail closed

A guardrail that crashes must not let the command through:

```json
{ "type": "command", "command": "python3 \"$CLAUDE_PROJECT_DIR/.claude/hooks/no_exfil.py\"", "timeout": 10, "onFailure": "block" }
```

`onFailure: "block"` turns a crash, a timeout, or a missing script into a block. Inside the script, unreadable input should also exit 2.

## What to detect

A network tool (`curl`, `wget`, `nc`, `scp`, `rsync`, `/dev/tcp/`) **together with** a secret source (`.env`, SSH keys, `.pem`, `~/.aws/credentials`, `secrets/`, `printenv`, `$..._TOKEN`). Requiring both keeps false positives low. Pattern matching is a speed bump, not a proof - pair it with sandboxing and network rules for real isolation.

## Commands this node introduces

`permissionDecision` / `permissionDecisionReason` JSON output and `onFailure: "block"` for fail-closed guards.
