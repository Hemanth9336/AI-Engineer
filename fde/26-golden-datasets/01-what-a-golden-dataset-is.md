---
type: lesson
title: "What a golden dataset is"
minutes: 5
---

A **golden dataset** is the fixed set of questions your eval runs on, each paired with what a correct answer looks like. It's the single most valuable artefact in an AI engagement - more durable than any prompt, model or index you'll build.

## One line per case

Store it as JSONL - one JSON object per line, easy to diff, append and review:

```json
{"id": "g01", "question": "How long do I have to report a damaged parcel?", "expected": "Within 7 days of delivery, with photos.", "source": "a1", "type": "easy"}
```

| Field | Why |
|---|---|
| `id` | Stable name for the case - "g07 regressed" is a useful sentence |
| `question` | Exactly as a user would type it |
| `expected` | The facts a correct answer must contain - not a word-for-word script |
| `source` | Which document holds the answer - lets you measure retrieval separately (topic 29) |
| `type` | Easy, hard or trap - so you can report scores per slice |

## What makes an expected answer good

- **Facts, not phrasing.** "7 days, with photos" - any answer containing those facts is right, however it's worded.
- **Checkable.** Numbers, deadlines, yes/no, a named step. "Explains the process well" can't be graded consistently.
- **Agreed with an expert.** If the customer's support lead wouldn't sign it, it isn't golden.

## How big?

Start with **20-50** cases you trust, not 500 you don't. Grow it every week from real questions and every reported failure. Quality beats size: one wrong expected answer teaches you to ignore the eval.
