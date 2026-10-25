---
type: lesson
title: "QA and debugging workflows worth the browser"
minutes: 14
---

Handing an agent your logged-in browser is a real trust decision, so use it where it clearly pays:

| Workflow | Example prompt |
|---|---|
| **Live debugging** | "Open localhost:3000/dashboard, read the console errors, and fix the cause in src/" |
| **Form and flow testing** | "Test the signup form on localhost:3000 with an empty email, a bad email, and a valid one; report what each shows" |
| **Design verification** | "Compare the settings page with this mock and list every difference in spacing and colour" |
| **Visual regressions** | "Screenshot the pricing page before and after my change and describe what moved" |
| **Authenticated apps without an API** | "Draft the release summary into this Google Doc" |
| **Data extraction** | "Extract the listings on this page into listings.csv" |
| **Recording a repro** | "Record a GIF of the checkout bug" |

## Rules of thumb

1. **Prefer localhost and staging.** Debugging your own app is the sweet spot. Acting on production SaaS as you is the risky end.
2. **Use a dedicated browser profile** for agent work, signed in only to what the task needs (see the scenario below).
3. **Keep Manual mode** for sites with irreversible actions. Claude won't buy things or create accounts without you, but don't rely on that alone.
4. **Close the loop in code:** after it finds a bug in the browser, have Claude write a test that reproduces it, so the fix doesn't depend on a browser run.
5. **Watch context.** Browser tools and screenshots are large. Don't leave Enabled by default on for sessions that never need a browser.

The Desktop app's built-in browser pane uses a **clean profile** with none of your logins (topic 079). It's the safer choice for testing your own app.

## Commands this node introduces

Live debugging, form testing, design verification, GIF repros, a dedicated browser profile, and browser findings turned into tests.
