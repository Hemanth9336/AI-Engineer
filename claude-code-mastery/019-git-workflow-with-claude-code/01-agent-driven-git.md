---
type: lesson
title: "Agent-driven git"
minutes: 14
---

Claude Code is good at git because git is text: diffs, logs, and status output are exactly what a language model reads well.

## What it can do well

- **Read and explain**: "what changed on this branch since main?" (`git log main..`, `git diff main...`).
- **Write commit messages** from the staged diff - usually better than "fix stuff".
- **Stage selectively** and split mixed work into separate commits.
- **Resolve conflicts** by reading both sides.
- **Search history**: "when did we start rounding VAT up?" (`git log -S`, `git blame`).

## Permissions for git

`git status`, `git diff`, `git log`, and other read-only forms run without a prompt in every mode. Anything that changes the repository asks. A sensible headless setup:

```bash
claude -p "Commit the staged changes with a Conventional Commits message" \
  --allowedTools "Bash(git diff *)" "Bash(git commit *)"
```

and in project settings:

```json
{ "permissions": { "ask": ["Bash(git push *)"], "deny": ["Bash(git push --force *)", "Bash(git reset --hard *)"] } }
```

## Attribution

When Claude commits, it adds a `Co-Authored-By: Claude ...` trailer by default. Change or hide it with the `attribution.commit` setting (the older `includeCoAuthoredBy` is deprecated). Your team's policy decides whether AI-assisted commits are labelled.

## Staged versus everything

The cleanest pattern: **you** decide what is in the commit by staging it; the agent writes the message for exactly that (`git diff --cached`) and commits **only what is staged**. Tell it not to `git add -A` - otherwise scratch files and secrets ride along.

## Commands this node introduces

`git diff --cached` (what will be committed), `git log --oneline`, and the `attribution.commit` setting.
