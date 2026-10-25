---
type: lesson
title: "Foundations recap"
minutes: 15
---

Twenty topics in, you have every piece needed to put Claude Code to work on a real repository safely. Here is the toolkit on one page.

| Area | What you now use | Where |
|---|---|---|
| The loop | Prompt, tool calls, results, repeat; `-p` and `--output-format json` for scripts | 001-002 |
| Reading | Read, Grep, Glob - and proving what was read from the transcript | 003 |
| Health | `claude --version`, `claude doctor`, a baseline script | 004 |
| Changing | Edit (after Read), Write, Bash; `permission_denials` in headless runs | 005 |
| Guardrails | Six modes; deny, ask, allow rules; trust; the sandbox | 006 |
| Boundaries | `--add-dir`, `/cd` | 007 |
| Models | `--model`, `--effort`, measuring with the envelope | 008 |
| Context | `/context`, `/compact`, handoff files | 009 |
| Instructions | `CLAUDE.md`, `/init`, levels, `@imports` | 010-011 |
| Memory | Auto memory, `MEMORY.md`, `/memory` | 012 |
| Reuse | Prompt files, skills, commands, plugins | 013-016 |
| Control | Plan mode, checkpoints, git restore | 017-018 |
| Shipping | Agent-written conventional commits of staged work | 019 |

## The order that works on any new repo

1. **Look before acting**: read-only exploration, or plan mode.
2. **Write down the rules**: a short `CLAUDE.md` with build, test, and convention lines.
3. **Fence it**: deny secrets and destructive commands; allow the test command; trust the folder.
4. **Package the ritual**: one command or skill for the check you run constantly.
5. **Checkpoint**: clean tree, then let the agent work.
6. **Verify**: tests, `git status`, the envelope's `permission_denials`.
7. **Ship**: commit only what you meant, with a message a reviewer can trust.

## Mistakes worth not repeating

- Trusting `subtype: success` without checking the work.
- `bypassPermissions` on a machine with credentials.
- Rules in `CLAUDE.md` that should be deny rules.
- Relying on `/rewind` for Bash changes.
- `git add -A` with secrets in the tree.

## Commands this node introduces

None new - the challenge uses only what you already know, with no hints.
