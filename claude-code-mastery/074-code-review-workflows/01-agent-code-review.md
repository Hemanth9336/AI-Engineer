---
type: lesson
title: "Agent code review"
minutes: 14
---

An agent reviewer is fast, tireless and good at the mechanical half of review: injection, swallowed errors, missing checks, leftover debug flags. It isn't accountable for the merge. Use it as a **disciplined first pass** that a human finishes.

## `/code-review` in your session

```text
/code-review                     # current branch + uncommitted changes
/code-review high                # pick the effort: low through max (and ultra, a deeper cloud review)
/code-review main...my-feature   # one branch against another
/code-review 1234                # a pull request by number
/code-review src/auth            # a path
/code-review --fix               # also apply the findings (through your permission mode)
/code-review --comment           # post findings as PR inline comments (or one GitLab MR note via glab)
/code-review --max-findings 10   # cap the number of findings
```

| Effort | What it does |
|---|---|
| `low` | Reports only the findings it's most confident in, so there are fewer false positives |
| `medium` through `max` | Broader coverage, more findings, more cost |
| `ultra` | A deeper review in the cloud. It needs a claude.ai account, and isn't available on Bedrock, Agent Platform or Foundry |

A level you type is remembered for later runs (except in `-p` and `ultra`). The review runs as a background subagent with its own context, follows your `CLAUDE.md`, and works on any plan. `/review` is an alias.

## Managed Code Review on GitHub

For Team and Enterprise, the **Code Review** product reviews pull requests on GitHub automatically: when a PR opens, on every push, or on request with `@claude review`. It posts inline comments ranked by severity, a summary, and a **Claude Code Review** check run.

- It reads `REVIEW.md` and `CLAUDE.md` **from the base branch**, never from the PR's own changes. A PR can't rewrite its own review rules.
- It **never approves or blocks** a PR, and its check run doesn't conclude as a failure. The merge decision stays with people.
- It runs read-only on Anthropic infrastructure and doesn't build or run your code.

Local `/code-review` doesn't read `REVIEW.md`. Put team-wide review rules in `CLAUDE.md` or a skill, and repo-wide managed-review tuning in `REVIEW.md`.

## Commands this node introduces

`/code-review` (`/review`), effort levels, `--fix`, `--comment`, `--max-findings`, review targets, `ultra`, managed Code Review, `@claude review`, and `REVIEW.md`.
