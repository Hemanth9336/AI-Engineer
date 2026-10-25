---
type: lesson
title: "The six permission modes"
minutes: 12
---

A **permission mode** sets the baseline: what Claude may do without asking. Rules (next lesson) then pre-approve or block specific tools on top of it.

| Mode | What runs without asking | Use it for |
|---|---|---|
| `default` (shown as **Manual**) | Reads only | Sensitive work, unfamiliar code, reviewing every step |
| `acceptEdits` | Reads, file edits, and common filesystem commands in the working folder | Iterating on code you are watching |
| `plan` | Reads (plus classifier-approved commands where auto mode is available); edits wait for an approved plan | Exploring before changing anything |
| `auto` | Everything, with a classifier model reviewing each action in the background | Long tasks where prompts would interrupt you constantly |
| `dontAsk` | Reads in the working folders and pre-approved tools; anything that would prompt is **denied** | CI and scripts with an exact allowlist |
| `bypassPermissions` | Everything | Disposable containers and VMs only |

## Which mode you start in

1. The `--permission-mode` flag (or `--dangerously-skip-permissions`)
2. `permissions.defaultMode` in a settings file
3. The built-in default: since v2.1.283, interactive terminal sessions start in **auto** where auto mode is available (it needs a supported model and can be turned off by your organization), otherwise in Manual; `claude -p` and the Agent SDK start in **Manual**.

In the console, **Shift+Tab** cycles through the modes, and the status bar shows the active one (for example `⏵⏵ accept edits on`).

## Things no mode waves through

- Explicit **ask** rules always prompt; **deny** rules block in every mode, including `bypassPermissions`.
- Writes to protected paths (`.git`, `.vscode`, `.husky`, most of `.claude`, ...) are never auto-approved outside `bypassPermissions`.
- Recognized `rm`/`rmdir` of critical paths always go through the regular permission flow.

## Choosing

Pick the mode for the **risk of the work**, not the speed of the demo. Unfamiliar repo: Manual or plan. Your own feature branch: acceptEdits. A pipeline: dontAsk with an exact allowlist. `bypassPermissions` belongs inside something you can throw away.

## Commands this node introduces

`--permission-mode <mode>` picks the mode at launch; Shift+Tab switches it in the console.
