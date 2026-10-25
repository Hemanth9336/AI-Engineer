---
type: lesson
title: "The diagnostic baseline"
minutes: 12
---

When Claude Code misbehaves - it stops finding files, a hook stops firing, updates fail - the first question is always "what changed?". You can only answer that if you wrote down what *normal* looked like. That record is a **diagnostic baseline**.

## What goes in a baseline

A baseline is a handful of facts that describe the installation, in a stable `key: value` format you can diff:

```text
version: 2.1.310
running: native (2.1.310)
search: OK (bundled)
auto-updates: enabled
```

| Fact | Why it matters later |
|---|---|
| Version | Behaviour changes between releases; bug reports need it |
| Install method and running version | Two installs on one machine is a classic source of "it worked yesterday" |
| Search backend | Search, `@file` mentions, custom agents, and skills all depend on ripgrep |
| Auto-updates | Explains why a version changed under you - or why it never did |

## Make it a script, not a screenshot

A baseline you copy by hand drifts. A script produces the same shape every time, so tomorrow's output can be compared with today's using plain `diff`:

```bash
./baseline.sh > baseline.txt          # today, when everything works
./baseline.sh > now.txt && diff baseline.txt now.txt   # the day something breaks
```

A good baseline script does one more thing: it **fails loudly** when two of its own facts disagree. If `claude --version` and the diagnostics report different versions, something is already wrong, and an exit code of 1 is how a script says so.

## Commands this node introduces

`diff baseline.txt now.txt` shows exactly what changed between two baselines.
