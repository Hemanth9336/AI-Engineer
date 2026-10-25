---
type: lesson
title: "Agents and data analysis"
minutes: 19
---

Ask a model "what was Q3 revenue?" with a 240-row CSV pasted in and you get a confident, plausible, wrong number. Language models don't add up hundreds of values reliably in their heads. Coding agents don't have to: they can write the arithmetic as code and run it.

## Make the agent compute, never estimate

- **Code, not context.** "Write `analysis.py` that loads the CSV with the `csv` module and computes each answer; run it." The numbers come from Python, not from the model.
- **Peek, don't swallow.** For large files, the agent should read the header and a few rows (`head -5`), then work with code. Loading a 50 MB CSV into context is slow, expensive, and still won't be summed correctly.
- **Keep the script.** `analysis.py` is the audit trail: anyone can re-run it and get the same answers. A number without the code that produced it is an opinion.

## Definitions decide the answer

Most "wrong" analyses are ambiguous questions. Pin the definitions in the question itself:

| Ambiguity | Pinned |
|---|---|
| "Revenue" | Net: `units × unit_cents`, returned orders excluded |
| "Q3" | `2026-07-01` to `2026-09-30`, inclusive |
| "Median order value" | Over orders, not over line items; an even count takes the mean of the middle two |
| Ties | Say how to break them, or ask for all tied values |

## Sanity checks

Before trusting a result, reconcile it: the row count matches `wc -l` minus the header, per-region totals sum to the overall total, and each quarter's revenue is no more than the year's. Have the script print these checks, or assert them.

## When to reach for pandas

The `csv` module plus the standard library is enough for one-off questions and keeps the lab dependency-free. For joins, pivots, and time series, `pandas` is the usual tool. The principle is the same: the agent writes and runs the code, and you keep the code.

## Commands this node introduces

`analysis.py` as the audit trail, pinned definitions, and reconciliation checks.
