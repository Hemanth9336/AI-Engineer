---
type: lesson
title: "What an agent task costs"
minutes: 9
---

An agent run is not one model call. It is a loop, and every turn sends the whole conversation so far back to the model.

## Where the tokens go

| Part | Sent | Notes |
|---|---|---|
| System prompt and tool definitions | Every turn | Thousands of tokens before you type anything; MCP servers add their tool schemas |
| CLAUDE.md, rules, skill descriptions | Every turn | Why short instruction files matter |
| Your prompt and every tool result so far | Every turn after they appear | A 2,000-line file read once is paid for on every later turn |
| The model's output | Once | Priced higher per token than input |

Two effects dominate:

- **Turns multiply input.** A 10-turn run re-sends its growing context ten times. Fewer, better turns beat a cheaper model that flails.
- **Prompt caching discounts the repeated prefix.** Claude Code caches the stable start of the context, so later turns read it at a fraction of the input price. In the JSON envelope that shows as `cache_read_input_tokens`; `/usage` shows a `Prompt cache (main)` line in a live session.

## The tier is a multiplier, not the bill

A smaller model (haiku) costs far less per token than a larger one (sonnet, opus). But the bill is **price per token × tokens × turns × retries**. A smaller model that needs three attempts, or twice as many turns, can cost more than a larger model that gets it right once. The only honest comparison is **cost per successful task**.

## Reference points

- Anthropic reports enterprise averages around $13 per developer per active day, under $30 for 90% of users.
- `total_cost_usd` and `/usage` are **estimates computed locally at list price**. Subscribers don't pay them per run. Organizations on contracted rates set `modelPricing` so the figures match the bill.

## Commands this node introduces

`/usage`, `total_cost_usd`, `usage.cache_read_input_tokens`, and the idea of cost per successful task.
