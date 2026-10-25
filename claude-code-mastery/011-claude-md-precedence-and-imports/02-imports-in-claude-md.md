---
type: lesson
title: "Imports in CLAUDE.md"
minutes: 14
---

Long instruction files are hard to maintain. An `@path` anywhere in a `CLAUDE.md` **imports** another file: its contents are expanded into context alongside the file that references it.

```markdown
# payments-utils
See @README.md for the project overview.

## Style
@docs/summary-style.md
```

## Rules of imports

- Relative paths resolve from **the file containing the import**, not the working folder.
- Imports can nest, up to **four hops** deep.
- Paths with spaces need backslashes: `@Design\ Docs/api.md`. A quoted path is not imported.
- Inside backticks or a code block, `@README` is literal text, not an import.
- An import that resolves **outside** the project (for example `@~/.claude/my-notes.md` in a project file) triggers a one-time approval dialog, because a teammate could commit an import of your private files.

## What imports are for

- **One source of truth.** The release team owns `docs/summary-style.md`; every repo that imports it stays in sync.
- **Organization.** A short `CLAUDE.md` index that imports topic files is easier to review.
- **Personal rules across worktrees.** A gitignored `CLAUDE.local.md` exists in one worktree only; importing `@~/.claude/my-project.md` shares it across all of them.

Imports organize; they do not save context. Imported files load in full at startup, the same as if pasted in. To load rules only when relevant, use a nested `CLAUDE.md` or `.claude/rules/` files with `paths:` frontmatter.

## Commands this node introduces

`/context` shows imported files as separate memory entries, which is how you confirm an import resolved.
