---
type: lesson
title: "Sessions that message each other"
minutes: 14
---

Subagents (topic 024) live *inside* one session. Sometimes the work is spread across **separate sessions**: one terminal on the API, another on the docs, a background worker running tests. Claude Code lets those sessions talk.

## Cross-session messaging

- Claude finds other sessions with the `ListAgents` tool and sends plain text with `SendMessage`. You don't call these tools yourself. You ask ("tell the api-worker the schema changed"), or Claude sends on its own.
- **@-mentions:** type `@` plus the start of a session name (`@api-worker`, or `@"release notes"` for names with spaces) to address one.
- **Names:** `claude --name api-worker`, or `/rename`, set the name other sessions see. `/list-agents` (alias `/peers`) shows who's reachable. `/status` shows this session's inbox address.
- A message carries **text only**, never the sender's conversation or files. A path in a message attaches nothing; the receiver opens it with its own tools if it's allowed to.
- The receiver reads a message between tool calls (it never interrupts a running tool), or starts a new turn if it's idle.

## How messages travel

| Other session | Path |
|---|---|
| On this machine | A per-session Unix socket (or a named pipe on Windows), **never through Anthropic servers** |
| On another of your machines | Through Anthropic servers, over that machine's Remote Control connection (topic 075) |
| In the cloud | Through Anthropic servers to the cloud session |

## Controls

| Setting | Effect |
|---|---|
| `crossSessionInbound: "accept"` | Deliver incoming messages to Claude |
| `crossSessionInbound: "hold"` | Show a notice, and deliver only after you approve |
| `crossSessionInbound: "refuse"` | Drop them. A project or local `refuse` beats every other source |
| `isolatePeerMachines: true` | Require approval before any message leaves this machine, even in bypass mode |
| Deny `SendMessage` and `ListAgents` | An organization-wide off switch. This also cuts messaging to subagents and agent-team teammates, because they all use the same tool |

An incoming message **can't** approve your permission prompts, change your config, or run your slash commands. It arrives as text, and the receiver's own permissions still apply. Treat a peer message like any other untrusted input.

## Agent teams (experimental)

With `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`, an interactive lead session can spawn named **teammates** with a shared task list and a mailbox. Use `--teammate-mode` or the `teammateMode` setting for split panes in tmux or iTerm2. Teams need an interactive lead. In `-p` and the SDK, named agents run as ordinary subagents. Start with 3-5 teammates: the token cost scales with each one.

## Commands this node introduces

`SendMessage`, `ListAgents`, `@session-name`, `claude --name`, `/rename`, `/list-agents` (`/peers`), `crossSessionInbound`, `isolatePeerMachines`, and `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`.
