---
type: lesson
title: "Deny-pattern guardrails with PreToolUse"
minutes: 23
---

Before you let an agent loose on a red suite, decide what it must **never** do, and enforce that in code. A **PreToolUse** hook runs before every matching tool call, *before* the permission system. Exit code 2 denies the call, and your stderr message is shown to the agent so it can change course.

```json
{"hooks": {"PreToolUse": [{"matcher": "Bash|Edit|Write", "hooks": [{"type": "command",
  "command": "python3 \"$CLAUDE_PROJECT_DIR\"/.claude/hooks/guard.py"}]}]}}
```

## What the release guard denies

| Pattern | Why |
|---|---|
| `git push`, `git tag` | Publishing is a human step (the spec's non-goal) |
| `git reset --hard`, `git commit --no-verify` | Throws away work, or skips the checks |
| `rm -rf` in any flag order (`-rf`, `-fr`, `-r -f`) | Broad deletes |
| `curl ... \| sh` | Running code from the internet |
| Writes to `tests/` (Edit/Write paths, or Bash redirects, `tee`, `sed -i`, `mv`, `cp`, `rm`) | **The suite is the judge.** An agent that edits tests can always "fix" a red build |

## Design rules

- **Explain the denial.** "Blocked by the release guard: tests/ is protected." lets the agent pivot to the real fix instead of retrying.
- **Log every denial** (`guard.jsonl`). A guard that fires often means the instructions are wrong.
- **Fail open on garbage input**, but only for the guard's *parsing*. The permission system and sandbox still apply behind it.
- **Test the guard directly** by piping event JSON into it, with both the dangerous variants and the innocent look-alikes (`git status`, `rm -f one-file`).
- **Patterns reduce risk; they aren't a sandbox.** `bash -c "$(echo Z2l0IHB1c2g= | base64 -d)"` gets past a regex. Pair the guard with permissions and sandboxing (topics 028 and 062) for real isolation.

## Then let the agent fix it

```bash
claude -p "The release check is red. Find the regression and fix it in app/ - do not change the tests." \
  --permission-mode acceptEdits --allowedTools "Bash(python3 release/check.py),Bash(git log *),Bash(git diff *),Read"
```

Verify the result independently: re-run the check yourself, confirm `tests/` is byte-identical, and read the diff.

## Commands this node introduces

PreToolUse deny hooks, exit code 2 with a stderr reason, `guard.jsonl`, protected `tests/`, testing a guard with piped events, and independent verification after an agent fix.
