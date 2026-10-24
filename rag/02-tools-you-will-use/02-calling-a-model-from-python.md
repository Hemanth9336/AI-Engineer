---
type: lesson
title: "Calling a model from Python"
minutes: 8
---

In AI Fundamentals you called models with curl. From here on you will use Python, because RAG means loops, files, and math - all easier in code.

## The smallest script

```python
from openai import OpenAI

client = OpenAI()                     # reads OPENAI_BASE_URL and OPENAI_API_KEY
resp = client.chat.completions.create(
    model="lab-fast",
    messages=[{"role": "user", "content": "In one sentence, what is DNS?"}],
)
print(resp.choices[0].message.content)
```

Run it with `python hello.py`. `python` is the course venv - it's first on your `PATH`.

## Make it a function you can reuse

Every RAG step ends with "now ask the model". Wrap that in one function:

```python
def ask(question, system=None, model="lab-fast"):
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": question})
    resp = client.chat.completions.create(model=model, messages=messages, temperature=0)
    return resp.choices[0].message.content.strip()
```

Three choices worth noticing:

- **`system` is optional.** Later, grounding rules go there.
- **`temperature=0`** makes answers as repeatable as possible. For answering from documents you want the same answer every time, not creativity.
- **It returns a string.** The caller decides what to print or store.

## Make it a command too

The `if __name__ == "__main__":` block runs only when you start the file directly - not when another script imports it. That lets one file be both a library and a tool:

```python
import sys

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: ask.py QUESTION", file=sys.stderr)
        sys.exit(2)
    print(ask(" ".join(sys.argv[1:])))
```

```bash
python ask.py "What is a vector database?"
python -c "from ask import ask; print(ask('Say hi'))"     # the same function, imported
```

## When something goes wrong

| Error | Usual cause |
|---|---|
| `openai.APIConnectionError` | The gateway isn't running - `ailab up` |
| `openai.AuthenticationError` | The environment isn't loaded - `source ~/.bashrc` |
| `openai.NotFoundError` mentioning a model | A typo in the model name |

Now write your own.
