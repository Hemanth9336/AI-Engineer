---
type: lesson
title: "Scoring answers, worked through"
minutes: 6
---

Answer accuracy runs the full pipeline and checks every answer.

```python
import json

from rag_lib import REFUSAL, answer

items = json.load(open("eval.json"))
results = []
for item in items:
    got = answer(item["question"])["answer"]
    if item["expect"]:
        correct = item["expect"].lower() in got.lower()
    else:
        correct = got == REFUSAL
    results.append({"question": item["question"], "expect": item["expect"], "answer": got, "correct": correct})

correct = sum(r["correct"] for r in results)
print(f"accuracy: {correct}/{len(results)} = {correct / len(results):.2f}")
for r in results:
    if not r["correct"]:
        print("WRONG", r)
```

```text
accuracy: 10/10 = 1.00
```

## The two rules

- **Answerable** (`expect` set): correct if the answer **contains** the expected string, ignoring case. `"35 days"` is in "Database backups are kept for 35 days." -> correct.
- **Unanswerable** (`expect` is null): correct only if the answer is **exactly** the refusal. An invented wifi password is wrong, however confident it sounds.

## Reading the result with the retrieval number

| Retrieval hit rate | Answer accuracy | Where to look |
|---|---|---|
| High | High | Ship it - and keep running both |
| Low | Low | Retrieval: chunking, k, embedding model |
| High | Low | Generation: prompt rules, model choice |
| - | Unanswerables wrong | The refusal rule, or the model ignoring it |

## Cost

Unlike retrieval eval, this calls the chat model once per item. Ten items cost almost nothing; a thousand do. Keep a small "smoke" set you run on every change, and a bigger set you run before releases.

## Make it repeatable

`temperature=0` (already in `answer()`) keeps results stable between runs, so a change in the score means your change did something - not the dice.
