---
type: lesson
title: "Checklists and verdicts"
minutes: 14
---

"Review this" gets you a different review every time. A **checklist skill** plus a **schema for the verdict** makes reviews comparable, gradeable and automatable.

## A checklist skill

```markdown
---
name: review-checklist
description: Review a diff file against the team checklist and return a verdict.
argument-hint: DIFF_FILE
disable-model-invocation: true
---
Review the unified diff in $ARGUMENTS. Report only issues on added lines, citing the file and the new line number.

| Rule | Look for | Severity |
|---|---|---|
| SEC-SQL | SQL built with f-strings, %, +, or .format | blocker |
| ERR-SWALLOW | except blocks that pass or hide the error | major |
| CFG-DEBUG | Debug or insecure settings switched on | minor |
| TEST-MISSING | Behaviour changed without a test change | major |

Verdict: request_changes if any finding is blocker or major; otherwise approve.
```

- **Rule ids** make findings countable ("SEC-SQL found in 4 of 30 PRs") and let you grade the reviewer.
- **Severities with a fixed meaning** turn the verdict into a rule, not a mood.
- `disable-model-invocation: true` keeps it a deliberate step that you, or CI, invoke as `/review-checklist changes.diff`.

## A verdict schema

```json
{"type": "object", "required": ["verdict", "findings"], "properties": {
  "verdict": {"enum": ["approve", "request_changes"]},
  "findings": {"type": "array", "items": {"type": "object", "required": ["file", "line", "rule", "severity"],
    "properties": {"file": {"type": "string"}, "line": {"type": "integer"}, "rule": {"enum": ["SEC-SQL", "ERR-SWALLOW", "CFG-DEBUG", "TEST-MISSING"]},
                   "severity": {"enum": ["blocker", "major", "minor"]}, "note": {"type": "string"}}}}}}
```

Run it with `--json-schema` (topic 053) and read `.structured_output`. That gives you a verdict a pipeline can act on: comment, label, or request a human.

## Grade the reviewer

Keep a few **seeded diffs** with known issues (an answer key), and score the reviewer on them whenever you change the checklist or the model:

| Measure | Meaning |
|---|---|
| Recall (found / seeded) | Did it catch what matters? A missed blocker is the costly failure |
| Precision (correct / reported) | How much noise does a human wade through? |
| Verdict agreement | Did it reach the verdict the key expects? |

Match a finding to the key by file, rule, and a line within ±1. Diff line numbers shift easily.

## Commands this node introduces

Checklist skills with rule ids and severities, `disable-model-invocation`, `$ARGUMENTS`, verdict schemas, `.structured_output`, seeded diffs, and recall/precision grading.
