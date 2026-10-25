---
type: lesson
title: "Reproduce, locate, fix, verify"
minutes: 14
---

Bug fixing with an agent follows the same four steps as without one. The agent makes each step faster; it doesn't let you skip any.

## 1. Reproduce

Turn "the counts look wrong" into a command with an expected and an actual output:

```text
$ python3 logcount.py app.log
WARN 3          <- expected 2: an independent count says 2 WARN lines
```

The **expected** value must come from somewhere other than the code under suspicion: a spec, a hand count, `grep -c`, a second implementation.

## 2. Locate

Give Claude the reproduction, not a guess: "Running `logcount.py app.log` prints WARN 3; there are 2 WARN lines. Find why." Claude reads the code, narrows it to a line, and explains the mechanism. Here: `if level in line` matches the word anywhere in the message.

## 3. Fix - test first

1. Write a **regression test** that fails for the reported reason. Run it and watch it fail: a test that never failed proves nothing.
2. Make the smallest change that turns it green.
3. Run the whole suite: the fix must not break anything else.

## 4. Verify

Re-run the original reproduction and compare it with the expected output. Then check the edge cases the fix touched (blank lines, malformed lines, other levels).

## The fix comes with

| Deliverable | Why |
|---|---|
| A reproduction (command, expected, actual) | Anyone can confirm the bug and the fix |
| A regression test that failed before | The bug cannot quietly return |
| The smallest code change | Easy review, low risk |
| A root-cause sentence | The reviewer learns why, not just what |

## Commands this node introduces

Reproduce, locate, fix test-first, verify: the four-step loop, with the regression test as the contract.
