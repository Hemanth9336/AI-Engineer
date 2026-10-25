---
type: lesson
title: "Automation recap"
minutes: 15
---

Topics 027-035 gave you every piece of a headless pipeline you can trust. Here they are in the order a pipeline uses them.

| Layer | Piece | Topic |
|---|---|---|
| Boundaries | `permissions.deny` for tools the job must never use; allow only what it needs | 030 |
| Guardrails | PreToolUse hooks for rules that permission patterns cannot express | 028, 029 |
| Audit | A PostToolUse hook logging every tool call with session and tool_use id | 027 |
| Data access | MCP servers scoped to the job, with path guards | 031-033 |
| The run | `claude -p` with `--allowedTools`, `--max-turns`, `--max-budget-usd` | 034 |
| The output | `--json-schema` and `structured_output` | 035 |
| The decision | A gate that reads the stream and fails closed | 035 |
| The record | One log line per run with subtype, session id, and outcome | 034 |

## One principle per layer

- **The agent proposes, the script disposes.** Let the agent produce structured data; let deterministic code render files, post messages, and decide exit codes.
- **Fail closed.** Missing, malformed, or contradictory output stops the pipeline and leaves the last good artifact in place.
- **Prove it with records.** If you cannot point at the session, the tool calls, and the gate decision for last night's run, you do not know what happened.

## Commands this node introduces

None - this node ties together the automation commands from topics 027-035.
