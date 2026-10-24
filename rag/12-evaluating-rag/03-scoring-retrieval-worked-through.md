---
type: lesson
title: "Scoring retrieval, worked through"
minutes: 6
---

Retrieval hit rate needs no chat model at all - just the collection.

```python
import json

from rag_lib import collection

items = [i for i in json.load(open("eval.json")) if i["source"]]
k = 3
hits, misses = 0, []
for item in items:
    res = collection.query(query_texts=[item["question"]], n_results=k)
    got = [m["source"] for m in res["metadatas"][0]]
    if item["source"] in got:
        hits += 1
    else:
        misses.append({"question": item["question"], "expected": item["source"], "got": got})

print(f"hit rate @{k}: {hits}/{len(items)} = {hits / len(items):.2f}")
for m in misses:
    print("MISS", m)
```

```text
hit rate @3: 8/8 = 1.00
```

On this small, clean set every question finds its document. On real data you'd see misses like:

```text
MISS {'question': 'How long do we keep backups?', 'expected': 'backups.md', 'got': ['access.md', 'deploys.md', 'costs.md']}
```

and the miss list is the useful part: it tells you exactly which questions to look at.

## Only answerable items

Items with `source: null` are skipped - there's no right document to find. They matter for the answer eval.

## Using it to choose settings

Run the same eval with different settings and compare:

| Setting | Hit rate @3 |
|---|---|
| chunk 500 / overlap 100 | 1.00 |
| chunk 200 / overlap 0 | ? |
| k = 1 | ? |

Now "should we use smaller chunks?" is a 10-second experiment, not an argument.

## Write results to a file

Save the numbers as JSON so you can compare runs, chart them, or fail a CI build if the hit rate drops below a threshold.
