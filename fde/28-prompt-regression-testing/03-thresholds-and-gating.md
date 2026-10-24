---
type: lesson
title: "Thresholds and gating"
minutes: 6
---

Comparing two result files by eye works once. To make it a habit, turn it into a **gate**: a script that exits non-zero when a change makes things worse, so a build pipeline (or you, before a release) can't miss it.

## What the gate checks

```text
python gate.py results/v1.json results/v2.json --max-drop 0.0
regressed: g1, g2
FAIL: score 0.67 < baseline 1.00 (max drop 0.00)
```

- **Score drop** - the candidate's score may fall at most `--max-drop` below the baseline. Exit `1` if it falls further.
- **Regressed cases** - cases that passed before and fail now. Always print them: they're what you'll read first.

## Choosing the threshold

| Suite | Threshold | Why |
|---|---|---|
| Small, stable code checks | `0.0` - no drop at all | Every case is deterministic and important |
| Larger judge-graded suite | `0.02-0.05` | Judges and models wobble a little between runs |
| Safety slice (traps, PII, refusals) | `0.0`, always | One invented fee or leaked record is one too many |

Gate safety slices separately and strictly; allow small noise only where it's real.

## Absolute bars too

Besides "no worse than last time", keep the **agreed bar** from the customer contract (topic 25): "at least 90% correct, 100% of traps refused". A candidate that's better than the baseline but still below the bar isn't ready either.

## Where it runs

Locally before you commit a prompt change; in CI on every pull request that touches prompts, retrieval or model settings; and nightly against the production configuration to catch provider-side drift.
