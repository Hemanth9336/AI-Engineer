---
type: lesson
title: "Comparing agents on equal terms"
minutes: 10
---

Claude Code and OpenAI's Codex CLI are the same kind of tool: an agent loop in your terminal that reads files, runs commands, edits code, and keeps going until the task is done. Teams often run both. Comparing them is only useful if the comparison is fair, and a fair comparison is mostly about controlling everything except the tool.

## Hold everything else still

| Keep the same | Why |
|---|---|
| The repository state | Start both runs from the same commit, in separate worktrees or clean checkouts |
| The instructions file | One `AGENTS.md` both tools read (next lesson) |
| The guardrails | Equivalent permissions on both sides (third lesson) |
| The prompt | Word for word, saved in a file |
| The success test | A command that decides pass or fail, such as the test suite, not your impression of the transcript |

Then compare **outcomes**: did the tests pass, how big is the diff, how many turns and how long, what did it cost, and how often did a human have to step in.

## The same jobs, side by side

| Job | Claude Code | Codex CLI (0.164) |
|---|---|---|
| Interactive session | `claude` | `codex` |
| One-shot, scripted | `claude -p "..."` | `codex exec "..."` |
| Final answer only | default text output | stdout of `codex exec` (progress goes to stderr) |
| Event stream | `--output-format stream-json --verbose` | `--json` (`thread.started`, `item.*`, `turn.completed`) |
| Shaped final answer | `--json-schema '<schema>'`, read `structured_output` | `--output-schema schema.json`, `-o answer.json` |
| Continue a run | `claude -c`, `--resume <id>` | `codex resume --last`, `codex exec resume --last` |
| Choose the model | `--model` | `-m` |
| Isolated worktree | `--worktree` / `-w` | `--worktree` |
| Don't save the session | `--no-session-persistence` | `--ephemeral` |
| Skip personal config | `--bare` (skips CLAUDE.md, hooks, MCP, skills) | `--ignore-user-config`, `--ignore-rules` |
| Piped stdin | appended to the prompt | appended as a `<stdin>` block; `codex exec -` reads the whole prompt from stdin |

## Defaults that skew a comparison

- `codex exec` runs in a **read-only sandbox** by default. An edit task "finishes" with no edits unless you pass `--sandbox workspace-write`.
- `claude -p` refuses edits and commands it has no permission for, and reports success anyway. Pre-approve tools with `--allowedTools` or project settings.
- `codex exec` refuses to run outside a git repository unless you add `--skip-git-repo-check`.
- Both tools read their personal config (`~/.claude`, `~/.codex`) unless told not to, so a teammate's machine can behave differently from yours.

The rule is the same as in your headless pipelines: decide by checking the repository afterwards (`git diff`, tests), never by what the agent says it did.

## Commands this node introduces

`codex exec`, `--sandbox workspace-write`, `--json`, `--output-schema`, `--ephemeral`, and `--worktree` on both tools.
