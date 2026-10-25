---
type: lesson
title: "Permission rules, env, and statusLine"
minutes: 14
---

A project settings file is the team's contract with the agent. The three blocks you will write most:

## permissions

```json
"permissions": {
  "allow": ["Bash(python3 scripts/show_env.py)", "Bash(python3 -m unittest *)"],
  "ask":   ["Bash(git push *)"],
  "deny":  ["Read(./.env)", "Read(./secrets/**)"],
  "defaultMode": "default"
}
```

- Evaluation order: **deny** first, then **ask**, then **allow**. The first match decides.
- `ask` in a headless run means **refused** - nobody is there to answer.
- Paths: `x` or `./x` is relative to the current directory, `/x` to the settings source (the project root for project settings), `~/x` to home, `//x` absolute - `/Users/me/x` is **not** an absolute path.
- `Bash(...)` rules match each subcommand of `a && b`; `Read(...)` rules also stop Grep and Glob from reading the file.
- File-write rules are spelled `Edit(path)` and cover Write too. A `Write(path)` rule **never matches** - a classic silent mistake.
- Allow rules in project files apply only after the folder is **trusted**.

## env

```json
"env": { "APP_ENV": "test", "LOG_LEVEL": "info" }
```

Set for the whole session, including every Bash command and hook. Good for non-secret switches; secrets belong in your shell or a secrets manager, never in a committed file.

## statusLine and friends

```json
"statusLine": { "type": "command", "command": "jq -r '\"[030] \" + .model.display_name'" }
```

Other useful keys: `model`, `outputStyle`, `cleanupPeriodDays`, `additionalDirectories`, `enableAllProjectMcpServers`, and `hooks`.

## Commands this node introduces

`permissions.allow / ask / deny / defaultMode`, `env`, and `statusLine` in a project file.
