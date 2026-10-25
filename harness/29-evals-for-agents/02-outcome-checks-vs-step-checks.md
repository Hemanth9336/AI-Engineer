---
type: lesson
title: "Outcome checks vs step checks"
minutes: 8
---

There are two families of checks, and a good suite uses both.

## Outcome checks: grade the end state

Look at what the agent left behind, and don't care how it got there.

| Check | Passes when |
|---|---|
| `answer_contains` | The final answer contains a string ("8081") |
| `file_contains` | A file in the workspace contains some text |
| `file_unchanged` | A file is byte-for-byte what it was before |
| `file_absent` | A file doesn't exist afterwards |
| Tests pass | For coding agents: `pytest` succeeds in the resulting repo |

**Strengths:** they don't break when the agent finds a different, equally good path. They test what the user actually cares about.
**Weakness:** they can pass for the wrong reason - a lucky guess, or a correct answer reached by doing something dangerous along the way.

## Step checks: grade the trajectory

Look at the trace.

| Check | Passes when |
|---|---|
| `tool_called` | A tool was used at least once (it looked, rather than guessed) |
| `tool_not_called` | A tool was never used (no deletes, no emails) |
| `max_tool_calls` | It finished within N tool calls |
| Order | It read the file before writing it |

**Strengths:** they catch dangerous or wasteful behavior that outcome checks miss.
**Weakness:** they're brittle if you over-specify. "Must call list_dir, then read_file" fails a good agent that went straight to the right file.

## The rule of thumb

- **Outcome checks for correctness.** Is the result right?
- **Step checks for safety and cost.** Did it do anything it must not, and was it reasonably efficient?
- **Avoid step checks that encode one particular path**, unless that path is a real requirement.

## Make checks objective

Every check in the suite should be decidable by code, with no judgment call: a string match, a file comparison, a count. For things that need judgment (tone, completeness), use a model grader with a fixed rubric - and validate it against human grades first. Start with objective checks; you'll be surprised how far they get you.
