---
type: lesson
title: "query, ClaudeAgentOptions, and the message stream"
minutes: 14
---

## The smallest program

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage

async def main():
    opts = ClaudeAgentOptions(allowed_tools=["Read", "Glob", "Grep"], max_turns=8, cwd=".")
    async for message in query(prompt="Which file mentions the outage?", options=opts):
        if isinstance(message, ResultMessage):
            print(message.result, message.total_cost_usd)

asyncio.run(main())
```

`query()` is an **async iterator**. It starts the agent, sends your prompt and yields every message as the loop runs. It finishes after the result.

## The options you'll set most

| Option | CLI equivalent | Purpose |
|---|---|---|
| `allowed_tools`, `disallowed_tools` | `--allowedTools`, `--disallowedTools` | Permission rules: pre-approve, or block, tools and patterns such as `Bash(git diff *)` |
| `tools` | `--tools` | Which built-in tools exist at all |
| `permission_mode` | `--permission-mode` | `default`, `acceptEdits`, `plan`, `bypassPermissions` |
| `max_turns`, `max_budget_usd` | `--max-turns`, `--max-budget-usd` | Hard stops on loop length and spend |
| `model`, `fallback_model` | `--model`, `--fallback-model` | Which model runs the loop |
| `cwd`, `add_dirs` | the working directory, `--add-dir` | Where the agent works |
| `system_prompt`, `setting_sources` | (the defaults differ, see the previous lesson) | Instructions and which settings files load |
| `output_format` | `--json-schema` | A JSON schema for a validated `structured_output` |
| `mcp_servers`, `agents`, `hooks`, `can_use_tool` | `.mcp.json`, `--agents`, settings hooks, (none) | Topic 060 |

## The message stream

| Message | When | What to read |
|---|---|---|
| `SystemMessage` (subtype `init`) | First | `data["session_id"]`, `data["tools"]`, `data["mcp_servers"]`, `data["model"]`, `data["permissionMode"]` |
| `AssistantMessage` | Each model turn | `content`: a list of `TextBlock` (`.text`), `ToolUseBlock` (`.name`, `.input`, `.id`), and `ThinkingBlock` |
| `UserMessage` | After each tool runs | `content` holds `ToolResultBlock` (`.tool_use_id`, `.content`, `.is_error`) |
| `ResultMessage` | Last | `subtype`, `is_error`, `result`, `num_turns`, `duration_ms`, `total_cost_usd`, `usage`, `session_id`, `structured_output` |

These are the same events as `claude -p --output-format stream-json` (topic 039), decoded into Python objects.

## How a run ends

`ResultMessage.subtype` is `success`, `error_max_turns`, `error_max_budget_usd`, `error_during_execution` or `error_max_structured_output_retries`.

On an error ending, the SDK **yields the `ResultMessage` first and then raises `ResultError`**, for example `Claude Code returned an error result: Reached maximum number of turns (1)`. A loop that saves the result only after `async for` finishes never gets there. Record the result as it arrives, and catch the exception:

```python
from claude_agent_sdk import ClaudeSDKError, ResultError

final = None
try:
    async for m in query(prompt=p, options=opts):
        if isinstance(m, ResultMessage):
            final = m                       # keep it - the exception may come next
except ResultError:
    pass                                    # final already holds subtype and errors
except ClaudeSDKError as e:                 # CLINotFoundError, ProcessError, CLIConnectionError, ...
    print("agent failed to run:", e)
```

`ClaudeSDKError` is the base class. Below it, `CLINotFoundError` means the binary is missing, `ProcessError` means the CLI crashed (it carries `exit_code`), and `CLIJSONDecodeError` means unreadable output.

## Where the numbers live

- `total_cost_usd` is the run's estimated cost.
- `usage` holds `input_tokens`, `output_tokens`, `cache_read_input_tokens` and `cache_creation_input_tokens`.
- `num_turns` counts model turns, and `duration_ms` is the wall time.

Write them to a file on every run, failed runs included. Topics 063 and 066 build dashboards on exactly these fields.

## Commands this node introduces

`query`, `ClaudeAgentOptions`, `SystemMessage`, `AssistantMessage`, `UserMessage`, `ResultMessage`, `TextBlock`, `ToolUseBlock`, `ToolResultBlock`, `ResultError`, `ClaudeSDKError`, `CLINotFoundError`, and `ProcessError`.
