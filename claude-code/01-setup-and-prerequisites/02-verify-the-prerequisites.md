---
type: task
title: "Verify the prerequisites"
minutes: 12
---

## Task: Prove the machine is ready

## Goal

Verify each prerequisite yourself and record the evidence in `/root/prereq-report.txt`. This is what "is Claude Code set up?" means on any machine, anywhere.

## Practice

Check each piece, appending what you find to the report:

```bash
node --version    >> /root/prereq-report.txt
command -v claude >> /root/prereq-report.txt
claude --version  >> /root/prereq-report.txt
```

One thing has to be true for Claude Code to run: the CLI itself, on a supported OS with a network. It is a native binary - it does not run on your Node. Node shows up here because the usual way to get the CLI is `npm install -g @anthropic-ai/claude-code`, and that npm package asks for Node 22 or newer; on an older Node, npm warns (`EBADENGINE`) and installs it anyway. So record the Node version as part of the picture, but do not treat it as a gate. On this VM the CLI is already in place and your Claude account is already signed in, so there is no key to paste. On your own laptop you would sign in once with `claude` and it remembers you after that.

## Expected Result

A report showing this machine's Node version, a path to `claude`, and the CLI version.

## Ready To Continue

Press **Submit** when all three checks pass.

<details><summary>Solution</summary>

```bash
node --version    >> /root/prereq-report.txt
command -v claude >> /root/prereq-report.txt
claude --version  >> /root/prereq-report.txt
cat /root/prereq-report.txt
```

</details>

## Check your work

```bash
R=/root/prereq-report.txt
if command -v node >/dev/null; then
  grep -qxF "$(node --version)" $R 2>/dev/null && echo "✅ the report records this machine's Node version ($(node --version))" || echo "❌ append the output of node --version to $R"
else
  [ -s $R ] && echo "✅ Node isn't installed here - that's fine, Claude Code doesn't need it" || echo "❌ create $R with the three commands above"
fi
grep -qxF "$(command -v claude)" $R 2>/dev/null && echo "✅ the report records where claude is installed ($(command -v claude))" || echo "❌ append the output of command -v claude to $R"
grep -qxF "$(claude --version 2>/dev/null)" $R 2>/dev/null && echo "✅ the report records the Claude Code version ($(claude --version 2>/dev/null))" || echo "❌ append the output of claude --version to $R"
```

## What you learned

- Claude Code is a native CLI; Node only matters if you install it through npm.
- `command -v claude` proves the CLI is on your `PATH`; `claude --version` proves it runs.
- Appending command output with `>>` builds a simple, checkable evidence file.

> **Your lab setup:** this VM comes with Claude Code preinstalled and signed in - just run `claude` to start. (Setting up your own machine? Follow step 7 of `setup/README.md` once.)
