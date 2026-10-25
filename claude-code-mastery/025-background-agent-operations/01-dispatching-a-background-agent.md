---
type: lesson
title: "Dispatching a background agent"
minutes: 12
---

A **background session** is a full Claude Code session that runs without a terminal attached. You start it, go do something else, and check back.

```bash
claude --bg --name nightly-audit "Audit src/ for TODOs and write artifacts/report.md"
```

```text
backgrounded · 7c5dcf5d · nightly-audit
  claude agents             list sessions
  claude attach 7c5dcf5d    open in this terminal
  claude logs 7c5dcf5d      show recent output
  claude stop 7c5dcf5d      stop this session
```

- The prompt is the **positional argument**; `--bg` cannot be combined with `-p`.
- `--name` labels the session in agent view and lets `claude logs` and `claude attach` find it by name.
- `--agent <name>` runs one of your specialists as the session's main agent.
- `--permission-mode` and `--model` work as for any session. A `--bg` session otherwise starts the way a new interactive session in that folder would.
- The folder must be **trusted**; a script that cannot show the trust dialog gets an error instead.

Background sessions are hosted by a **supervisor** process (`claude daemon status`) that keeps them alive after your terminal closes.

## Isolation in git repositories

In a git repository, a background session moves into its own **worktree** under `.claude/worktrees/` before it edits anything, so parallel background sessions never write to your checkout. Outside git (or with `worktree.bgIsolation: "none"`), it edits the folder directly.

## Other ways in

- In a running session, press `←` on an empty prompt (or `/background`) to send it to the background.
- `/fork <prompt>` copies the session into a new background one.
- `claude agents` opens agent view, where you can type a prompt to dispatch a new session.

## Commands this node introduces

`claude --bg [--name] "<prompt>"`, `claude logs`, `claude attach`, `claude stop`, and `claude daemon status`.
