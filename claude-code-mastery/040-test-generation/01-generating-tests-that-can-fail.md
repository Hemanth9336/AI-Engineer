---
type: lesson
title: "Generating tests that can fail"
minutes: 19
---

Asking an agent to "write tests" is easy. The trap: a generated suite that passes on the first run tells you almost nothing. It may only assert what the code already does, bugs included, or assert nothing that matters.

## What good generated tests do

- **Pin the contract, not the implementation.** Read the docstring and the callers: "10+ units get 5% off" is the contract. Test the boundaries: 9, 10, 49, 50, 99, 100.
- **Cover the error paths.** Negative quantities, unknown coupon codes - whatever the docstring says should raise.
- **Use exact expected values** computed independently (by hand or from the spec), never copied from a run of the code under test.
- **Stay fast and deterministic.** No sleeping, no network, no random data without a fixed seed.

## Prove the suite can fail: mutation testing

A **mutant** is a copy of the code with one small deliberate bug: `>=` changed to `>`, rounding removed, a `raise` deleted. Run the suite against each mutant:

| Result | Meaning |
|---|---|
| Suite fails | The mutant is **killed**: your tests would catch that bug |
| Suite passes | The mutant **survived**: a real bug of that shape would ship |

The loop is mechanical:

```bash
cp pricing/discounts.py /tmp/original.py
for m in mutants/*.py; do
  cp "$m" pricing/discounts.py
  if python3 -m unittest -q 2>/dev/null; then echo "SURVIVED $m"; else echo "KILLED $m"; fi
done
cp /tmp/original.py pricing/discounts.py        # always restore
```

Tools like `mutmut` generate mutants automatically. A handful of hand-written ones for the riskiest lines already catches most weak suites.

## Driving the agent

Give Claude the contract and the bar: "Write tests from the docstrings, include boundary values and error cases, compute expected values by hand, and run them." Then run the mutants yourself. Feed survivors back: "this mutant survived - add a test that kills it."

## Commands this node introduces

Mutants, killed versus survived, and a restore-always loop around `cp`.
