---
type: lesson
title: "Teleporting a cloud session back to your terminal"
minutes: 14
---

```bash
claude --teleport                 # pick from your cloud sessions
claude --teleport <session-id>    # a specific one
/teleport   (or /tp)              # the same picker from inside a session; in /tasks, press t
```

**What teleport brings home:** Claude checks you're in the right repository, **fetches and checks out the session's branch**, and **loads the full conversation history** into your terminal. You continue exactly where the cloud session was.

| Requirement | Why |
|---|---|
| A clean git state (you're offered a stash) | The branch is checked out over your working tree |
| The same repository, not a fork | The branch lives on that remote |
| The cloud branch is pushed | Teleport fetches it |
| The same claude.ai account | It's your session |

- The terminal gets **its own copy**. New work there stays local and doesn't appear in the cloud session. To keep steering from your phone afterwards, start `/remote-control` locally.
- `--resume` reopens *local* history and doesn't list cloud sessions. `--teleport` is for cloud sessions.
- Teleport needs claude.ai subscription authentication. With an API key, `/login` first.

## The round trip

```text
desk:   git push && claude --cloud "Get the integration tests green on this branch"
phone:  check progress, answer a question, approve
desk:   claude --teleport <id>      # branch + conversation, continue locally with your tools
```

## Commands this node introduces

`claude --teleport [session-id]`, `/teleport` (`/tp`), `t` in `/tasks`, and the difference between `--teleport` and `--resume`.
