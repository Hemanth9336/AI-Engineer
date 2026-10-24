---
type: lesson
title: "Uses at work"
minutes: 6
---

At work the same abilities - drafting, summarizing, explaining, transforming text - turn into real time savings, especially for engineers.

## For every professional

- **Meeting notes and follow-ups.** Turn a transcript into decisions, owners, and dates.
- **Writing for different audiences.** One technical update, rewritten for executives, customers, and the support team.
- **Reading at speed.** Summarize a 40-page vendor document, an RFC, or a long email chain.
- **Spreadsheets.** "Write a formula that flags rows where the due date has passed and status is not Done."
- **Research starting points.** Outline the options for a decision before you dig into real sources.

## For engineers

| Job | What you hand the AI |
|---|---|
| Explaining code | "What does this function do, and what happens if `items` is empty?" |
| Writing code | A small script, a regex, a SQL query, a unit test |
| Debugging | The error message, the code, and what you expected to happen |
| Reading logs | A burst of log lines - what failed first, and why? |
| Documentation | A README, a runbook, docstrings, a changelog from commit messages |
| Converting formats | CSV to JSON, a bash script to Python, YAML to a table |
| Reviewing | "Review this diff for bugs and missing error handling" |

## AI in software you build

The bigger shift is that AI becomes **part of the software itself**. A support system sorts incoming tickets. A monitoring tool explains an alert in plain English. An internal tool answers questions from the company's own runbooks. Each of these is an LLM called from code, with a carefully written prompt and a check on the output.

That is where this course goes. From topic 05 you call models from code, and the three projects at the end build exactly those tools: a ticket triage tool, a log explainer, and a runbook assistant.

## Still your name on it

Whatever the AI drafts, you ship. Code it wrote still needs reading and testing; a summary of a contract still needs checking against the contract. Next: an honest look at where AI falls short.
