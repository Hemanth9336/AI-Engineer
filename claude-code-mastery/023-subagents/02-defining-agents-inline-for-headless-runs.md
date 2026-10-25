---
type: lesson
title: "Defining agents inline for headless runs"
minutes: 14
---

For a script or a one-off fan-out you do not want to save a file. `--agents` defines subagents for **this session only**, as JSON:

```bash
claude -p "Map every service under services/ using one service-scout per service" \
  --agents '{
    "service-scout": {
      "description": "Reads one service folder and reports its port, owner, and entrypoint. Use one per service.",
      "prompt": "You inspect exactly one service folder. Reply with one line: name | port | owner | entrypoint.",
      "tools": ["Read", "Grep", "Glob"],
      "model": "haiku"
    }
  }'
```

In `-p` mode, `--agents` also accepts a **path to a JSON file** with the same object - easier to review and commit:

```bash
claude -p "..." --agents ./agents.json --permission-mode acceptEdits --output-format json
```

## The fields

| Field | Meaning |
|---|---|
| key (`service-scout`) | The agent's name - what `subagent_type` refers to |
| `description` | **When** to use it; Claude delegates based on this |
| `prompt` | The agent's system prompt |
| `tools` | Allowed tools; omit to inherit all. Leave out Edit, Write, and Bash for a read-only scout |
| `model` | `haiku`, `sonnet`, `opus`, `inherit`, or a full model id |

## Making the fan-out happen

Say it in the prompt: "use one service-scout subagent **per service**, then combine their lines into MAP.md". The main agent then issues one Agent call per service; without that instruction it may just read everything itself.

## Commands this node introduces

`--agents '<json>'` or `--agents ./agents.json` defines session-only subagents.
