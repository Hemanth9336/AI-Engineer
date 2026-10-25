---
type: lesson
title: "Causes of flaky tests"
minutes: 19
---

A flaky test passes and fails on the same code. It is worse than a failing test: people learn to click "re-run", and then they stop believing red builds at all.

## Where nondeterminism hides

| Source | Typical symptom | How to force it |
|---|---|---|
| Hash and set ordering | A list built from a `set` or a hash map comes out in a different order | Vary `PYTHONHASHSEED` (Python randomizes string hashing per process) |
| Time | Fails near midnight, at month end, or on the CI machine's timezone | Set `TZ`, freeze or inject the clock |
| Unseeded randomness | Fails one run in fifty | Fix the seed, then sweep seeds |
| Test order and shared state | Passes alone, fails in the suite | Run tests in a different order or one at a time |
| Concurrency | Fails under load | Run in parallel, add stress |
| External services | Timeouts, rate limits | Run offline; fake the service |

## Detect: rerun and vary one factor

A single green run says nothing. Rerun the suite many times, and **deliberately vary the factor you suspect**, recording which values fail:

```bash
for seed in $(seq 0 29); do
  if PYTHONHASHSEED=$seed python3 -m unittest -q 2>/dev/null; then echo "seed=$seed pass"; else echo "seed=$seed fail"; fi
done | tee hunt.log
```

If some seeds fail and others pass, you have both **proof** of the flake and a way to **reproduce** it on demand: `PYTHONHASHSEED=3 python3 -m unittest`.

## Fix the cause, not the symptom

- **Not a fix:** retry decorators, `sleep`, deleting the assertion, sorting the expected value so any order passes. Each one hides a real contract violation.
- **A fix:** make the code honor its contract. "First-seen order" means an ordered structure (`dict.fromkeys`), not a `set`.
- **Quarantine** (skip with a ticket) only while a fix is in progress, never as the end state.

## With the agent

Give Claude the evidence (which seeds fail), take away the shortcut (`--disallowedTools "Edit(tests/**)"`), and let it run the hunt script itself to confirm that zero runs fail.

## Commands this node introduces

`PYTHONHASHSEED`, a seed sweep that logs pass or fail per run, and reproducing a flake on demand.
