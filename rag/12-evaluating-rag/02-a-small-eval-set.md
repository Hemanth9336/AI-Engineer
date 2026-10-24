---
type: lesson
title: "A small eval set"
minutes: 6
---

An eval set is a list of questions with known right answers. Ten good items beat a hundred vague ones.

```json
[
  { "question": "How long are database backups kept?", "source": "backups.md", "expect": "35 days" },
  { "question": "How often must secrets be rotated?",   "source": "security.md", "expect": "90 days" },
  { "question": "What is the office wifi password?",    "source": null,         "expect": null }
]
```

| Field | Meaning | Used for |
|---|---|---|
| `question` | Asked exactly as written | Both evals |
| `source` | The document that holds the answer, or `null` | Retrieval: is it in the top k? |
| `expect` | A short string the correct answer must contain, or `null` | Answers: contains it - or, when null, refuses |

## Writing good items

- **Ask like a user**, not like the document. "How long do we keep backups?" tests retrieval; copying the document's wording makes it too easy.
- **Pick a distinctive `expect`**: `35 days`, not `days`. It should be hard to contain it by accident.
- **Cover every document**, so a broken file shows up.
- **Add 10-20% unanswerable questions** - plausible ones, like the wifi password, that the documents genuinely don't cover.
- **Keep it in git** next to the code. When a user reports a bad answer, add that question to the set - it can never silently break again.

## Your eval set

The task gives you `eval.json` with 10 items over the 8 ops docs: 8 answerable questions, one per document, and 2 that should be refused.
