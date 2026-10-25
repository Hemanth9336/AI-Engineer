---
type: lesson
title: "Comparing your loop to a production loop"
minutes: 8
---

Put your topic 7-33 harness next to Claude Code and the differences are mostly **depth**, not kind.

| Concern | Your harness | Claude Code |
|---|---|---|
| Loop | `for step in range(max_steps)` | Same loop; `--max-turns`, interrupts, background tasks |
| Stop | Text-only reply or step limit | Same, plus user interrupt and budget limits |
| Tools | 2-5 hand-written schemas | ~20 built-ins + MCP servers; very long descriptions |
| Results | Trimmed and capped (topic 13) | Line-numbered reads, truncated outputs, pagination |
| Errors | Returned as text (topic 9) | Returned as `tool_result` with `is_error: true` |
| Permissions | Allowlist + approval prompt (topics 15, 21) | Modes, allow/deny rules per tool and pattern, managed policy |
| Sandbox | Workdir checks in tool code (topic 22) | Working-directory limits, optional OS sandbox for Bash |
| Context | System prompt + compaction + notes file | System prompt, CLAUDE.md hierarchy, auto-compaction, memory |
| Subagents | `delegate` tool (topic 25) | `Task` tool with named agent types |
| Extensibility | Edit the code | MCP servers, hooks, skills, settings files - no code changes |
| Observability | `transcripts/<id>.jsonl` (topic 31) | stream-json events, session transcripts, cost per run |

## What production adds

1. **Extension points instead of edits.** You change your harness by editing `agent.py`. Claude Code users change behavior through MCP (new tools), hooks (code around tool calls), CLAUDE.md (instructions) and skills (packaged workflows) - the next three topics.
2. **Layered configuration.** Enterprise policy, then user settings, then project settings, then the command line. A company can forbid `Bash(curl:*)` everywhere, and no project file can re-allow it.
3. **Defaults for the unhappy path.** Denials explain themselves, long outputs are truncated with a note, and a stuck command times out.

## What stays your job

Even with a production harness, **you** still decide what it may touch, which tools it gets, what instructions it follows, and how you'll know it worked. The rest of this phase is about doing that through Claude Code's extension points - and topic 38 is about when to build your own instead.
