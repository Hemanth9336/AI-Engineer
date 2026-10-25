---
type: lesson
title: "Session control and SDK subagents"
minutes: 12
---

## Sessions

Every run is a session with an id: `ResultMessage.session_id`, also in the first `SystemMessage`. The transcript is saved under `~/.claude/projects/` like a CLI session.

| You want | Option | Session id afterwards |
|---|---|---|
| Continue a specific conversation later, even from another process | `resume=session_id` | The same id |
| Branch off an earlier conversation without changing it | `resume=session_id, fork_session=True` | A new id |
| Continue the most recent session in this folder | `continue_conversation=True` | The same id |
| Several turns in one live process, with interrupts | `ClaudeSDKClient` | One id for the whole client |

```python
from claude_agent_sdk import ClaudeSDKClient

async with ClaudeSDKClient(options=opts) as client:
    await client.query("List my running jobs.")
    async for m in client.receive_response():      # stops after this turn's ResultMessage
        ...
    await client.query("Cancel the oldest one.")     # same session, full context
    async for m in client.receive_response():
        ...
```

Use `query()` for one-shot tasks. Use `ClaudeSDKClient` when your program holds a conversation: a chat backend, or a REPL. It also gives you `interrupt()` to stop a run that's going wrong. To store a session id per user and pick it up on the next request, use `resume`.

`list_sessions()` and `get_session_messages(session_id)` read saved sessions back, which is useful for support tooling and audits.

## Subagents in code

```python
from claude_agent_sdk import AgentDefinition

opts = ClaudeAgentOptions(
    allowed_tools=["Agent"],
    agents={"log-reader": AgentDefinition(
        description="Reads job logs and returns the failing step. Use for any 'why did job X fail' question.",
        prompt="You read logs. Reply with the failing step and the first error line only.",
        tools=["Read", "Grep"], model="haiku")},
)
```

These are the same subagents as in topic 024, defined in code instead of `.claude/agents/*.md`: an isolated context, a restricted tool list and a cheaper model. Your `can_use_tool` and hooks also see the calls a subagent makes, so one gate covers the whole tree.

## Commands this node introduces

`resume`, `fork_session`, `continue_conversation`, `ClaudeSDKClient`, `receive_response`, `interrupt`, `list_sessions`, `get_session_messages`, and `AgentDefinition`.
