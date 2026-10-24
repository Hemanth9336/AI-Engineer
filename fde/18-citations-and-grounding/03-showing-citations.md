---
type: lesson
title: "Showing citations"
minutes: 5
---

"Trust me" doesn't work with customers' legal and compliance teams. **Citations** - the source ids behind each claim - let a human check any answer in seconds, and let your code check grounding automatically.

## Ask for citations in a structure

```text
After each fact, cite its source id in square brackets, like [a3].
Reply with JSON: {"answer": "...", "citations": ["a3"]}
```

```json
{"answer": "Customs checks usually add 2 to 5 working days [a3]. Duties are paid by the receiver unless DDP was booked [a3].",
 "citations": ["a3"]}
```

The UI turns `[a3]` into a link to the article; the `citations` list feeds logging and checks.

## Validate citations in code

Models sometimes cite sources that weren't provided, or forget the brackets. Check every response:

| Check | Catches |
|---|---|
| Every citation is one of the ids you sent | Invented or stale ids |
| Every citation appears as `[id]` in the answer | A list that doesn't match the text |
| A non-refusal answer has at least one citation | Answers with no grounding |
| A refusal has no citations | Contradictory output |

```python
def check_citations(result, source_ids):
    problems = []
    cites = result.get("citations") or []
    for c in cites:
        if c not in source_ids:
            problems.append(f"unknown source {c}")
        elif f"[{c}]" not in result.get("answer", ""):
            problems.append(f"{c} not cited in the answer")
    ...
    return problems
```

## Citations aren't proof

A correct citation shows *where* the model says a fact came from - not that the fact really is in that source. To check that, you need a **faithfulness** eval (topic 29), which compares each claim against the cited text. Citations make that check possible, and make spot-checks by humans fast.
