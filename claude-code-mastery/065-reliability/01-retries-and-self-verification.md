---
type: lesson
title: "Retries and self verification"
minutes: 19
---

An agent's "Done, all tests pass" is a claim, not a result. Reliable automation treats each run as an **attempt**. Then it checks the attempt with something the agent doesn't control, and feeds the evidence back on failure.

## The loop

```text
attempt 1: claude -p "$task"                                   → envelope (session_id)
           verify (your command, your tests)                     → fail: keep the output
attempt 2: claude -p "Verification failed: <output>" --resume $sid → envelope
           verify                                                → pass → exit 0
...        up to N attempts                                      → exit 1, with every attempt logged
```

| Rule | Why |
|---|---|
| **Verify with your own command**, every attempt | The agent's summary is the least reliable signal in the loop |
| **Resume the same session** on retry (`--resume "$sid"`) | The agent keeps what it read and tried, so the retry is a correction, not a cold start |
| **Feed back the evidence**, trimmed (`tail -40` of the failing output) | "It failed" makes the agent guess. The assertion error tells it what's wrong |
| **Protect the verifier** | Deny edits to the tests (`--disallowedTools "Edit(tests/**)" "Write(tests/**)"`), *and* check their hash after each attempt. An attempt that touches them fails, and they're restored |
| **Bound it** | A maximum number of attempts plus `--max-turns` per attempt. A task that fails three corrected attempts needs a human, not a fourth |
| **Treat errors as failed attempts** | `is_error: true`, a non-zero exit or an unreadable envelope all count as an attempt that didn't work |
| **Log every attempt** | One row each in `attempts.jsonl` (attempt, session, verify exit, cost). That's how you notice a task that usually needs two tries |

## What counts as verification

The verifier must be able to fail. Good verifiers include:
- the test suite, or a single focused test;
- `python3 -m py_compile`, a type checker, or a linter;
- a schema check on JSON output;
- `grep` for facts you computed (topic 061);
- a dry run of the deploy.

Asking the agent "are you sure?" doesn't count.

## Retrying transient failures vs. wrong answers

| Failure | Retry how |
|---|---|
| `529 overloaded`, a network error, a `429` rate limit | The same prompt after a backoff. Nothing is wrong with the work |
| The verifier fails | A correction prompt with the evidence, in the same session |
| The agent changed the tests, or went out of scope | Fail the attempt, restore, and say in the next prompt that tests are off limits |
| Every attempt fails the same way | Stop. The task, the environment or the tests need a person |

## Commands this node introduces

`--resume "$sid"`, `tail -40` evidence, `sha256sum` (or `shasum -a 256`) on protected files, `attempts.jsonl`, and bounded attempts.
