---
type: lesson
title: "The /design canvas"
minutes: 11
---

To mock up a UI, a screen flow, a landing page or a poster, rather than build a working page, run `/design` with a brief:

```text
/design a settings screen for a mobile banking app
/design a three-step onboarding flow for a CLI tool, light and dark variants
```

> "Claude drafts the design as artboards on one canvas and publishes the canvas as a Claude Design artifact."

- Open it in a desktop browser, **select an element to edit it** (changes save automatically), and **export each artboard as PNG or PDF**.
- It needs Claude Code v2.1.265 or later, a session where artifacts are available, and the **Design** template turned on. Templates are on by default on Pro, Max and Team; Enterprise Owners enable them under Organization settings > Artifacts. It's Anthropic API only.
- `/slides` does the same for a deck. Claude Docs is available as a connector.
- `/design consent` and `/design revoke` grant or withdraw Claude's access to Claude Design. `/design-sync` converts a repo's React design system and uploads it to Claude Design, so mockups use your real components. Authorize it first with `/design-login`.

## Where it fits

```text
/design (explore layouts, agree on a direction)  →  build the real UI in code  →  publish a live artifact for review  →  Claude in Chrome / tests to verify
```

Mockups are cheap to throw away, so explore two or three directions on the canvas before any code exists. Then implement the chosen one, with the canvas open as the reference.

## Commands this node introduces

`/design [brief]`, artboards, PNG and PDF export, the Design template, `/slides`, `/design consent`, `/design revoke`, `/design-sync`, and `/design-login`.
