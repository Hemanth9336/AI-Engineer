---
type: lesson
title: "Verdict files and exit codes"
minutes: 23
---

The release check is the deterministic heart of the release manager. Everything else reads its output, so its contract must be precise.

## The contract

| Situation | `verdict` | Exit code |
|---|---|---|
| Tests ran, all passed (and at least one ran) | `go` | 0 |
| Tests ran, any failure or error | `no-go` | 1 |
| Couldn't check: no tests folder, no summary, timeout | `error` | 2 |

```json
{"version": "1.1.0", "commit": "3f2c9e1...", "generated_at": "2026-10-25T21:03:11+00:00",
 "verdict": "go", "tests": {"ran": 6, "failed": 0, "errors": 0}}
```

## Rules that keep it honest

- **Three outcomes, not two.** "I couldn't tell" must never look like "go". A missing summary is `error`, not success.
- **Zero tests isn't green.** An empty suite says nothing about the code.
- **Write the verdict on every run.** A failed run must overwrite yesterday's `go`. Write to a temp file and rename it, so readers (like the HTTP endpoint) never see half a file.
- **Keep the raw output** (`test-output.txt`) next to the verdict, for humans and for the triage worker.
- **Record what was checked:** the commit and version. A verdict without a commit is a rumour.
- **Parse the runner's summary, not its prose.** `unittest` ends with `Ran N tests` and `FAILED (failures=F, errors=E)`. Its exit code is a second signal, so require both to agree.

```bash
python3 release/check.py; echo "exit $?"
jq . release/out/verdict.json
```

## Commands this node introduces

The go/no-go/error contract, exit codes 0, 1 and 2, the atomic write (temp file and rename), `test-output.txt`, and parsing the `Ran N tests` and `failures=` summary.
