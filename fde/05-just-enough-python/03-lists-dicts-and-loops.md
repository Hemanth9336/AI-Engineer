---
type: lesson
title: "Lists, dicts, and loops"
minutes: 5
---

Every API reply you'll handle is made of two structures: **lists** and **dicts**. Learn to move through them and you can read any JSON.

## Lists: ordered collections

```python
models = ["lab-mini", "lab-fast", "lab-smart"]
models[0]          # "lab-mini" - counting starts at 0
models[-1]         # "lab-smart" - last item
len(models)        # 3
models.append("lab-open")
```

## Dicts: named fields

```python
ticket = {"id": "T-104", "priority": "high", "text": "Parcel arrived damaged"}
ticket["priority"]           # "high"
ticket.get("owner")          # None - no error when the key is missing
ticket.get("owner", "none")  # "none" - with a default
ticket["owner"] = "Priya"    # add or change a field
"id" in ticket               # True
```

## Nesting: how API replies look

A chat API reply is a dict containing lists of dicts:

```python
reply = {
    "model": "lab-mini",
    "choices": [
        {"index": 0, "message": {"role": "assistant", "content": "Your parcel is in Leeds."}, "finish_reason": "stop"}
    ],
    "usage": {"prompt_tokens": 21, "completion_tokens": 7, "total_tokens": 28},
}
reply["choices"][0]["message"]["content"]   # "Your parcel is in Leeds."
reply["usage"]["total_tokens"]              # 28
```

Read the path left to right: the `choices` field, item 0, its `message`, its `content`.

## Loops

```python
for m in models:
    print(m)

for i, choice in enumerate(reply["choices"]):
    print(i, choice["message"]["content"])

for key, value in reply["usage"].items():
    print(key, value)
```

## Comprehensions: a loop that builds a list

```python
high = [t for t in tickets if t["priority"] == "high"]
lengths = [len(t["text"]) for t in tickets]
total = sum(lengths)
```

## JSON in and out

JSON files map directly onto lists and dicts:

```python
import json

data = json.load(open("reply.json"))        # file -> dicts and lists
json.dump(data, open("out.json", "w"), indent=2)
text = json.dumps(data)                     # to a string
```
