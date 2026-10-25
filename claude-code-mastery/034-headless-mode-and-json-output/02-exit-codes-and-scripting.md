---
type: lesson
title: "Exit codes and scripting"
minutes: 14
---

A script around `claude -p` is only as good as its failure handling.

## What claude itself returns

| Situation | Exit code | JSON |
|---|---|---|
| Run finished | `0` | `subtype: success` |
| Hit `--max-turns` | `1` | `subtype: error_max_turns`, `is_error: true`, no `result` |
| Hit `--max-budget-usd` | `1` | `subtype: error_max_budget_usd` |
| Bad flags, bad schema, no auth | `1` | Often **no JSON at all** - an error on stderr |

So: never parse blindly. Capture the output even when claude fails, then check that it **is** JSON, then check `subtype`.

```bash
set -euo pipefail
out=$(mktemp)
claude -p "$prompt" --output-format json --max-turns 4 < /dev/null > "$out" || true     # keep going; decide below
subtype=$(jq -r '.subtype // "no-json"' "$out" 2>/dev/null || echo no-json)
if [ "$subtype" != success ]; then
  echo "agent run failed: $subtype" >&2
  exit 1
fi
```

## Give your script its own contract

CI needs to tell "the agent found problems" from "the agent broke". Pick codes and document them at the top of the script:

| Code | Meaning |
|---|---|
| `0` | Ran, nothing to report |
| `1` | The agent run failed - retry or alert |
| `2` | Bad usage (missing argument or file) |
| `3` | Ran and found issues - fail the build |

## Bound every run

`--max-turns N` and `--max-budget-usd X` stop runaway loops; `--allowedTools` keeps the run to what it needs; `--no-session-persistence` skips saving sessions you will never resume. Log one line per run (file, subtype, turns, cost, session id) - that log is how you debug a job that ran at 3 a.m.

## Close stdin, and know what the run inherits

When stdin is not a terminal, `claude -p` **reads it and appends it to your prompt** - that is what makes `cat log.txt | claude -p "explain"` work. Inside a script, stdin is whatever the script was given: a heredoc, a CI runner's pipe, the rest of a `while read` loop. The agent quietly receives text you never meant to send, and a `while read` loop loses its remaining lines. Give every scripted call `< /dev/null` unless you are deliberately piping data in.

The run also inherits the machine's configuration: `~/.claude/CLAUDE.md`, user hooks, the project's `.mcp.json`. On a laptop that means a personal rule such as "sign changelog summaries" leaks into a pipeline's output. For CI, `claude --bare -p ...` skips all auto-discovery (CLAUDE.md, hooks, skills, plugins, MCP servers, auto memory) and loads only what you pass: `--settings <file>`, `--mcp-config <file>`, `--append-system-prompt-file`. Bare mode needs `ANTHROPIC_API_KEY` (or an `apiKeyHelper` in `--settings`); it never reads a subscription login.

## Commands this node introduces

`--max-turns`, `--max-budget-usd`, `--no-session-persistence`, `|| true` plus a `subtype` check, `< /dev/null`, and `--bare`.
