---
type: task
title: "Summarize old turns, keep the summary in context"
minutes: 9
---

## Set up

`workspace/logs/` has six logs of about 2,400 characters each. `history.json` is a saved run that read five of them.

```bash
mkdir -p /root/harness-lab/18-compact/workspace/services
cd /root/harness-lab/18-compact
cat > workspace/README.md <<'EOF'
# Stackline services
Two services run in production: billing and search.
Config lives in services/<name>.yaml.
EOF
cat > workspace/services/billing.yaml <<'EOF'
name: billing
port: 8081
owner: payments team
replicas: 3
EOF
cat > workspace/services/search.yaml <<'EOF'
name: search
port: 9200
owner: discovery team
replicas: 5
EOF
[ -f agent.py ] || cat > agent.py <<'EOF'
import json
import sys
from pathlib import Path

from openai import OpenAI

SYSTEM = "You are Stackline's project assistant. Use the tools to look at the workspace before answering. Answer briefly."

SCHEMAS = [
    {"type": "function", "function": {
        "name": "list_dir",
        "description": "List the files and folders inside a workspace folder. Folders end with /. Use it to find files before reading them.",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string", "description": "Folder relative to the workspace, for example services. Use . for the top."}},
            "required": ["path"]}}},
    {"type": "function", "function": {
        "name": "read_file",
        "description": "Read a text file from the workspace and return its contents. Use it whenever the answer depends on what a file says.",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string", "description": "File path relative to the workspace, for example services/billing.yaml"}},
            "required": ["path"]}}},
]

WORK = Path(__file__).parent / "workspace"


def list_dir(path="."):
    p = WORK / path
    if not p.is_dir():
        return f"error: no such folder {path}"
    return "\n".join(sorted(c.name + ("/" if c.is_dir() else "") for c in p.iterdir()))


def read_file(path):
    p = WORK / path
    if not p.is_file():
        return f"error: no such file {path}"
    return p.read_text()


IMPL = {"list_dir": list_dir, "read_file": read_file}


def run_tool(name, args):
    if name not in IMPL:
        return f"error: unknown tool {name}"
    try:
        return IMPL[name](**args)
    except TypeError as e:
        return f"error: bad arguments for {name}: {e}"


def run(question, max_steps=8):
    client = OpenAI()
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": question}]
    for _ in range(max_steps):
        msg = client.chat.completions.create(model="lab-fast", tools=SCHEMAS, messages=messages).choices[0].message
        if not msg.tool_calls:
            return msg.content
        messages.append(msg)
        for call in msg.tool_calls:
            result = run_tool(call.function.name, json.loads(call.function.arguments or "{}"))
            messages.append({"role": "tool", "tool_call_id": call.id, "content": result})
    return f"stopped: reached max steps ({max_steps})"


if __name__ == "__main__":
    answer = run(sys.argv[1])
    print(answer)
    sys.exit(2 if answer.startswith("stopped: reached max steps") else 0)
EOF
echo 'agent.py is your loop with a step limit (topic 08)'
python - <<'EOF'
from pathlib import Path
Path('workspace/logs').mkdir(parents=True, exist_ok=True)
for n in range(1, 7):
    Path(f'workspace/logs/part{n}.log').write_text(''.join(f'line {n}.{i} INFO search request ok {i * 7 % 300}ms\n' for i in range(60)))
EOF
cat > history.json <<'EOF'
[
 {
  "role": "system",
  "content": "You are Stackline's project assistant. Use the tools to look at the workspace before answering. Answer briefly."
 },
 {
  "role": "user",
  "content": "Which log has the slowest request?"
 },
 {
  "role": "assistant",
  "content": null,
  "tool_calls": [
   {
    "id": "call_1",
    "type": "function",
    "function": {
     "name": "read_file",
     "arguments": "{\"path\": \"logs/part1.log\"}"
    }
   }
  ]
 },
 {
  "role": "tool",
  "tool_call_id": "call_1",
  "content": "line 1.0 INFO search request ok 0ms\nline 1.1 INFO search request ok 7ms\nline 1.2 INFO search request ok 14ms\nline 1.3 INFO search request ok 21ms\nline 1.4 INFO search request ok 28ms\nline 1.5 INFO search request ok 35ms\nline 1.6 INFO search request ok 42ms\nline 1.7 INFO search request ok 49ms\nline 1.8 INFO search request ok 56ms\nline 1.9 INFO search request ok 63ms\nline 1.10 INFO search request ok 70ms\nline 1.11 INFO search request ok 77ms\nline 1.12 INFO search request ok 84ms\nline 1.13 INFO search request ok 91ms\nline 1.14 INFO search request ok 98ms\nline 1.15 INFO search request ok 105ms\nline 1.16 INFO search request ok 112ms\nline 1.17 INFO search request ok 119ms\nline 1.18 INFO search request ok 126ms\nline 1.19 INFO search request ok 133ms\nline 1.20 INFO search request ok 140ms\nline 1.21 INFO search request ok 147ms\nline 1.22 INFO search request ok 154ms\nline 1.23 INFO search request ok 161ms\nline 1.24 INFO search request ok 168ms\nline 1.25 INFO search request ok 175ms\nline 1.26 INFO search request ok 182ms\nline 1.27 INFO search request ok 189ms\nline 1.28 INFO search request ok 196ms\nline 1.29 INFO search request ok 203ms\nline 1.30 INFO search request ok 210ms\nline 1.31 INFO search request ok 217ms\nline 1.32 INFO search request ok 224ms\nline 1.33 INFO search request ok 231ms\nline 1.34 INFO search request ok 238ms\nline 1.35 INFO search request ok 245ms\nline 1.36 INFO search request ok 252ms\nline 1.37 INFO search request ok 259ms\nline 1.38 INFO search request ok 266ms\nline 1.39 INFO search request ok 273ms\nline 1.40 INFO search request ok 280ms\nline 1.41 INFO search request ok 287ms\nline 1.42 INFO search request ok 294ms\nline 1.43 INFO search request ok 1ms\nline 1.44 INFO search request ok 8ms\nline 1.45 INFO search request ok 15ms\nline 1.46 INFO search request ok 22ms\nline 1.47 INFO search request ok 29ms\nline 1.48 INFO search request ok 36ms\nline 1.49 INFO search request ok 43ms\nline 1.50 INFO search request ok 50ms\nline 1.51 INFO search request ok 57ms\nline 1.52 INFO search request ok 64ms\nline 1.53 INFO search request ok 71ms\nline 1.54 INFO search request ok 78ms\nline 1.55 INFO search request ok 85ms\nline 1.56 INFO search request ok 92ms\nline 1.57 INFO search request ok 99ms\nline 1.58 INFO search request ok 106ms\nline 1.59 INFO search request ok 113ms\n"
 },
 {
  "role": "assistant",
  "content": null,
  "tool_calls": [
   {
    "id": "call_2",
    "type": "function",
    "function": {
     "name": "read_file",
     "arguments": "{\"path\": \"logs/part2.log\"}"
    }
   }
  ]
 },
 {
  "role": "tool",
  "tool_call_id": "call_2",
  "content": "line 2.0 INFO search request ok 0ms\nline 2.1 INFO search request ok 7ms\nline 2.2 INFO search request ok 14ms\nline 2.3 INFO search request ok 21ms\nline 2.4 INFO search request ok 28ms\nline 2.5 INFO search request ok 35ms\nline 2.6 INFO search request ok 42ms\nline 2.7 INFO search request ok 49ms\nline 2.8 INFO search request ok 56ms\nline 2.9 INFO search request ok 63ms\nline 2.10 INFO search request ok 70ms\nline 2.11 INFO search request ok 77ms\nline 2.12 INFO search request ok 84ms\nline 2.13 INFO search request ok 91ms\nline 2.14 INFO search request ok 98ms\nline 2.15 INFO search request ok 105ms\nline 2.16 INFO search request ok 112ms\nline 2.17 INFO search request ok 119ms\nline 2.18 INFO search request ok 126ms\nline 2.19 INFO search request ok 133ms\nline 2.20 INFO search request ok 140ms\nline 2.21 INFO search request ok 147ms\nline 2.22 INFO search request ok 154ms\nline 2.23 INFO search request ok 161ms\nline 2.24 INFO search request ok 168ms\nline 2.25 INFO search request ok 175ms\nline 2.26 INFO search request ok 182ms\nline 2.27 INFO search request ok 189ms\nline 2.28 INFO search request ok 196ms\nline 2.29 INFO search request ok 203ms\nline 2.30 INFO search request ok 210ms\nline 2.31 INFO search request ok 217ms\nline 2.32 INFO search request ok 224ms\nline 2.33 INFO search request ok 231ms\nline 2.34 INFO search request ok 238ms\nline 2.35 INFO search request ok 245ms\nline 2.36 INFO search request ok 252ms\nline 2.37 INFO search request ok 259ms\nline 2.38 INFO search request ok 266ms\nline 2.39 INFO search request ok 273ms\nline 2.40 INFO search request ok 280ms\nline 2.41 INFO search request ok 287ms\nline 2.42 INFO search request ok 294ms\nline 2.43 INFO search request ok 1ms\nline 2.44 INFO search request ok 8ms\nline 2.45 INFO search request ok 15ms\nline 2.46 INFO search request ok 22ms\nline 2.47 INFO search request ok 29ms\nline 2.48 INFO search request ok 36ms\nline 2.49 INFO search request ok 43ms\nline 2.50 INFO search request ok 50ms\nline 2.51 INFO search request ok 57ms\nline 2.52 INFO search request ok 64ms\nline 2.53 INFO search request ok 71ms\nline 2.54 INFO search request ok 78ms\nline 2.55 INFO search request ok 85ms\nline 2.56 INFO search request ok 92ms\nline 2.57 INFO search request ok 99ms\nline 2.58 INFO search request ok 106ms\nline 2.59 INFO search request ok 113ms\n"
 },
 {
  "role": "assistant",
  "content": null,
  "tool_calls": [
   {
    "id": "call_3",
    "type": "function",
    "function": {
     "name": "read_file",
     "arguments": "{\"path\": \"logs/part3.log\"}"
    }
   }
  ]
 },
 {
  "role": "tool",
  "tool_call_id": "call_3",
  "content": "line 3.0 INFO search request ok 0ms\nline 3.1 INFO search request ok 7ms\nline 3.2 INFO search request ok 14ms\nline 3.3 INFO search request ok 21ms\nline 3.4 INFO search request ok 28ms\nline 3.5 INFO search request ok 35ms\nline 3.6 INFO search request ok 42ms\nline 3.7 INFO search request ok 49ms\nline 3.8 INFO search request ok 56ms\nline 3.9 INFO search request ok 63ms\nline 3.10 INFO search request ok 70ms\nline 3.11 INFO search request ok 77ms\nline 3.12 INFO search request ok 84ms\nline 3.13 INFO search request ok 91ms\nline 3.14 INFO search request ok 98ms\nline 3.15 INFO search request ok 105ms\nline 3.16 INFO search request ok 112ms\nline 3.17 INFO search request ok 119ms\nline 3.18 INFO search request ok 126ms\nline 3.19 INFO search request ok 133ms\nline 3.20 INFO search request ok 140ms\nline 3.21 INFO search request ok 147ms\nline 3.22 INFO search request ok 154ms\nline 3.23 INFO search request ok 161ms\nline 3.24 INFO search request ok 168ms\nline 3.25 INFO search request ok 175ms\nline 3.26 INFO search request ok 182ms\nline 3.27 INFO search request ok 189ms\nline 3.28 INFO search request ok 196ms\nline 3.29 INFO search request ok 203ms\nline 3.30 INFO search request ok 210ms\nline 3.31 INFO search request ok 217ms\nline 3.32 INFO search request ok 224ms\nline 3.33 INFO search request ok 231ms\nline 3.34 INFO search request ok 238ms\nline 3.35 INFO search request ok 245ms\nline 3.36 INFO search request ok 252ms\nline 3.37 INFO search request ok 259ms\nline 3.38 INFO search request ok 266ms\nline 3.39 INFO search request ok 273ms\nline 3.40 INFO search request ok 280ms\nline 3.41 INFO search request ok 287ms\nline 3.42 INFO search request ok 294ms\nline 3.43 INFO search request ok 1ms\nline 3.44 INFO search request ok 8ms\nline 3.45 INFO search request ok 15ms\nline 3.46 INFO search request ok 22ms\nline 3.47 INFO search request ok 29ms\nline 3.48 INFO search request ok 36ms\nline 3.49 INFO search request ok 43ms\nline 3.50 INFO search request ok 50ms\nline 3.51 INFO search request ok 57ms\nline 3.52 INFO search request ok 64ms\nline 3.53 INFO search request ok 71ms\nline 3.54 INFO search request ok 78ms\nline 3.55 INFO search request ok 85ms\nline 3.56 INFO search request ok 92ms\nline 3.57 INFO search request ok 99ms\nline 3.58 INFO search request ok 106ms\nline 3.59 INFO search request ok 113ms\n"
 },
 {
  "role": "assistant",
  "content": null,
  "tool_calls": [
   {
    "id": "call_4",
    "type": "function",
    "function": {
     "name": "read_file",
     "arguments": "{\"path\": \"logs/part4.log\"}"
    }
   }
  ]
 },
 {
  "role": "tool",
  "tool_call_id": "call_4",
  "content": "line 4.0 INFO search request ok 0ms\nline 4.1 INFO search request ok 7ms\nline 4.2 INFO search request ok 14ms\nline 4.3 INFO search request ok 21ms\nline 4.4 INFO search request ok 28ms\nline 4.5 INFO search request ok 35ms\nline 4.6 INFO search request ok 42ms\nline 4.7 INFO search request ok 49ms\nline 4.8 INFO search request ok 56ms\nline 4.9 INFO search request ok 63ms\nline 4.10 INFO search request ok 70ms\nline 4.11 INFO search request ok 77ms\nline 4.12 INFO search request ok 84ms\nline 4.13 INFO search request ok 91ms\nline 4.14 INFO search request ok 98ms\nline 4.15 INFO search request ok 105ms\nline 4.16 INFO search request ok 112ms\nline 4.17 INFO search request ok 119ms\nline 4.18 INFO search request ok 126ms\nline 4.19 INFO search request ok 133ms\nline 4.20 INFO search request ok 140ms\nline 4.21 INFO search request ok 147ms\nline 4.22 INFO search request ok 154ms\nline 4.23 INFO search request ok 161ms\nline 4.24 INFO search request ok 168ms\nline 4.25 INFO search request ok 175ms\nline 4.26 INFO search request ok 182ms\nline 4.27 INFO search request ok 189ms\nline 4.28 INFO search request ok 196ms\nline 4.29 INFO search request ok 203ms\nline 4.30 INFO search request ok 210ms\nline 4.31 INFO search request ok 217ms\nline 4.32 INFO search request ok 224ms\nline 4.33 INFO search request ok 231ms\nline 4.34 INFO search request ok 238ms\nline 4.35 INFO search request ok 245ms\nline 4.36 INFO search request ok 252ms\nline 4.37 INFO search request ok 259ms\nline 4.38 INFO search request ok 266ms\nline 4.39 INFO search request ok 273ms\nline 4.40 INFO search request ok 280ms\nline 4.41 INFO search request ok 287ms\nline 4.42 INFO search request ok 294ms\nline 4.43 INFO search request ok 1ms\nline 4.44 INFO search request ok 8ms\nline 4.45 INFO search request ok 15ms\nline 4.46 INFO search request ok 22ms\nline 4.47 INFO search request ok 29ms\nline 4.48 INFO search request ok 36ms\nline 4.49 INFO search request ok 43ms\nline 4.50 INFO search request ok 50ms\nline 4.51 INFO search request ok 57ms\nline 4.52 INFO search request ok 64ms\nline 4.53 INFO search request ok 71ms\nline 4.54 INFO search request ok 78ms\nline 4.55 INFO search request ok 85ms\nline 4.56 INFO search request ok 92ms\nline 4.57 INFO search request ok 99ms\nline 4.58 INFO search request ok 106ms\nline 4.59 INFO search request ok 113ms\n"
 },
 {
  "role": "assistant",
  "content": null,
  "tool_calls": [
   {
    "id": "call_5",
    "type": "function",
    "function": {
     "name": "read_file",
     "arguments": "{\"path\": \"logs/part5.log\"}"
    }
   }
  ]
 },
 {
  "role": "tool",
  "tool_call_id": "call_5",
  "content": "line 5.0 INFO search request ok 0ms\nline 5.1 INFO search request ok 7ms\nline 5.2 INFO search request ok 14ms\nline 5.3 INFO search request ok 21ms\nline 5.4 INFO search request ok 28ms\nline 5.5 INFO search request ok 35ms\nline 5.6 INFO search request ok 42ms\nline 5.7 INFO search request ok 49ms\nline 5.8 INFO search request ok 56ms\nline 5.9 INFO search request ok 63ms\nline 5.10 INFO search request ok 70ms\nline 5.11 INFO search request ok 77ms\nline 5.12 INFO search request ok 84ms\nline 5.13 INFO search request ok 91ms\nline 5.14 INFO search request ok 98ms\nline 5.15 INFO search request ok 105ms\nline 5.16 INFO search request ok 112ms\nline 5.17 INFO search request ok 119ms\nline 5.18 INFO search request ok 126ms\nline 5.19 INFO search request ok 133ms\nline 5.20 INFO search request ok 140ms\nline 5.21 INFO search request ok 147ms\nline 5.22 INFO search request ok 154ms\nline 5.23 INFO search request ok 161ms\nline 5.24 INFO search request ok 168ms\nline 5.25 INFO search request ok 175ms\nline 5.26 INFO search request ok 182ms\nline 5.27 INFO search request ok 189ms\nline 5.28 INFO search request ok 196ms\nline 5.29 INFO search request ok 203ms\nline 5.30 INFO search request ok 210ms\nline 5.31 INFO search request ok 217ms\nline 5.32 INFO search request ok 224ms\nline 5.33 INFO search request ok 231ms\nline 5.34 INFO search request ok 238ms\nline 5.35 INFO search request ok 245ms\nline 5.36 INFO search request ok 252ms\nline 5.37 INFO search request ok 259ms\nline 5.38 INFO search request ok 266ms\nline 5.39 INFO search request ok 273ms\nline 5.40 INFO search request ok 280ms\nline 5.41 INFO search request ok 287ms\nline 5.42 INFO search request ok 294ms\nline 5.43 INFO search request ok 1ms\nline 5.44 INFO search request ok 8ms\nline 5.45 INFO search request ok 15ms\nline 5.46 INFO search request ok 22ms\nline 5.47 INFO search request ok 29ms\nline 5.48 INFO search request ok 36ms\nline 5.49 INFO search request ok 43ms\nline 5.50 INFO search request ok 50ms\nline 5.51 INFO search request ok 57ms\nline 5.52 INFO search request ok 64ms\nline 5.53 INFO search request ok 71ms\nline 5.54 INFO search request ok 78ms\nline 5.55 INFO search request ok 85ms\nline 5.56 INFO search request ok 92ms\nline 5.57 INFO search request ok 99ms\nline 5.58 INFO search request ok 106ms\nline 5.59 INFO search request ok 113ms\n"
 }
]
EOF
```

## What to build

1. Write `/root/harness-lab/18-compact/compact.py` with `compact(messages, client, limit=6000, keep_last=2)` that returns a new message list:
   - `messages[0]` (system) and `messages[1]` (the task) are always kept.
   - Group the rest into turns (an assistant message plus the tool messages after it; any other message is a turn of its own).
   - If the rest is at most `limit` characters (total `len(json.dumps(m))`), or there are no more than `keep_last` turns, return `messages` unchanged - and make **no** model call.
   - Otherwise send every turn except the last `keep_last` to **`lab-mini`** with a summarizer system prompt (it must contain the word "summarize") and the old turns as text in one user message.
   - Return system + task + one user message `[summary of earlier steps]\n<summary>` + the last `keep_last` turns, unchanged.
2. In `agent.py`, store assistant messages as plain dicts and call `messages = compact(messages, client)` before every model call.

Try it on the saved history:

```bash
cd /root/harness-lab/18-compact
python -c "import json; from openai import OpenAI; from compact import compact; h = compact(json.load(open('history.json')), OpenAI()); print(len(h), 'messages'); print(h[2]['content'])"
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Reuse `turns()` from topic 17's budget.py.
- A previous summary is a user message - a turn of its own - so it gets folded into the next summary automatically.
- Render tool calls as text for the summarizer, for example `assistant called: read_file({"path": ...})`.

</details>

<details><summary>Solution</summary>

```bash
cd /root/harness-lab/18-compact
cat > compact.py <<'EOF'
import json

SUMMARIZER = ("You compress an AI agent's working history so it can keep going with less context. "
              "Summarize the earlier steps below: which tools were called, what they found (keep exact names, "
              "numbers, paths and error messages), and what is still unknown. At most 150 words, plain text.")
PREFIX = "[summary of earlier steps]\n"
LIMIT = 6000
KEEP_LAST = 2


def size(msgs):
    return sum(len(json.dumps(m)) for m in msgs)


def turns(msgs):
    out = []
    for m in msgs:
        if m.get("role") == "tool" and out:
            out[-1].append(m)
        else:
            out.append([m])
    return out


def as_text(msgs):
    lines = []
    for m in msgs:
        if m.get("tool_calls"):
            calls = ", ".join(f"{c['function']['name']}({c['function']['arguments']})" for c in m["tool_calls"])
            lines.append(f"assistant called: {calls}")
        else:
            lines.append(f"{m['role']}: {m.get('content') or ''}")
    return "\n".join(lines)


def compact(messages, client, limit=LIMIT, keep_last=KEEP_LAST):
    head, rest = messages[:2], messages[2:]
    groups = turns(rest)
    if size(rest) <= limit or len(groups) <= keep_last:
        return messages
    old, recent = groups[:-keep_last], groups[-keep_last:]
    summary = client.chat.completions.create(model="lab-mini", messages=[
        {"role": "system", "content": SUMMARIZER},
        {"role": "user", "content": as_text([m for g in old for m in g])},
    ]).choices[0].message.content
    return head + [{"role": "user", "content": PREFIX + summary}] + [m for g in recent for m in g]

EOF
cat > agent.py <<'EOF'
import json
import sys
from pathlib import Path

from openai import OpenAI

from compact import compact

SYSTEM = "You are Stackline's project assistant. Use the tools to look at the workspace before answering. Answer briefly."

SCHEMAS = [
    {"type": "function", "function": {
        "name": "list_dir",
        "description": "List the files and folders inside a workspace folder. Folders end with /. Use it to find files before reading them.",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string", "description": "Folder relative to the workspace, for example services. Use . for the top."}},
            "required": ["path"]}}},
    {"type": "function", "function": {
        "name": "read_file",
        "description": "Read a text file from the workspace and return its contents. Use it whenever the answer depends on what a file says.",
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string", "description": "File path relative to the workspace, for example services/billing.yaml"}},
            "required": ["path"]}}},
]

WORK = Path(__file__).parent / "workspace"


def list_dir(path="."):
    p = WORK / path
    if not p.is_dir():
        return f"error: no such folder {path}"
    return "\n".join(sorted(c.name + ("/" if c.is_dir() else "") for c in p.iterdir()))


def read_file(path):
    p = WORK / path
    if not p.is_file():
        return f"error: no such file {path}"
    return p.read_text()


IMPL = {"list_dir": list_dir, "read_file": read_file}


def run_tool(name, args):
    if name not in IMPL:
        return f"error: unknown tool {name}"
    try:
        return IMPL[name](**args)
    except TypeError as e:
        return f"error: bad arguments for {name}: {e}"


def run(question, max_steps=8):
    client = OpenAI()
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": question}]
    for _ in range(max_steps):
        messages = compact(messages, client)
        msg = client.chat.completions.create(model="lab-fast", tools=SCHEMAS, messages=messages).choices[0].message
        if not msg.tool_calls:
            return msg.content
        messages.append({"role": "assistant", "content": msg.content,
                         "tool_calls": [{"id": c.id, "type": "function", "function": {"name": c.function.name, "arguments": c.function.arguments}}
                                        for c in msg.tool_calls]})
        for call in msg.tool_calls:
            result = run_tool(call.function.name, json.loads(call.function.arguments or "{}"))
            messages.append({"role": "tool", "tool_call_id": call.id, "content": result})
    return f"stopped: reached max steps ({max_steps})"


if __name__ == "__main__":
    answer = run(sys.argv[1])
    print(answer)
    sys.exit(2 if answer.startswith("stopped: reached max steps") else 0)

EOF
python -c "import json; from openai import OpenAI; from compact import compact; h = compact(json.load(open('history.json')), OpenAI()); print(len(h), 'messages'); print(h[2]['content'])"
```

</details>

## Check your work

```bash
D=/root/harness-lab/18-compact; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/compact.py 2>/dev/null && [ -s $D/compact.py ] && echo "✅ compact.py reads the key from the environment" || echo "❌ compact.py must not contain a key - let the SDK read it from the environment"
python - <<'PYEOF'
import json, math, os, subprocess, sys
from pathlib import Path
from openai import OpenAI
_C = OpenAI()
sys.excepthook = lambda t, e, tb: print(f"❌ check stopped: {t.__name__}: {e}")
def E(xs):
    return [d.embedding for d in _C.embeddings.create(model="lab-embed", input=xs).data]
def cos(a, b):
    return sum(x * y for x, y in zip(a, b)) / math.sqrt(sum(x * x for x in a) * sum(y * y for y in b))
def ok(cond, good, bad):
    print(("✅ " + good) if cond else ("❌ " + bad))
def load(p):
    try:
        return json.loads(Path(p).read_text())
    except Exception:
        return None
def run(*args, cwd=None):
    r = subprocess.run([sys.executable, *args], capture_output=True, text=True, cwd=cwd)
    return r.returncode, r.stdout.strip(), r.stderr.strip()
sys.path.insert(0, '/opt/harness')
from labmock import MockModel
def valid(h):
    pending = set()
    for x in h:
        if x.get("role") == "tool":
            if x.get("tool_call_id") not in pending:
                return False
            pending.discard(x["tool_call_id"])
        else:
            if pending:
                return False
            pending = {c["id"] for c in x.get("tool_calls") or []}
    return not pending

sys.path.insert(0, ".")
from openai import OpenAI
def turn(i, n, tag):
    return [{"role": "assistant", "content": None, "tool_calls": [{"id": f"c{i}", "type": "function", "function": {"name": "read_file", "arguments": json.dumps({"path": f"logs/part{i}.log"})}}]},
            {"role": "tool", "tool_call_id": f"c{i}", "content": tag + " " + "x" * n}]
head = [{"role": "system", "content": "S"}, {"role": "user", "content": "task"}]
try:
    import compact as C
    with MockModel(rules=[{"match": "summari", "on": "system", "steps": ["Read part1-part3; the slowest so far is 299ms in part2.log."]}]) as m:
        cl = OpenAI(base_url=m.url, api_key="mock")
        small = head + turn(1, 100, "T1")
        ok(C.compact(small, cl) == small and not m.requests, "a history under the limit comes back unchanged, with no model call", f"expected no change and no request - got {len(m.requests)} request(s)")
        big = head + [x for i in range(1, 6) for x in turn(i, 1500, f"T{i}")]
        r = C.compact(big, cl)
        req = m.requests[-1] if m.requests else {}
        sysm = [x.get("content", "") for x in req.get("messages", []) if x.get("role") == "system"]
        ok(len(m.requests) == 1 and req.get("model") == "lab-mini" and sysm and "summari" in sysm[0].lower(), "old turns go to lab-mini with a summarizer system prompt", f"expected one lab-mini call whose system prompt mentions summarizing - got {[(x.get('model'), len(x.get('messages', []))) for x in m.requests]}")
        sent = json.dumps(req.get("messages", []))
        ok(all(f"T{i} " in sent for i in (1, 2, 3)) and "T4 " not in sent and "T5 " not in sent, "the summarizer gets the old turns, not the last two", "send turns 1-3 to the summarizer and keep turns 4-5 out of it")
        ok(r[:2] == head and len(r) == 7 and r[2].get("role") == "user" and str(r[2].get("content")).startswith("[summary of earlier steps]") and "299ms in part2.log" in r[2]["content"] and r[3:] == big[-4:] and valid(r),
           "the result is system + task + one summary message + the last two turns", f"got roles {[x.get('role') for x in r]}, third message {str(r[2:3])[:120]}")
        n = len(m.requests)
        r2 = C.compact(r + [x for i in range(6, 9) for x in turn(i, 1500, f"T{i}")], cl)
        sent2 = json.dumps(m.requests[-1]["messages"]) if len(m.requests) > n else ""
        ok(sum(1 for x in r2 if str(x.get("content") or "").startswith("[summary of earlier steps]")) == 1 and "299ms in part2.log" in sent2, "compacting again folds the old summary into the new one", "a second compaction should summarize the previous summary too, leaving a single summary message")
except Exception as e:
    ok(False, "", f"compact.py should define compact(messages, client, limit=6000, keep_last=2) - {type(e).__name__}: {e}")
script = [{"tool": "read_file", "args": {"path": f"logs/part{n}.log"}} for n in range(1, 7)] + ["The slowest request is 294ms."]
with MockModel(rules=[{"match": "summari", "on": "system", "steps": ["Read part1 to part4; slowest so far 294ms."]}, {"match": "", "by": "calls", "steps": script}]) as m:
    rc, out, err = m.run(["python", "agent.py", "Which log has the slowest request?"], timeout=40)
agent = [x for x in m.requests if x.get("model") == "lab-fast"]
ok(rc == 0 and len(agent) == 7 and any(x.get("model") == "lab-mini" for x in m.requests) and all(valid(x["messages"]) and x["messages"][1].get("content") == "Which log has the slowest request?" for x in agent)
   and any("[summary of earlier steps]" in json.dumps(x["messages"]) for x in agent), "the agent compacts during a long run and keeps every request valid", f"{len(agent)} agent calls, {len(m.requests) - len(agent)} summarizer calls, rc {rc}; {err[-200:]}")
PYEOF
jq -se 'any(.[]; .ok and .api == "chat.completions" and .model == "lab-mini" and (.client | startswith("OpenAI/Python")) and .roles == ["system", "user"] and .max_tokens == null)' /var/log/ailab/requests.jsonl >/dev/null 2>&1 && echo "✅ you compacted the saved history with lab-mini" || echo "❌ run the compaction on history.json - no lab-mini summarizer call in the gateway log"
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Compaction replaces old turns with a short summary instead of deleting them.
- Keep the system prompt, the task and the most recent turns verbatim; summarize whole older turns with a cheap model.
- Ask the summarizer for exact names, numbers and errors - a summary for the agent, not for a person.
