---
type: lesson
title: "Claude Code and the agent loop"
minutes: 14
---

Claude Code is a coding agent that runs in your terminal. You give it a goal in plain language. It reads files, edits them, runs commands, and checks its own work until the goal is met or it needs your input. That loop is the difference between an agent and a chatbot: a chatbot answers, an agent acts.

```mermaid
flowchart LR
  G["Your goal"] --> C["Read context"]
  C --> A["Act with tools"]
  A --> K["Check the result"]
  K --> D{"Done?"}
  D -->|No| C
  D -->|Yes| R["You review"]
```

This course builds Claude Code mastery from the ground up. The first 18 topics cover the fundamentals: project instructions, permissions, tool use, headless runs. Almost every idea here also has a direct counterpart in Codex, OpenAI's terminal agent, and a comparison chapter later in the course maps the two side by side.

## What Claude Code can touch

The agent works from the folder you start it in. Everything it does goes through tools:

| Tool | What it does | Needs your approval? |
|---|---|---|
| Read, Grep, Glob | Inspect files and search code | No |
| Edit, Write | Change or create files | Yes, until you allow it |
| Bash | Run shell commands | Yes, until you allow it |

Reads are safe and free of prompts. Anything that changes the machine asks first. You will spend a whole hour on that permission system soon; for now the takeaway is that the agent is powerful but fenced.

> **Version note:** on Linux, macOS, and WSL, current Claude Code builds leave the separate Grep and Glob tools out of the default set. Claude searches with `grep` and `find` through Bash instead, and Bash runs that built-in set of read-only commands without asking. Topic 003 shows how to bring the dedicated search tools back.

## This lab VM

Claude Code is already installed here and wired to a lab model gateway, so there is no signup or login step. Check the install:

```bash
claude --version
```

The lab gateway serves three Claude model aliases you will use throughout the course: **haiku** (fast and cheap), **sonnet** (balanced), and **opus** (deepest reasoning). Model choice gets its own hour later.

## Commands this node introduces

`claude --version` prints the installed Claude Code version.
