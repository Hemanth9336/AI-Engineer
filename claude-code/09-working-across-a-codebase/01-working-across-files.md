---
type: lesson
title: "Working across files"
minutes: 8
---

Real changes rarely live in one file. A renamed function has callers, a new field needs a migration, a handler and a test. Claude Code works on the **whole repository** from the folder you start in - finding what's relevant, reading it, and making coordinated edits.

## How Claude finds its way around

Claude doesn't load the whole repo into context - that would fill the window in seconds. It explores like you would:

| Step | How |
|---|---|
| Get the layout | List directories, read the README and CLAUDE.md |
| Find things | Search with `grep`/`rg` through Bash, or glob for file names |
| Read selectively | Open the files (or line ranges) that matter |
| Delegate big searches | Hand a broad sweep to a read-only **Explore** subagent, which returns only the answer |

You'll see these steps as tool calls. If it's searching in the wrong place, interrupt and point it: "the handlers are in `app/routes/`".

## Ask before you change

Questions are cheap and teach you the codebase:

- "Where is the discount applied at checkout?"
- "Which files call `get_usr`? Paths only."
- "Trace what happens when a password reset email is sent."
- "What would break if I removed `legacy_auth.py`?"

Answers come with file paths, so you can check them.

## Coordinated edits

For a change that spans files, say what "everywhere" means:

> Rename `get_usr` to `get_user` everywhere - definition, imports, calls and tests. Then run the tests.

Claude finds every use, edits each file, and runs the tests. Being explicit about "imports and tests" matters: those are the places a quick search-and-replace misses, like `users.get_usr(...)` through a module import.

## Reviewing a multi-file change

```bash
git diff --stat          # which files changed, how much
git diff                 # the actual changes
grep -rn get_usr .       # nothing left behind?
```

Then the test suite. For mechanical changes, a clean `--stat`, an empty leftover search and green tests are strong evidence. For varied changes, read each file's diff.

## Keep the scope where you want it

- Start Claude in the project folder, not above it, so it can't wander into other repos.
- Mention what's out of bounds: "don't touch `vendor/` or the generated `api_client/`".
- For very large repos, add a short **map** to CLAUDE.md so exploration starts in the right place.
