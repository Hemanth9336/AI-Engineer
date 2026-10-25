---
type: lesson
title: "What the Agent SDK is and how to install it"
minutes: 14
---

Every topic so far drove the agent through the `claude` binary: interactively, or headless with `claude -p`. The **Claude Agent SDK** gives you the same agent loop as a library. It has the same tools, permissions, hooks, MCP servers, subagents and sessions, but you control them from Python or TypeScript code instead of shell flags.

## When to reach for it

| You want | Use |
|---|---|
| A one-off headless step in a script or CI job | `claude -p ... --output-format json` (topic 053) |
| Your own program that embeds an agent: a service, a bot, an internal tool | **Agent SDK** |
| Tools written in your own language, running in your process | **Agent SDK** (`@tool`, in topic 060) |
| A decision in code on every tool call (allow, deny, or rewrite the input) | **Agent SDK** (`can_use_tool` and hooks, in topic 060) |
| Raw model calls with no agent loop, no tools, and no files | The Claude API client SDK (`anthropic`), not the Agent SDK |

The Agent SDK is *not* the plain API client. Calling `query()` starts a full Claude Code agent that can read files, run commands and loop until the task is done. That's why everything you learned about permissions still applies.

## Installing it

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install claude-agent-sdk          # Python 3.10+; ships with a bundled Claude Code CLI
python3 -c "import claude_agent_sdk as s; print(s.__version__)"

npm install @anthropic-ai/claude-agent-sdk   # the TypeScript package, same concepts
```

The Python package bundles its own copy of the Claude Code CLI and runs it as a subprocess, so you don't need a separate install. To use a specific binary instead, pass `ClaudeAgentOptions(cli_path=...)`.

## Authentication and configuration

The SDK reads the same environment the CLI does: `ANTHROPIC_API_KEY`, or a gateway via `ANTHROPIC_BASE_URL` plus `ANTHROPIC_AUTH_TOKEN`, or the Bedrock and Vertex switches in topic 071. Keep keys in the environment or a secret manager, never in the script.

Two defaults differ from the CLI, and both catch people out:

| Default | CLI | SDK | To get CLI behaviour |
|---|---|---|---|
| System prompt | The full Claude Code prompt | A minimal one | `system_prompt={"type": "preset", "preset": "claude_code"}` (add `"append": "..."` for your own rules) |
| Filesystem settings (`CLAUDE.md`, `.claude/settings.json`, skills, project commands) | Loaded | **Not loaded** | `setting_sources=["project"]` (or `"user"`, `"local"`) |

That second default is deliberate. A service that embeds an agent shouldn't silently pick up whatever `CLAUDE.md` or permission rules happen to be on the machine where it runs.

> **This lab VM:** `claude-agent-sdk` is already installed in the lab Python, and it's wired to the lab gateway like `claude` is.

## Commands this node introduces

`pip install claude-agent-sdk`, `npm install @anthropic-ai/claude-agent-sdk`, `cli_path`, `system_prompt` presets, and `setting_sources`.
