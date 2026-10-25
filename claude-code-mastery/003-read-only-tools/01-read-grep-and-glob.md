---
type: lesson
title: "Read, Grep, and Glob"
minutes: 14
---

Before an agent changes anything, it has to find things. Claude Code has three kinds of read-only inspection:

| Tool | Finds | Example |
|---|---|---|
| **Read** | The contents of one file (with optional line range) | read `src/app/cli.py` lines 1-80 |
| **Glob** | Files by name pattern | `**/*.toml`, `tests/test_*.py` |
| **Grep** | Lines inside files, by regex (ripgrep syntax) | `def compute_` in `*.py` |

None of them changes the machine, so none of them prompts inside your working folder. Reads outside the folder (and any extra roots you grant) still ask.

## How search reaches the model today

On Linux, macOS, and WSL, Claude Code leaves the dedicated **Glob** and **Grep** tools out of the default tool set. Claude searches with `find` and `grep` through the **Bash** tool instead - they run embedded versions of `bfs` and `ugrep`, and Bash runs that built-in set of read-only commands without prompting. The searches show up in transcripts, hooks, and permission rules as `Bash` calls.

You get the dedicated tools back by naming them when you start the session:

```bash
claude -p "..." --allowedTools "Read Grep Glob"
```

Naming either one in `--allowedTools` (or listing exactly the tools you want with `--tools`) restores both. An allow rule in a settings file does **not** have this effect. Two behaviours worth knowing:

- **Grep** uses ripgrep regex syntax and skips files matched by `.gitignore`. `interface{}` has to be written `interface\{\}`.
- **Glob** does *not* respect `.gitignore` by default, so it also finds ignored files.

## Why restrict to read-only tools

For exploration you want an agent that can look everywhere and touch nothing. Naming only `Read Grep Glob` gives it fast, structured search, and every other tool still needs approval - which a headless run cannot give - so nothing gets edited by accident.

## Commands this node introduces

`--allowedTools "Read Grep Glob"` pre-approves the read-only trio and brings Grep and Glob into the session.
