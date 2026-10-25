---
type: lesson
title: "What to put in CLAUDE.md"
minutes: 6
---

A good CLAUDE.md is short and specific. Everything in it costs context on every request, and a wall of generic advice gets skimmed by models just like by people.

## Put in

| Section | What | Example |
|---|---|---|
| **Commands** | How to build, test, lint, run one test | `./scripts/test.sh`, `python3 -m unittest tests.test_invoice` |
| **Conventions** | Rules Claude can't infer from the code | "Money is integer cents, never floats" |
| **Do not** | Things that look reasonable but are wrong here | "Never edit `migrations/` - add a new migration" |
| **Map** | Where things live, if not obvious | "API handlers in `app/routes/`, business logic in `app/core/`" |
| **Gotchas** | Traps you've fallen into | "Integration tests need `docker compose up -d db` first" |

## Leave out

- **Generic advice** - "write clean code", "add helpful error messages". Claude does that anyway; it's noise.
- **Things the code already says** - a list of every file, every function signature.
- **Secrets** - keys, passwords, internal URLs with tokens. CLAUDE.md is committed and sent to the model.
- **Long documents** - link them with `@docs/thing.md` instead of pasting.
- **Rules that must be enforced** - write them here *and* as permissions or hooks.

## Write it like a note to a new teammate

```markdown
## Commands
- Run all tests: `./scripts/test.sh`

## Conventions
- Money is always integer cents, never floats.

## Do not
- Never edit files in `migrations/` - add a new numbered migration.
```

Short bullets, real commands in backticks, one fact per line. For a rule that matters a lot, it's fine to say so: "IMPORTANT: ...".

## Keep it alive

- When Claude makes the **same mistake twice**, that's a missing line in CLAUDE.md.
- When a command changes, update the file in the same commit.
- Review it like code - it's shared instructions for every teammate's agent.
- Aim for something you could read in a minute. If it's growing past a page, move detail into linked docs.
