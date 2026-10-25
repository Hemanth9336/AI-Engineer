---
type: lesson
title: "The repo onboarding workflow"
minutes: 19
---

The first real job most people give a coding agent is "explain this codebase to me". Done well, it saves a new engineer days. Done carelessly, it produces a confident document full of commands that don't exist.

## Explore before you write

1. **Map the tree.** `Glob` for the layout, `Grep` for entry points (`if __name__`, `def main`, route tables, `Makefile` targets).
2. **Read the load-bearing files.** Config, entry point, routing, the build file, one representative test.
3. **Write from what was read.** Every fact in the document should trace back to a file Claude actually opened in this session.

In an interactive session, "use the Explore subagent to map this repo" keeps the exploration out of your main context. Headless, a read-only tool list (`Read`, `Glob`, `Grep`, plus `Write` for the one output file) is enough. On macOS and Linux, `Glob` and `Grep` are not in the default tool set (Claude searches with `find` and `grep` through Bash). Naming them in `--allowedTools` brings them back, which lets you leave Bash out entirely.

## Ask for verifiable facts

Vague prose can't be checked. Ask for facts in shapes a script can verify:

| Ask for | Verify by |
|---|---|
| Every environment variable with its default, as a table | Parse the config module and compare |
| Every HTTP route as `METHOD /path` | Compare with the route table |
| Commands as `make <target>` | Check the target exists in the Makefile |
| File paths in backticks | Check each path exists |
| "Where to start" pointing at real files | Same |

Then **run the check**. A document that passes is one you can hand to someone. A document that fails tells you exactly which sentence the agent invented.

## Keep it alive

Commit the document next to the code, and regenerate it when the code it describes changes. The same verification script can run in CI so the document never quietly goes stale.

## Commands this node introduces

Read-only tool lists for exploration, and the habit of asking for checkable facts: tables, `METHOD /path`, `make <target>`, real paths.
