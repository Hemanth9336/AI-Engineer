---
type: lesson
title: "Commit messages and changelogs from diffs"
minutes: 19
---

Writing commit messages and changelog entries is a small, frequent chore, and a good first bot: one input (the diff), a constrained output, and a deterministic action (commit).

## Conventional commits

```text
feat(greet): add farewell helper

Callers needed a matching goodbye message for the CLI exit path.
```

| Part | Rule |
|---|---|
| `type` | One of a fixed set: `feat`, `fix`, `docs`, `refactor`, `test`, `chore` |
| `(scope)` | Optional, lowercase: the area touched |
| subject | Imperative ("add", not "added"), at most 72 characters, no trailing period |
| body | Why the change exists; the diff already shows what |

The changelog entry is different: it's for **users**, not developers. "Add `farewell(name)` for goodbye messages", under `## Unreleased`.

## The bot's shape

1. **Nothing to commit? Stop.** `git status --porcelain` is empty: exit 0 without calling the model. No diff, no tokens.
2. **Stage and pipe.** `git add -A`, then `git diff --cached | claude -p "..."`. This time stdin is the input **on purpose**: `claude -p` appends it to the prompt.
3. **No tools.** `--tools ""` removes every built-in tool. The diff is all the context the bot needs, and a bot that can't run commands can't wander.
4. **Constrain the answer.** `--json-schema` with an enum for `type`, a pattern for `scope`, and `maxLength` for the subject.
5. **Validate in code anyway**, then write the changelog and commit. Your validator, not the model, decides what gets committed.
6. **Fail atomically.** If anything fails, `git reset -q` to unstage and exit 1. The repository is exactly as you found it, and nothing half-done is committed.

## What the diff can't tell the model

A diff shows what changed, not why. For a bot, either accept a body that only describes the change, or pass the why in (a ticket title, the branch name, a line from the author). Never let the model invent a motivation.

## Commands this node introduces

`git diff --cached | claude -p`, `--tools ""`, conventional commits, and a validator that owns the commit.
