---
type: lesson
title: "Headless Claude Code in a pipeline"
minutes: 19
---

A CI system reads two things from a step: its **exit code** and the files it leaves behind. A Claude Code step is only useful in CI when both are reliable, which means designing for every way the step can end.

## What `claude -p` gives a pipeline

| Signal | Where | Meaning |
|---|---|---|
| Exit code | `$?` | `0` when the run completed; non-zero when it errored, hit `--max-turns` or `--max-budget-usd`, or couldn't start |
| `is_error` | JSON envelope (`--output-format json`) | `true` for any error ending, even if you didn't look at the exit code |
| `subtype` | JSON envelope | `success`, `error_max_turns`, `error_max_budget_usd`, `error_during_execution`, or `error_max_structured_output_retries` |
| `structured_output` | JSON envelope, with `--json-schema` | The schema-validated answer, which is the only part a gate should parse |
| `total_cost_usd`, `num_turns`, `session_id` | JSON envelope | For budgets, dashboards, and finding the transcript |

A run cut off by `--max-turns 1` exits `1` with `{"subtype": "error_max_turns", "is_error": true, "errors": ["Reached maximum number of turns (1)"]}`.

## Fail closed

The question a gate asks is not "did Claude say it's fine?" but "**do I have a valid, positive verdict?**" Anything else should fail the build. That includes a crash, a timeout, a missing `structured_output`, a garbled file, or a verdict you don't recognize.

```bash
claude -p "$(cat ci/review-prompt.txt)" --tools Read --allowedTools Read --max-turns 6 \
  --json-schema "$(cat review.schema.json)" --output-format json < /dev/null > review.json
rc=$?
if [ $rc -ne 0 ] || ! jq -e '.is_error == false and (.structured_output.verdict | type == "string")' review.json > /dev/null 2>&1; then
  echo "review step failed" >&2; exit 3          # broken step: not a pass, not a code problem either
fi
```

Distinct exit codes per outcome make the pipeline's red mean something: `1` tests failed, `2` the review found a blocker, `3` the review step itself broke.

## Shell traps in CI scripts

- **`claude ... | jq`** returns `jq`'s exit code. Use `set -o pipefail`, or write to a file and check `$?` before parsing.
- **`set -e` plus an expected failure** aborts the script before you can report it. Capture the result with `if ! cmd; then ...` or `cmd || rc=$?`.
- **stdin**: CI runners may attach a pipe, and `claude -p` appends piped stdin to the prompt. Close it with `< /dev/null`.
- **Don't trust a verdict over its evidence.** If the schema has severities, recompute: any `blocker` finding blocks, whatever `verdict` says.

## Keep the step bounded and reproducible

`--max-turns` and `--max-budget-usd` cap the work. A job-level timeout (`timeout-minutes` in GitHub, `timeout` in GitLab) caps wall time. Give it the narrowest tools (`--tools Read` plus `--allowedTools Read` for a reviewer). `--bare` skips user CLAUDE.md, hooks, and plugins, so the run on CI matches the one on your laptop. Credentials come from the CI secret store as `ANTHROPIC_API_KEY`, never from the repository.

## Commands this node introduces

The `claude -p` exit code, `is_error` and `subtype`, `--json-schema` with `structured_output`, `--max-turns`, `--max-budget-usd`, `set -o pipefail`, and fail-closed gating with distinct exit codes.
