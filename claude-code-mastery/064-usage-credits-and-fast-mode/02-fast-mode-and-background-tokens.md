---
type: lesson
title: "Fast mode and background tokens"
minutes: 19
---

## Fast mode

Fast mode runs supported models with **faster output generation at a higher price per token**. It's the same model with the same quality, just quicker and more expensive. Toggle it in a session with `/fast`. When it's on, the prompt shows a marker, and the tokens are billed at the fast-mode rate.

| Use fast mode when | Leave it off when |
|---|---|
| You're waiting interactively on long outputs: a big refactor plan, a live debugging session, a demo | Work runs unattended (CI, cron, background helpers); nobody is waiting |
| Latency is the bottleneck, not thinking | The run is slow because it loops through many tool calls; fast output doesn't shorten test runs or tool time |
| The task is short enough that the price difference is small | You're on a tight usage window; faster tokens use it up faster |

Fast mode makes *generation* faster. If a session is slow because `npm test` takes four minutes per turn, fast mode changes nothing. Measure first: `duration_api_ms` against `duration_ms` in the envelope tells you how much of the time was the model.

## Background tokens

Not every token in a session comes from your prompt:

- **Background model calls:** Claude Code uses a small model for side tasks, such as summarising, titling a session, or classifying a command. They show up as a separate model in `modelUsage`.
- **Subagents and background tasks:** each subagent has its own context and its own tokens. Ten parallel workers bill ten contexts.
- **Compaction:** summarising a long conversation is itself a model call.
- **Hooks that call `claude -p`:** a hook that runs a model on every tool call multiplies your usage silently.

When a session costs more than its visible conversation explains, read `modelUsage` per model, count the subagent transcripts under the session's `subagents/` folder, and check your hooks.

## Commands this node introduces

`/fast`, `duration_api_ms` against `duration_ms`, `modelUsage` per model, and subagent token accounting.
