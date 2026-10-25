---
type: lesson
title: "Sending work to the cloud with --cloud"
minutes: 14
---

A **cloud session** runs Claude Code on an Anthropic-managed VM (or on your self-hosted runners, topic 072). It keeps running when you close your laptop. You can start one from claude.ai/code, the mobile app, Desktop, or the terminal.

```bash
claude --cloud "Fix the authentication bug in src/auth/login.ts"     # a new cloud session
claude -p "Also add a regression test" --cloud <session-id>         # post one follow-up message and exit
```

| Fact | Detail |
|---|---|
| What it works on | The VM clones **your GitHub remote at the current branch**, not your local checkout. **Push first**: local-only commits and uncommitted changes aren't in the session |
| One repo | `--cloud` works with a single repository at a time |
| No GitHub access | `claude --cloud` bundles and uploads your local repo instead (git with at least one commit; uncommitted credential-like files such as `.env` and `*.pem` are left out). `CCR_FORCE_BUNDLE=1` forces this |
| Follow-ups | `--cloud <session-id>` with `-p` posts a message and returns `{ok, session_id, url}` with `--output-format json`. It sends no local state |
| One-way from the terminal | You can pull a cloud session down with `--teleport`, but you can't push an existing terminal session up |
| Requirements | A claude.ai account on Pro, Max, Team or Enterprise (Enterprise with premium or Claude Code seats). Not on Bedrock, Agent Platform or Foundry. The organization's cloud sessions policy must be on. Not for ZDR, HIPAA or CMEK organizations |
| Billing | Counts toward plan usage. There's no separate charge for the VM |

`--remote` is the old spelling of `--cloud`. `--remote-control` is a different feature (topic 075).

## When it's the right tool

- Long tasks you don't need to watch: a migration, a test-suite fix loop, a dependency upgrade.
- Several tasks in parallel without tying up your machine.
- Starting work from your phone and picking it up at your desk.

## Commands this node introduces

`claude --cloud "<task>"`, `claude -p "<msg>" --cloud <session-id>`, `CCR_FORCE_BUNDLE`, and `/remote-env` (the default environment for `--cloud`).
