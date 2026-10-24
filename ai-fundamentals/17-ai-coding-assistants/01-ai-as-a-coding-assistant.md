---
type: lesson
title: "AI as a coding assistant"
minutes: 8
---

Coding assistants are the most widely used AI tools in software teams. They come in a few shapes, and knowing which to reach for saves a lot of time.

## Three kinds

| Kind | What it does | Examples |
|---|---|---|
| **Autocomplete** | Suggests the next lines as you type | Copilot, Cursor Tab |
| **Chat in the editor** | Answers questions about your code, writes snippets you paste in | Editor chat panels |
| **Coding agents** | Reads files, runs commands, edits code, and checks its work in a loop | Claude Code, Cursor Agent, Codex CLI, Copilot agent |

Agents are the big shift of the last two years: instead of you copying code around, the assistant uses tools (topic 16) - read file, edit file, run tests - to finish a task.

## Where they shine

- **Boilerplate**: scripts, config files, test scaffolding, CLI argument parsing.
- **Explaining** unfamiliar code, errors, and stack traces.
- **Translating** between languages or frameworks.
- **Small, well-defined changes** with a clear way to check them (a test, a command).
- **Investigation**: "find where we set the retry timeout".

## Where they struggle

- **Vague goals**: "make it better" gets you a random refactor.
- **Large, cross-cutting designs** with many hidden constraints.
- **Your private context**: internal conventions, why a weird line exists - unless you tell them or keep it in a rules file.
- **Correctness under pressure**: code that looks right but misses an edge case.

## The golden rule

**You own the code.** Treat AI output like a pull request from a fast, confident new colleague:

1. Read it before running it - especially anything with `rm`, `sudo`, credentials, or network calls.
2. Run it on a safe input first.
3. Test the edge cases (empty input, missing file, bad arguments).
4. Commit only what you understand.

## Good prompts for code

Say the language, the inputs and outputs, the edge cases, and the constraints:

```text
Write a bash script count_errors.sh. Usage: count_errors.sh LOGFILE.
Print the number of lines containing ERROR. If the argument is missing or the
file does not exist, print a usage message to stderr and exit 1.
```

That prompt is also a test plan. Next: driving an assistant from the terminal.
