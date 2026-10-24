---
type: lesson
title: "Reading a loop transcript"
minutes: 7
---

When an agent gives a wrong answer, the answer alone tells you almost nothing. **The transcript** - every step the loop took - tells you everything. Learning to read one is the most practical debugging skill in harness work.

## What to record per step

```json
{"step": 1, "prompt_tokens": 412, "completion_tokens": 18, "tool_calls": [{"name": "list_dir", "args": {"path": "."}}], "results": ["README.md\nservices/"], "answer": null}
{"step": 2, "prompt_tokens": 486, "completion_tokens": 21, "tool_calls": [{"name": "list_dir", "args": {"path": "services"}}], "results": ["billing.yaml\nsearch.yaml"], "answer": null}
{"step": 3, "prompt_tokens": 571, "completion_tokens": 24, "tool_calls": [{"name": "read_file", "args": {"path": "services/billing.yaml"}}], "results": ["name: billing\nport: 8081 ..."], "answer": null}
{"step": 4, "prompt_tokens": 655, "completion_tokens": 12, "tool_calls": [], "results": [], "answer": "Billing uses port 8081."}
```

One JSON object per line (**JSONL**) is easy to append while the loop runs, survives a crash halfway through, and loads with one line of Python.

## Questions a transcript answers

- **Did it look before answering?** If step 1 is the answer, the model guessed.
- **Did it read the right thing?** A wrong answer after reading `search.yaml` is a retrieval problem, not a reasoning problem.
- **Where did it waste steps?** The same `list_dir` three times in a row is a loop that should have been stopped.
- **What did it cost?** `prompt_tokens` grows each step because the history grows. Sum them for the task's input cost.
- **What did the model actually see?** The `results` column is the model's only view of the world. If a result is an error or truncated, that explains a lot.

## Keep results short in the trace

The trace is for humans. Store the first couple of hundred characters of each result, not the whole file. (The full detail goes in a separate transcript - topic 31.)

In the next task you'll add this logging to your loop, then read a trace from someone else's run.
