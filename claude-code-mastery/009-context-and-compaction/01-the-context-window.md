---
type: lesson
title: "The context window"
minutes: 14
---

Everything the model knows about your session lives in one **context window**: a fixed budget of tokens that is rebuilt and sent on every turn of the loop.

## What fills it

| Loaded | When |
|---|---|
| System prompt, tool definitions, skill descriptions | Before you type anything |
| `CLAUDE.md` files from the working folder and its parents, plus auto memory's `MEMORY.md` index | At startup |
| Your prompts and the model's replies | Every turn |
| **Tool results** - every file read, every command's output | Every tool call |

Tool results are usually the biggest part. Reading a 2,000-line file or running a chatty test suite can cost more context than an hour of conversation.

## Seeing it

In the console, `/context` draws a coloured grid of what is using the window - system prompt, tools, memory files, messages - with suggestions when something is bloated. In a headless run, `usage` in the JSON envelope shows the tokens for the run.

## Why a full window hurts before it is full

As the window fills, early details compete with recent ones, and answers get vaguer about decisions made an hour ago. Claude Code does not stop you at the limit (it compacts, next lesson), but quality usually drops before that.

## Keeping it lean

- Start a **new session for a new task** (`/clear` keeps project memory and drops the conversation).
- Ask for focused reads: "read the `apply_discount` function", not "read the whole package".
- Pipe noisy commands through `tail` or `grep` in the prompt: "run the tests and show only failures".
- Delegate broad searches to a subagent (topic 049) so only the summary lands in your window.

## Commands this node introduces

`/context` shows what fills the window; `/clear` starts a new conversation and keeps project memory.
