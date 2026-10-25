---
type: lesson
title: "The console: sessions, slash commands, and headless mode"
minutes: 14
---

Claude Code has two faces. The **interactive console** is where you converse, steer, and approve. **Headless mode** is a single command that runs one task and exits, which makes the agent scriptable.

## The interactive console

Start it from the folder you want the agent to work in:

```bash
cd /root
claude
```

Inside the console, plain text is a prompt for the agent. Lines starting with `/` are commands for the console itself:

| Command | What it does |
|---|---|
| `/help` | List available commands |
| `/model` | Show or switch the active model |
| `/clear` | Start a fresh conversation |
| `/exit` | Leave the console |

Type `/exit` (or press Ctrl+C twice) to leave. The conversation ends, but every file the agent created stays on disk. That is worth internalizing early: **the conversation is temporary, the artifacts are real.**

## Headless mode

The `-p` flag runs one prompt without opening the console and prints the result to stdout:

```bash
claude -p "Reply with one sentence: what directory are you running in?"
```

Because the reply lands on stdout, you can redirect it into a file like any other command output:

```bash
claude -p "your prompt" > answer.txt
```

You will use this constantly in the automation topics later in the course. For now it is the quickest way to prove the whole stack works: CLI, gateway, model, and your shell, in one line.

## Commands this node introduces

`claude` opens the console, `/help`, `/model`, `/clear`, and `/exit` work inside it, and `claude -p` with output redirection runs one task headless.
