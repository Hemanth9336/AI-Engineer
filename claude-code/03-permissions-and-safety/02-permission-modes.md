---
type: lesson
title: "Permission modes"
minutes: 6
---

Rules decide individual actions. A **permission mode** sets the baseline for the whole session.

| Mode | Edits | Commands | Use it for |
|---|---|---|---|
| `default` | Ask | Ask | Normal work, unfamiliar repos |
| `acceptEdits` | Allowed | Ask (or denied in `-p`) | You trust the edits, want to review commands |
| `plan` | Blocked | Blocked (read-only only) | Explore and propose a plan, change nothing |
| `bypassPermissions` | Allowed | Allowed | Throwaway containers and VMs only |

## Switching modes

- In the console, **Shift+Tab** cycles through default, accept edits and plan mode; the current mode shows under the prompt.
- At start-up: `claude --permission-mode plan`.
- Headless: `claude -p "..." --permission-mode acceptEdits`.
- As a project default: `"defaultMode": "acceptEdits"` inside `permissions` in `.claude/settings.json`.

## acceptEdits is not "do anything"

`acceptEdits` lets Claude change files without asking each time. It does not let it run `rm`, `curl` or your deploy script - those still need a rule or your Yes. That's the sweet spot for most headless jobs:

```bash
claude -p "Add type hints to utils.py" --permission-mode acceptEdits
```

Edits happen; nothing else does.

## bypassPermissions is a sharp tool

It skips every check (deny rules still apply). Anthropic's own advice: only inside an isolated container or VM with no secrets and no access to things you'd mind losing. On your laptop or a shared server, it's the wrong mode. If you're tempted because the prompts are annoying, write allow rules for the safe commands instead.

## Picking a mode

1. Unknown repo, or anything touching production? `default` or `plan`.
2. Routine edits you'll review in `git diff` afterwards? `acceptEdits`.
3. CI job that must run tests? `acceptEdits` plus `--allowedTools "Bash(npm test:*)"`.
4. Disposable sandbox for an experiment? Maybe `bypassPermissions`.

Next, you'll write an allowlist that lets an agent run the tests - and stops it cold at the deploy script.
