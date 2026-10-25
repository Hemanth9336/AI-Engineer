---
type: lesson
title: "Plan, execute, verify"
minutes: 19
---

A one-file change can be steered turn by turn. A feature that touches the model, the storage layer, the CLI, and the tests needs a loop with three distinct phases, and a different trust level in each.

| Phase | Mode | The agent may | You check |
|---|---|---|---|
| **Plan** | `--permission-mode plan` | Read and search only | Every file that must change is named, compatibility is addressed, and the tests are listed |
| **Execute** | `--permission-mode acceptEdits`, plus `--allowedTools` for the test command | Edit files and run the tests | Nothing yet: let it finish its own red-green loop |
| **Verify** | Your script, not the agent's word | - | The suite passes, a smoke test of the real entry point passes, and old data still loads |

## Plan in plan mode, and keep the plan

```bash
claude -p "$(cat FEATURE.md) Produce a plan: files to change, data compatibility, and the tests to add." \
  --permission-mode plan --output-format json < /dev/null > plan.json
jq -r .result plan.json > PLAN.md
```

In plan mode Claude can read but not edit. Saving the plan as a file turns it into a reviewable artifact and makes it the input for the next phase. A plan that doesn't mention **backward compatibility** (old `tasks.json` files without the new field) is the usual way a multi-file feature breaks production while every test passes.

## Execute against the plan

```bash
claude -p "Implement PLAN.md. Run python3 -m unittest after your edits and fix failures until the suite passes." \
  --permission-mode acceptEdits --allowedTools "Bash(python3 -m unittest *)" --output-format json < /dev/null > exec.json
```

Allowing the test command matters. An agent that can't run tests will tell you it's done; one that can will find out it isn't.

## Verify independently

"All tests pass" means only the tests the agent wrote pass. Verification is a script **you** own:

1. Run the whole suite.
2. Smoke-test the real entry point (`python3 -m tasks.cli ...`) in a temporary directory, the way a user would.
3. Load a fixture in the **old** data format.
4. Prove the script itself works: run it against the pre-feature code and watch it fail.

```bash
./verify.sh                       # exit 0 only when everything above holds
```

## Commands this node introduces

The plan, execute, and verify loop with `--permission-mode plan` and `--permission-mode acceptEdits`, saving the plan with `jq -r .result`, and an independent `verify.sh` that is itself tested against the old code.
