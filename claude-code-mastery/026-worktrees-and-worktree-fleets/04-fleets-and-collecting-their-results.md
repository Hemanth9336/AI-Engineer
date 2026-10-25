---
type: lesson
title: "Fleets and collecting their results"
minutes: 10
---

A **fleet** is several agents working at once, each in its own worktree on its own branch, each on an independent task.

```bash
claude -p -w fix-tax   "$(cat tasks/fix-tax.md)"  --permission-mode acceptEdits --allowedTools "Bash(git *)" --output-format json > runs/fix-tax.json &
claude -p -w add-docs  "$(cat tasks/add-docs.md)" --permission-mode acceptEdits --allowedTools "Bash(git *)" --output-format json > runs/add-docs.json &
wait
```

## Rules for a fleet that stays reviewable

- **Independent tasks only.** Two agents changing the same function will produce a merge conflict, not a speed-up.
- **Each task ends with a commit on its branch** - tell it to commit; uncommitted work in a worktree is easy to lose.
- **Nothing touches `main`.** The main checkout stays clean and on its original commit.
- **Collect, then review.** Results are branches; review each like a pull request.

## Collecting

```bash
git worktree list
for b in worktree-fix-tax worktree-add-docs; do
  echo "## $b"; git log --oneline main.."$b"; git diff --stat main..."$b"
done > FLEET.md
```

Then merge what passes review (`git merge --no-ff worktree-fix-tax`), and remove the worktrees: `git worktree remove .claude/worktrees/fix-tax`, `git branch -d worktree-fix-tax`.

## Worktree or clone?

Use worktrees for parallel tasks in one repository on one machine. Use separate clones when tasks need **different remotes**, when you need the **same branch** twice, or when the work moves to another machine or container.

## Commands this node introduces

`&` and `wait` run headless agents in parallel; `git log main..<branch>` and `git diff --stat main...<branch>` summarize each branch.
