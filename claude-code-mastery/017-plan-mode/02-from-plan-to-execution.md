---
type: lesson
title: "From plan to execution"
minutes: 14
---

When the plan is ready, the console asks how to proceed:

```text
Would you like to proceed?
❯ 1. Yes, and use auto mode
  2. Yes, manually approve edits
  3. No, keep planning
```

Approving switches the session out of plan mode into the mode you picked, and Claude starts implementing. **No, keep planning** lets you push back - "don't add a new dependency, reuse `money.py`" - and get a revised plan.

## Headless: plan, review, execute

A `-p` run in plan mode returns the plan as its `result`. That gives you a clean two-step pipeline with a human (or a script) in between:

```bash
# 1. plan - nothing in the repo can change
claude -p "Add a --json flag to report.py" --permission-mode plan --output-format json > plan.json
jq -r .result plan.json > PLAN.md

# 2. review PLAN.md, edit it if needed

# 3. execute exactly that plan
claude -p "Implement the plan in PLAN.md. Do not do anything it does not list." \
  --permission-mode acceptEdits --allowedTools "Bash(python3 -m unittest *)"
```

## Holding execution to the plan

- Tell the executing run to follow the plan and nothing else.
- Compare the files it touched with the files the plan named.
- Run the verification step from the plan yourself.

If execution needs something the plan did not anticipate, that is a signal to go back to planning, not to improvise.

## Commands this node introduces

`--permission-mode plan` with `-p` produces a reviewable plan; `jq -r .result plan.json > PLAN.md` saves it.
