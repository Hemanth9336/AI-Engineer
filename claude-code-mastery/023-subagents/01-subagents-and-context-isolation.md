---
type: lesson
title: "Subagents and context isolation"
minutes: 14
---

A **subagent** is a helper Claude starts for a sub-task. It runs with **its own context window**, its own system prompt, and (optionally) its own tools and model. When it finishes, only its **final answer** returns to the main conversation.

```text
main conversation ──► Agent(subagent_type: "service-scout", prompt: "scout services/billing")
                         └─ subagent: reads 9 files, runs 4 searches (its own window)
                    ◄── "billing | 8101 | team-payments | services/billing/main.py"
```

## What that buys you

- **Context**: the main window receives one line instead of nine file reads. Long investigations stop crowding out your actual task.
- **Parallelism**: several subagents can work at once - one per service, per module, per hypothesis.
- **Constraints**: a subagent can be limited to read-only tools, so an exploration can never edit.
- **Cost**: routine scouting can run on a cheaper model (`model: haiku`) while the main conversation stays on a stronger one.

## Built-in subagents

Claude Code ships some: **Explore** (fast, read-only codebase search), **Plan** (research for plan mode), and a general-purpose agent. Claude delegates to them on its own when a task fits their description - in plan mode, the instructions explicitly favour launching Explore agents.

## What a subagent does not get

- Your conversation history - its prompt must stand on its own.
- Your auto memory (it can have its own).
- Explore and Plan also start without `CLAUDE.md`, to stay fast.

## Where the evidence lives

Each subagent's transcript is saved beside the main session: `~/.claude/projects/<project>/<session-id>/subagents/agent-<id>.jsonl`, with a `.meta.json` naming its `agentType`. That is how you verify a fan-out really happened.

## Commands this node introduces

`/agents` lists and manages subagents in the console; the `Agent` tool is how Claude starts one.
