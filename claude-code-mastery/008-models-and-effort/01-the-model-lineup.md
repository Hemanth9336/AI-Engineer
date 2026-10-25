---
type: lesson
title: "The model lineup"
minutes: 14
---

Claude Code talks to one model at a time, picked by **alias** or full name. Aliases track the recommended version for your provider, so `sonnet` keeps meaning "the current Sonnet".

| Alias | Character | Good for |
|---|---|---|
| `haiku` | Fastest and cheapest | Summaries, classification, small edits, high-volume scripted runs |
| `sonnet` | Balanced | Everyday coding, most agent tasks |
| `opus` | Deepest reasoning | Hard debugging, architecture, long multi-step plans |
| `opusplan` | Opus while planning, Sonnet while executing | Plan-mode work where the plan deserves the bigger model |
| `default` | Clears your override and returns to the account's default | |

Some providers resolve the aliases to earlier versions; to pin an exact version, use the full model name or set `ANTHROPIC_DEFAULT_SONNET_MODEL` (and its `HAIKU`/`OPUS` siblings). That is exactly how this lab's gateway maps the three aliases to its own model names.

## Choosing and switching

```bash
claude --model haiku                 # this session
claude -p "..." --model sonnet       # this run
```

In the console, `/model` shows and switches the model. A model can also come from the `ANTHROPIC_MODEL` environment variable or the `model` key in settings. The order, first wins: `/model` in the session, then `--model`, then `ANTHROPIC_MODEL`, then the settings key.

## Effort

**Effort** controls how much the model reasons before acting, on models that support it: `low`, `medium`, `high`, `xhigh`, `max`. Lower is faster and cheaper; higher thinks harder on complex steps.

```bash
claude -p "..." --effort low
```

In the console, `/effort` shows a slider and `/effort status` the level in effect. If you pick a level the model does not support, Claude Code uses the highest supported level below it.

## A rule of thumb

Start a task on the cheapest model that can do it. Move up when the output is wrong in ways that need reasoning, not when it is merely slow. The next lesson shows how to measure instead of guessing.

## Commands this node introduces

`--model <alias>`, `/model`, `--effort <level>`, and `/effort`.
