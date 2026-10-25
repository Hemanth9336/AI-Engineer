---
type: lesson
title: "Allow, ask, and deny rules in settings.json"
minutes: 12
---

Rules live under `permissions` in a settings file. Project rules that everyone shares go in `.claude/settings.json`:

```json
{
  "permissions": {
    "allow": ["Bash(python3 -m unittest *)", "Edit(/src/**)"],
    "ask":   ["Bash(git push *)"],
    "deny":  ["Read(./.env)", "Bash(curl *)"]
  }
}
```

## How a call is decided

Rules are evaluated **deny, then ask, then allow** - the first match in that order wins, and specificity does not change the order. A broad `deny` of `Bash(aws *)` blocks `aws s3 ls` even if you also allow exactly `Bash(aws s3 ls)`. Rules from every scope are collected before evaluation, so a user-level deny beats a project-level allow and vice versa.

## Rule syntax

| Rule | Matches |
|---|---|
| `Bash(npm test)` | exactly `npm test` |
| `Bash(git log *)` | `git log` and anything after it - the space before `*` is part of the rule |
| `Bash(ls*)` | also `lsof`, because there is no space |
| `Read(./.env)` | `.env` relative to the current directory |
| `Edit(/src/**)` | `src/` relative to the settings file's project |
| `Read(~/.ssh/**)` | under your home directory |
| `Read(//etc/**)` | an absolute path (note the double slash) |
| `WebFetch(domain:docs.python.org)` | fetches to one host |

A `Read` deny also covers Grep, Glob, and other file-reading tools for that path.

## Trust gates the allow rules

`permissions.allow` rules in a project's `.claude/settings.json` grant capability, so Claude Code applies them **only after you accept the workspace trust dialog** for that folder. Deny and ask rules apply immediately - they only restrict. Open `claude` in the folder once and answer **Yes** to "Do you trust the files in this folder?". On a machine with no console, the flag lives under `projects["<folder>"].hasTrustDialogAccepted` in `~/.claude.json`.

## Commands this node introduces

`/permissions` in the console lists every active rule and where it came from.
