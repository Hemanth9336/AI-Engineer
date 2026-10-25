---
type: lesson
title: "What artifacts are"
minutes: 10
---

> "An artifact is a live, interactive web page that Claude Code publishes from your session to a private URL on claude.ai. You open it in a browser, and it updates in place as the session continues."

- It's **one self-contained page** (HTML or Markdown) with no backend and no extra routes.
- Claude may publish on its own when a page is the best answer (a dashboard, a report, a chart), or you ask: "publish this as an artifact".
- The page is **private to you** until you share it. The URL looks like `https://claude.ai/code/artifact/...`, and the gallery is at `claude.ai/code/artifacts`.
- `Ctrl+]` reopens the latest one, and `/artifacts` lists them. In the list, Enter attaches one to the conversation, `o` opens it, `c` copies the link, and `d` deletes it.

## Availability

| Requirement | Detail |
|---|---|
| Plan and auth | Pro, Max, Team or Enterprise, signed in with claude.ai. API keys, gateway tokens and cloud-provider credentials can't publish |
| Provider | The Anthropic API (not Bedrock, Agent Platform or Foundry) |
| Organization | Not CMEK, HIPAA or ZDR. Team and Enterprise have an **Artifacts** toggle (on by default) |
| Surface | The CLI and Desktop. **Off by default** in `-p`, the Agent SDK, GitHub Actions, and with `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` |

Turn artifacts off with `"enableArtifact": false` (in `/config` or settings), `CLAUDE_CODE_DISABLE_ARTIFACT=1`, or a deny rule on the `Artifact` tool. Once managed settings or the env var turn them off, no settings file turns them back on.

## Commands this node introduces

Artifacts, `Ctrl+]`, `/artifacts`, `claude.ai/code/artifacts`, `enableArtifact`, and `CLAUDE_CODE_DISABLE_ARTIFACT`.
