---
type: lesson
title: "Conventional commit messages"
minutes: 14
---

**Conventional Commits** is a small format that makes history readable by people and tools (changelogs, semantic versioning):

```text
<type>(<optional scope>): <subject>

<body: what and why, wrapped at ~72 columns>

<footers: BREAKING CHANGE: ..., Refs: #123>
```

| Type | For |
|---|---|
| `feat` | A new feature (minor version bump) |
| `fix` | A bug fix (patch bump) |
| `docs`, `test`, `refactor`, `perf`, `chore`, `ci`, `build`, `style` | Everything else |
| `!` after the type, or a `BREAKING CHANGE:` footer | A breaking change (major bump) |

## A good subject line

- Imperative mood: "fix VAT rounding", not "fixed" or "fixes".
- Lower case after the colon, no trailing period, **72 characters or fewer** including the prefix.
- Says *what changed for the user*, not which lines moved.

```text
fix(pricing): round VAT to the nearest cent

Credit notes were rounding VAT down, so totals could be off by one cent.
Use round() on the computed tax and add a regression test.
```

## Asking the agent for one

Give it the format and the facts it cannot infer:

> Read the staged diff with `git diff --cached`. Commit **only the staged changes** with a Conventional Commits message: type and scope from the diff, imperative subject of 72 characters or fewer, a body explaining why. Do not stage anything else.

Then check it: `git log -1 --format=%B`. If the type is wrong - a bug fix labelled `feat` - amend before pushing: `git commit --amend`.

## Commands this node introduces

`git log -1 --format=%B` shows the full last message; `git commit --amend` fixes it before you push.
