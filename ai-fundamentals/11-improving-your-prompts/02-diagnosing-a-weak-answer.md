---
type: lesson
title: "Diagnosing a weak answer"
minutes: 7
---

A weak answer is evidence. Read it like a bug report: the symptom points to the cause, and the cause points to the fix.

## Symptom to cause to fix

| Symptom in the answer | Likely cause | Fix |
|---|---|---|
| Generic, could apply to any company | Missing context | Add the specific facts, names, and situation |
| Right content, wrong shape | No format given | Name the exact format; show a template |
| Too long or too short | No length constraint | Give a number: words, items, sentences |
| Wrong level for the reader | No audience | Name the audience precisely |
| Answers a different question | Ambiguous task, or the question is buried | Put one clear task first; delimit the data |
| Invents facts or values | No permission to say "unknown" | "If the text doesn't say, write unknown" |
| Inconsistent between runs | Loose wording, high temperature | Tighter format, examples, `temperature: 0` |
| Ignores part of the prompt | Conflicting or too many instructions | Remove the conflict; order rules by importance |

## Look at the whole response, not just the text

The API tells you more than the reply:

- `finish_reason: "length"` - the answer was cut off; raise `max_tokens` or ask for less.
- `usage.prompt_tokens` far bigger than you expected - you may be sending more data than you think.
- The `model` field - make sure the model you meant actually answered.

## Compare against a target

Before you fix anything, write down what a good answer looks like - ideally the exact output you want. Then compare: what is missing, extra, or different? Vague dissatisfaction leads to random rewrites; a concrete target leads to one precise change.

## Change one thing at a time

If you change the role, the format, and the examples all at once and the answer improves, you do not know which change mattered - and you may have added something that hurts other inputs. Make one change, re-run, and compare. That is the refine loop, coming next.
