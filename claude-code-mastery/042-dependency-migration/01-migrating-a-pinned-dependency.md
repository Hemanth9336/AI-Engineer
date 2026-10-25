---
type: lesson
title: "Migrating a pinned dependency"
minutes: 19
---

A major-version upgrade is a perfect agent job: tedious, mechanical, and checkable, as long as you supply the two things the agent cannot invent: **the release notes** and **a way to prove nothing changed**.

## The order that works

1. **Green on the old version.** Run the tests. If they are red before you start, you can't tell what the upgrade broke.
2. **Capture behavior.** Save golden output for realistic inputs: a rendered page, an API response, a report. Tests cover what someone thought of; golden output covers what the app actually does.
3. **Read the release notes.** List every breaking change, and grep the code for each affected API.
4. **Swap the version.** Update the pin (`requirements.txt`, the vendored copy, the lockfile) and nothing else. Run the tests and **save the failures**: they are your to-do list.
5. **Migrate call sites.** Give Claude the release notes and the failures. One change per breaking item, no drive-by refactors.
6. **Prove it.** Tests green, golden output byte-identical, and a grep shows no removed API remains.
7. **Write it down.** A short `MIGRATION.md` lists each breaking change and where it was handled, for the reviewer and the next upgrade.

## Prompting the migration

```text
We upgraded markdownlite from 1.4.2 to 2.0.0. vendor/markdownlite/RELEASE_NOTES.md lists the breaking changes.
Update app/docs.py to the 2.x API. Change only what the release notes require, then run the tests.
```

Pointing at the notes beats "upgrade to v2": the model's memory of a library's API is often a version behind, and the notes are the source of truth.

## When the golden output differs

Either the migration is wrong, or the new version changed behavior on purpose (the notes say so). Decide which, explicitly. Never regenerate the golden file just to make the diff go away.

## Commands this node introduces

Golden output, `diff` against it, and the green, capture, swap, migrate, prove order.
