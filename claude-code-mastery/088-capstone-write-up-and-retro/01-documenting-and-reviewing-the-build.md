---
type: lesson
title: "Documenting and reviewing the build"
minutes: 19
---

A tool nobody can operate is a liability. Finish with two documents: a **README** for whoever runs it next, and a **retro** for whoever builds the next version (probably you).

## The README

| Section | Answers |
|---|---|
| **What it does** | In four bullets: what goes in and what comes out |
| **Quick start** | The exact commands, in a code block, that work from a fresh clone |
| **Components** | Every file, its kind (script, agent, hook), and its job. This mirrors the design doc, now with real paths |
| **Guardrails** | What agents can't do and how that's enforced (tools lists, the guard, verdict precedence) |
| **Operating it** | Where the logs are, how to read them, how to restart the API |
| **Limitations** | What it doesn't do. This is the section that saves your colleagues an afternoon |

**Every path in the README must exist.** Stale docs that name deleted files are worse than no docs, so check them mechanically.

## The retro

Write it while the details are fresh, and be specific:

- **What worked:** decisions you'd repeat, with the evidence ("the guard blocked a push during the regression fix").
- **What didn't:** bugs and wrong turns, and what found them ("a hidden test repo exposed missing scopes").
- **What I'd change next:** concrete, ranked changes, not "improve quality".
- **Numbers:** tests, components, guard patterns, red-to-green attempts, cost per run from the envelopes. Numbers make the next retro comparable.

## Review against the spec

Re-open `SPEC.md` and tick each **Done means** item only if you can show the command or file that proves it. Anything you can't tick goes into the retro's "what I'd change next". That closes the loop the course started with: specs, verification, and honest reporting.

## Commands this node introduces

README sections, a mechanical check that documented paths exist, the retro's four sections, and reviewing the build against the spec's done-criteria.
