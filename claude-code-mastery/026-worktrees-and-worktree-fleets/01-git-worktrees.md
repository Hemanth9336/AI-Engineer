---
type: lesson
title: "Git worktrees"
minutes: 10
---

A **worktree** is a second (third, tenth) working directory attached to the **same repository**, each on its own branch.

```bash
git worktree add ../app-fix-tax -b fix-tax      # new folder, new branch, same .git
git worktree list
git worktree remove ../app-fix-tax
```

Each worktree has its own files and its own checked-out branch; they all share one `.git` - commits, branches, and history. A branch can be checked out in only one worktree at a time.

## Why agents need them

Two agents editing the same folder trample each other: one runs the tests while the other is half-way through an edit; one commits the other's work. Worktrees give each agent **its own directory and branch**, while staying cheap - no second clone, no second download, and every branch is instantly visible to the others.

| | Worktree | Second clone |
|---|---|---|
| Disk and time | Only the working files | Full history again |
| Branches and commits | Shared immediately | Need push and fetch between clones |
| Same branch twice | Not allowed | Allowed |
| Gitignored files (`.env`, `node_modules`) | Not copied - a fresh checkout | Not copied either |

## What a worktree does not have

It is a fresh checkout of tracked files only: no `.env`, no `node_modules`, no build output. Each one needs its own setup - install dependencies, copy local config - before tests will pass.

## Commands this node introduces

`git worktree add <path> -b <branch>`, `git worktree list`, and `git worktree remove <path>`.
