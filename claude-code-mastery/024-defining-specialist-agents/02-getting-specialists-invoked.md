---
type: lesson
title: "Getting specialists invoked"
minutes: 14
---

Defining an agent does not mean it gets used. There are three ways in.

## 1. Automatic delegation

Claude compares the task to every agent's `description`. Descriptions that work:

- **Say when**, in the words of real requests: "Use after changes to auth, payments, or SQL".
- **Say proactively** if it should run without being asked: "Use proactively after any change to src/auth/".
- **Are specific**: "Reviews Terraform plans for public S3 buckets" beats "Helps with infrastructure".

## 2. Ask for it by name

```bash
claude -p "Use the security-reviewer agent to review src/auth.py"
```

In the console you can also `@`-mention the agent. Naming it is the reliable path in scripts.

## 3. Make it the main agent

```bash
claude -p --agent security-reviewer "Review src/auth.py"
```

The whole session runs as that agent, with its prompt and **its tool restrictions**. Set `"agent": "security-reviewer"` in settings to make it the default for a project.

## When the specialist never gets picked

| Cause | Fix |
|---|---|
| Vague description | Rewrite it around concrete triggers |
| The file is in `.claude/agent/` or has no frontmatter | `.claude/agents/<name>.md`, `---` on line 1 |
| Missing `name` or `description` | Both are required; the file is skipped otherwise |
| Another agent's description matches better | Make the triggers distinct |
| The main agent can do it itself cheaply | Ask by name, or make delegation part of the instructions |

## Commands this node introduces

`claude --agent <name>` and the `agent` setting run a specialist as the main agent.
