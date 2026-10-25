---
type: lesson
title: "Reading claude doctor output"
minutes: 12
---

`claude doctor` prints read-only installation and settings diagnostics from your shell, without starting a session. It is the command to run when `claude` itself will not start, and the source of most of a baseline.

```bash
claude doctor
```

```text
Claude Code doctor

Running: native (2.1.310)
Commit: 0d2056ecf42d
Platform: linux-x64
Path: /root/.local/share/claude/versions/2.1.310
Config install method: native
Search: OK (bundled)
Auto-updates: enabled
Auto-update channel: latest
Last update attempt: none recorded

Remote Control
- ...

1 warning found
- ...
```

## The lines that matter most

| Line | Read it as |
|---|---|
| `Running: <method> (<version>)` | Which build answered, and how it was installed (`native`, `npm-global`, ...) |
| `Path:` | The binary that actually ran |
| `Search:` | `OK (bundled)` means the built-in ripgrep works; a path means a system ripgrep is in use |
| `Auto-updates:` | `enabled`, or `disabled` with the reason, such as an environment variable |
| Warnings | Settings files that failed validation, broken installs, missing permissions |

## Reconcile it with the version flag

`claude --version` and the `Running:` line should name the same version. When they disagree, two different binaries answered - typically an old npm install and a newer native one, with `PATH`, an alias, or a stale shell hash deciding which runs. `type -a claude` lists every candidate.

## doctor versus /doctor

`claude doctor` (shell) only reports. `/doctor` inside a session runs a fuller setup checkup - installation, settings, extensions, `CLAUDE.md` - and proposes fixes that Claude applies after you confirm. Older builds drew `claude doctor` as an interactive screen; current builds print the report and exit, which is what makes it scriptable.

## Commands this node introduces

`claude doctor` prints diagnostics; `type -a claude` lists every `claude` on your `PATH`.
