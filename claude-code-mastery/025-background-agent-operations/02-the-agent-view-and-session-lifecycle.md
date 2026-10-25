---
type: lesson
title: "The agent view and session lifecycle"
minutes: 12
---

`claude agents` opens **agent view**: one screen listing every session, grouped by state, with the ones that need you at the top.

| State | Meaning |
|---|---|
| `working` | A turn is running, or it is between steps of work it drives itself |
| `blocked` | It needs **you**: a question, a permission prompt, a sandbox decision, an expired login |
| `done` | It finished what you asked and waits for your next prompt |
| `failed`, `stopped` | It ended with an error, or you stopped it |

From agent view you can peek at a session, reply without attaching, attach fully (`←` or `/exit` detaches again), pin, filter, and dispatch new sessions.

## From scripts

`claude agents --json` is the supported interface for programs:

```bash
claude agents --json --all | jq -r '.[] | select(.name == "nightly-audit") | .state'
```

Each entry has `cwd`, `kind` (`interactive` or `background`), `id`, `state`, and - while the process lives - `pid`, `status` (`busy`, `waiting`, `idle`), and `waitingFor`. `--all` includes finished background sessions. The files under `~/.claude/jobs/` are internal and change without notice; do not parse them.

## Lifecycle commands

| Command | Does |
|---|---|
| `claude logs <id or name>` | Recent output |
| `claude attach <id or name>` | Open it in this terminal |
| `claude stop <id>` | Stop it |
| `claude respawn <id>` | Restart it, e.g. on a new binary |
| `claude rm <id>` | Remove it from the list (and its worktree when safe); the transcript stays for `--resume` |

## Commands this node introduces

`claude agents`, `claude agents --json --all`, `claude respawn`, and `claude rm`.
