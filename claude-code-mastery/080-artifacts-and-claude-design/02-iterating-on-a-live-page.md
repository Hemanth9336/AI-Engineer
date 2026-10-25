---
type: lesson
title: "Iterating on a live page"
minutes: 11
---

## The same URL, new versions

Ask for changes ("add a filter by team", "make the chart weekly") and Claude edits the underlying file and **republishes to the same URL**. Anyone with the page open sees the update in place. Each publish is a version, and **Share** chooses which version viewers see. That's how you keep iterating without showing half-done states.

- **From another session**, give Claude the artifact's URL, or attach it with `/artifacts`. Otherwise a new session creates a new artifact.
- **Anchors** such as `#overview` link to a specific view of a page.
- **Comments**: people you share with inside your organization can comment. **Send to Claude** or `@claude` in a comment can trigger the session to respond and update, up to 60 activations per artifact per hour.

## Sharing

| Audience | How | Notes |
|---|---|---|
| Only you | The default | |
| Specific people, or everyone in your organization | **Share** (Team and Enterprise) | Viewers sign in. You can make someone an **editor** who can republish |
| Anyone with the link | Public | On Team and Enterprise, off until an Owner enables **External sharing**. Public viewers see "Content is user-generated and unverified." |

## Page constraints

- A strict content security policy. Scripts come only from a short list of CDNs (cdnjs, jsDelivr, Tailwind, jQuery, unpkg), fonts from Google Fonts, and network calls go only to the page's own origin.
- At most 16 MiB rendered. Relative links don't resolve, because it's one page.
- Claude asks before publishing in plan mode, before adding runtime capabilities, and before changing a public artifact.

## Commands this node introduces

Republishing to the same URL, versions and **Share**, attaching with `/artifacts`, comments with **Send to Claude**, editors, **External sharing**, and the page's content security policy.
