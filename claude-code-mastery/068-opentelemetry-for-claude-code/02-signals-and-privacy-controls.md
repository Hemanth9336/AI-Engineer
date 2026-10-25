---
type: lesson
title: "Signals and privacy controls"
minutes: 12
---

## What arrives

| Kind | Name | Tells you |
|---|---|---|
| Metric | `claude_code.session.count` | Sessions started |
| Metric | `claude_code.cost.usage` | Cost in USD, by `model` |
| Metric | `claude_code.token.usage` | Tokens, by `type` (`input`, `output`, `cacheRead`, `cacheCreation`) and `model` |
| Metric | `claude_code.active_time.total` | Seconds of active use |
| Metric | `claude_code.lines_of_code.count`, `claude_code.commit.count`, `claude_code.pull_request.count` | Output of the work |
| Metric | `claude_code.code_edit_tool.decision` | Accept or reject decisions on edits |
| Event | `user_prompt` | A prompt was submitted: its length and a `prompt.id`; the text is **redacted** by default |
| Event | `api_request`, `api_error` | Each model call: model, cost, tokens, duration; errors with their status |
| Event | `tool_decision`, `tool_result` | Permission decisions, and each tool's name, success and duration |
| Span (beta) | `claude_code.interaction` | One user turn, end to end |
| Span (beta) | `claude_code.llm_request`, `claude_code.tool` (and `.execution`, `.blocked_on_user`) | Where the time inside a turn went |

Every signal carries `session.id`, a pseudonymous `user.id` and, depending on login, `organization.id` and `user.email`. Add your own dimensions with `OTEL_RESOURCE_ATTRIBUTES="team=payments,cost_center=4200"`.

## Privacy defaults, and the switches that change them

| Variable | Default | When set to `1` |
|---|---|---|
| `OTEL_LOG_USER_PROMPTS` | Prompt text is sent as `<REDACTED>`, with only its length | Full prompt text is exported |
| `OTEL_LOG_TOOL_DETAILS` | Tool events carry names and outcomes | Adds details such as Bash commands and file paths |
| `OTEL_LOG_TOOL_CONTENT` | No tool input or output | Tool input and output content |
| `OTEL_LOG_ASSISTANT_RESPONSES` | No response text | The model's response text |
| `OTEL_LOG_RAW_API_BODIES` | Off | Raw request and response bodies |

The defaults are deliberately safe: you can measure cost, usage and latency for a whole organization without collecting what people typed. Each switch you flip sends more source code, secrets pasted into prompts, and customer data to your telemetry backend, which probably has broader access and longer retention than your code does. Turn one on only for a reason you can write down, for a limited scope, with the backend's retention and access set to match.

## Commands this node introduces

`claude_code.session.count`, `claude_code.cost.usage`, `claude_code.token.usage`, `claude_code.active_time.total`, `user_prompt`, `api_request`, `tool_result`, `claude_code.interaction`, `claude_code.llm_request`, `OTEL_RESOURCE_ATTRIBUTES`, `OTEL_LOG_USER_PROMPTS`, `OTEL_LOG_TOOL_DETAILS`, `OTEL_LOG_TOOL_CONTENT`, and `OTEL_LOG_ASSISTANT_RESPONSES`.
