---
type: lesson
title: "Surviving model updates"
minutes: 5
---

Your prompt was tuned for one model. Providers change models all the time:

- **Deprecation**: a model is announced for retirement - typically 3-12 months' notice - then requests start failing.
- **Silent updates**: an alias like `gpt-4o` or `claude-sonnet-latest` can start pointing to a newer snapshot.
- **Price and limit changes**: a cheaper successor appears; rate limits shift.

A new model is usually better overall, and still behaves **differently** on your prompts: longer answers, a different refusal style, stricter or looser format-following. "Better on benchmarks" does not mean "passes our tests".

## Defences

1. **Pin a dated model version** in production, not a moving alias: e.g. `gpt-4o-2024-08-06` or `claude-sonnet-4-20250514`. Your gateway's model name (`lab-fast`) maps to one pinned version.
2. **Use a gateway alias in your code.** Code says `support-model`; the gateway decides which pinned version that is. Switching is a config change, with no code deploy.
3. **Keep an eval suite** (later in this skill) and run it on the candidate model **before** switching.
4. **Switch in stages**: a share of traffic first, compare metrics, then all of it.
5. **Track deprecation notices** - put the provider's deprecation page in your runbook and calendar the dates.

## Migration checklist

```text
[ ] Candidate model chosen and pinned
[ ] Eval suite run on old and new model - scores compared
[ ] Prompt adjusted if needed (new prompt version)
[ ] Cost and latency measured on real prompts
[ ] Rollout plan: 10% -> 50% -> 100%, with a rollback switch
[ ] Customer informed of the change and the results
```

The customer cares about one thing: the assistant keeps working. Your job is to make a model change boring.
