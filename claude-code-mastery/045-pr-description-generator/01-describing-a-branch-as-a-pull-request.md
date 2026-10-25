---
type: lesson
title: "Describing a branch as a pull request"
minutes: 19
---

A PR description answers four questions for the reviewer: what changed, why, how risky it is, and what to look at. The inputs are already in git; the job is to select the right ones and shape the answer.

## Two dots and three dots

`main` has usually moved on since you branched. The difference matters:

| Command | Shows |
|---|---|
| `git log main..HEAD` | Commits on your branch that are not on main: the right list of commits |
| `git diff main..HEAD` | The difference between the two **tips**, including main's newer changes, shown as if your branch reverted them |
| `git diff main...HEAD` | Changes since the **merge base**: only what your branch did. This is what GitHub shows in a PR |

Feed the model the **three-dot diff**. With two dots, a description of your rate limiter would also "remove" the maintainer line someone added to `main`'s README yesterday.

## Inputs and output

```bash
{ echo "## Commits"; git log --reverse --format='- %s' main..HEAD
  echo; echo "## Diff"; git diff main...HEAD; } \
  | claude -p "$(cat .prdesc/prompt.txt)" --tools "" --output-format json --json-schema "$(cat .prdesc/schema.json)"
```

Shape the output, then render it with code:

| Field | Constraint |
|---|---|
| `title` | At most 70 characters, no trailing period |
| `summary` | Why the change exists, two or three sentences |
| `changes` | A list, one item per logical change |
| `risk` | `low`, `medium`, or `high` |
| `labels` | Only from your repository's fixed set (`feature`, `bugfix`, `docs`, `tests`, `breaking`) |

Rendering in code means every PR has the same headings, and a made-up label never reaches GitHub. Then `gh pr create --title "..." --body-file PR.md` opens the PR.

## Large branches

A huge diff costs tokens and buries the signal. Send `git diff --stat main...HEAD` plus the diff of the most important files, or allow `Read` and let the agent open files itself.

## Commands this node introduces

`git log main..HEAD`, `git diff main...HEAD`, `git merge-base`, and `gh pr create --body-file`.
