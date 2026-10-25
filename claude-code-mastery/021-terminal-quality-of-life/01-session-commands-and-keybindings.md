---
type: lesson
title: "Session commands and keybindings"
minutes: 10
---

Most of your time in Claude Code is spent at one prompt. A handful of commands and keys make that prompt much faster.

## Prefixes

| Type | Does |
|---|---|
| `/` at the start | Opens the command and skill menu |
| `!` at the start | Shell mode: runs the command directly, adds its output to the session, and Claude responds to it - `! git status` |
| `@` | File path autocomplete - `@src/billing.py` pulls the file into the prompt |

## Session commands you will use daily

| Command | Use |
|---|---|
| `/clear` | New conversation, same project memory |
| `/compact [focus]` | Summarize to free context |
| `/context` | See what fills the window |
| `/resume`, `/branch` | Return to, or fork, a conversation |
| `/rename <name>` | Name the session so you can `claude --resume <name>` later |
| `/btw <question>` | A side question that does not enter the conversation history |
| `/model`, `/effort` | Switch model or reasoning level |
| `/permissions`, `/memory`, `/config` | Inspect rules, instruction files, and settings |

## Keys worth memorizing

| Key | Action |
|---|---|
| `Esc` | Interrupt Claude mid-turn; it keeps the work done so far |
| `Esc Esc` (empty prompt) | Open the rewind menu |
| `Shift+Tab` | Cycle permission modes |
| `Ctrl+R` | Reverse-search your prompt history |
| `Ctrl+G` | Edit the prompt in your `$EDITOR` |
| `Ctrl+J` | Newline without sending (or `\` then Enter) |
| `Ctrl+O` | Transcript viewer: every tool call in detail |
| `Ctrl+B` | Send a running Bash command or agent to the background |
| `Ctrl+S` | Stash the prompt; press again on an empty prompt to restore it |
| `Ctrl+C` twice, `Ctrl+D` twice | Exit |

On macOS, the Option shortcuts (`Option+P` model picker, `Option+T` thinking) need "Option as Meta" in your terminal settings; `/terminal-setup` configures common terminals.

## Commands this node introduces

`!` shell mode, `@` file mentions, `/rename`, `/btw`, and `/terminal-setup`.
