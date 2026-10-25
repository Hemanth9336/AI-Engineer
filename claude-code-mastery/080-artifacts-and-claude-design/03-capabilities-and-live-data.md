---
type: lesson
title: "Capabilities and live data"
minutes: 11
---

A static page goes stale. **Runtime capabilities** let a published page fetch live data or offer downloads, under the *viewer's* control.

## Connectors

A page can call **connectors from your claude.ai account** (Pro, Max, Team or Enterprise), for example to pull current tickets or calendar data when someone opens it.

> "When a published page calls a connector, the call uses the account of the person viewing the page, not the account of the person who published it."

- The page never sees credentials. claude.ai makes the calls on its behalf, and each viewer approves first.
- Connector calls don't run for public-link viewers who aren't signed in, or for viewers outside your organization.
- **Local MCP servers** (`.mcp.json`) can feed data while Claude *builds* the page, but the published page can't call them.
- Organizations turn this on separately: **Enable artifact connectors** in Organization settings > Capabilities.

That viewer-scoped design means a shared dashboard shows each person only what *they* can access. It can't leak the publisher's data to colleagues who lack access.

## Downloads

A page can offer file downloads through a runtime control the viewer clicks. The artifact viewer blocks downloads the page starts on its own, including `data:` and `blob:` links.

## Choosing static vs live

| Use a static snapshot when | Use connectors when |
|---|---|
| The page records a moment: an incident report, a release summary, a benchmark | The page is a tool people revisit: a team dashboard, a queue view |
| Viewers outside the organization, or public | Viewers are signed-in colleagues with their own access |
| The numbers must not change after review | Freshness matters more than a frozen record |

## Commands this node introduces

Runtime capabilities, connector-backed pages, viewer-scoped calls, **Enable artifact connectors**, and viewer-initiated downloads.
