---
type: lesson
title: "Grading trajectories, not just answers"
minutes: 7
---

A chatbot eval is simple: question in, answer out, compare. An agent is different. Between the question and the answer it takes **actions** - reads files, calls APIs, writes, deletes, emails - and the answer is only part of what it did.

## Two agents, same answer

```text
Task: "Which port does billing use?"

Agent A: read_file(services/billing.yaml) -> "Billing uses port 8081."
Agent B: list_dir(.) x 6, read_file every file, delete_file(tmp.txt) -> "Billing uses port 8081."
```

Graded on the answer alone, both pass. But B took 8 steps, cost 5x more - and deleted a file nobody asked it to touch. An agent eval has to see the **trajectory** (every step) and the **resulting state** (what changed in the world), not just the last message.

## What to grade

| Dimension | Question | Example check |
|---|---|---|
| **Outcome** | Is the answer right? Is the world in the right state? | Answer contains 8081; `notes/oncall.md` contains the line |
| **Safety** | Did it avoid things it must never do? | `delete_file` never called; `README.md` unchanged |
| **Process** | Did it use the right tools, and not the wrong ones? | `read_file` was called (it didn't guess) |
| **Efficiency** | How many steps, tokens, seconds? | At most 2 tool calls; under 5,000 tokens |
| **Honesty** | Does the answer match what it actually did? | It says "I created the file" and the file exists |

## Where the data comes from

You can only grade what you recorded. A harness that's ready for evals:

- writes a **trace** of every tool call (name, arguments, result) - topic 31 makes it a full transcript;
- runs each eval task in a **fresh copy** of the workspace, so tasks don't affect each other and you can compare before/after;
- reports **usage** per call, so cost can be graded (topic 32).

## Agents are not deterministic

The same task can pass on one run and fail on the next. One run per task tells you little about a rare failure. Real suites run each task several times and report a **pass rate** ("8/10"), and track it over time.
