---
type: lesson
title: "Coding assistants and AI inside your apps"
minutes: 6
---

Chat assistants live in their own window. A growing share of AI use happens somewhere else: inside your code editor, your terminal, and the office apps you already have open all day.

## Coding assistants

A **coding assistant** is an LLM pointed at your code. The main kinds:

- **In the editor.** GitHub Copilot, Cursor, and Windsurf suggest the next lines as you type, answer questions about the file you have open, and make multi-file edits when you ask.
- **In the terminal.** Claude Code, OpenAI Codex CLI, and Gemini CLI run as a command. You describe a change in plain English and the assistant reads files, runs commands, and edits code, asking before it does anything risky.
- **In code review.** Bots that comment on pull requests, explain a diff, or suggest a fix for a failing test.

This course uses **`claude`**, Claude Code's terminal command, in later topics, because it works on any Linux machine and shows clearly what an assistant is doing.

## AI inside everyday apps

Most office software now has an LLM built in:

| Where | What it does |
|---|---|
| Microsoft 365 Copilot | Drafts Word documents, summarizes Teams meetings, builds Excel formulas |
| Gemini in Google Workspace | Writes in Docs and Gmail, summarizes long email threads |
| Notion AI, Confluence, Slack AI | Summarizes pages and channels, answers questions about your workspace |
| Zoom and Teams | Meeting notes, action items, and catch-up summaries |

The pattern is always the same: the app sends your content plus an instruction to a model and shows the reply in place. The advantage is that the AI already has your context - the document, the thread, the meeting - so you do not have to paste it in.

## Agents

The newest kind of tool is the **agent**: an assistant that does not just answer but takes a series of actions to reach a goal - searching, clicking, running code, calling other tools. Coding assistants in the terminal are agents. You will build a small one yourself in topic 21.

Next: what all this costs, and how to choose.
