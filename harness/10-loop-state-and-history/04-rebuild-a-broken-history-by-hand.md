---
type: task
title: "Rebuild a broken history by hand"
minutes: 10
---

## Scenario

A teammate's harness crashed halfway through a run and saved its history to `broken.json`. They want to resume the run - but every request with this history is rejected.

## Set up

```bash
mkdir -p /root/harness-lab/10-history/workspace/services
cd /root/harness-lab/10-history
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
cat > broken.json <<'EOF'
[
 {
  "role": "system",
  "content": "You are Stackline's project assistant. Use the tools to look at the workspace before answering. Answer briefly."
 },
 {
  "role": "user",
  "content": "Compare the ports of billing and search."
 },
 {
  "role": "tool",
  "tool_call_id": "call_1",
  "content": "billing.yaml\nsearch.yaml"
 },
 {
  "role": "assistant",
  "content": null,
  "tool_calls": [
   {
    "id": "call_1",
    "type": "function",
    "function": {
     "name": "list_dir",
     "arguments": "{\"path\": \"services\"}"
    }
   }
  ]
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
     "arguments": "{\"path\": \"services/billing.yaml\"}"
    }
   }
  ]
 },
 {
  "role": "tool",
  "tool_call_id": "call_9",
  "content": "name: billing\nport: 8081\nowner: payments team\nreplicas: 3\n"
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
     "arguments": "{\"path\": \"services/search.yaml\"}"
    }
   },
   {
    "id": "call_4",
    "type": "function",
    "function": {
     "name": "read_file",
     "arguments": "{\"path\": \"README.md\"}"
    }
   }
  ]
 },
 {
  "role": "tool",
  "tool_call_id": "call_4",
  "content": "# Stackline services\nTwo services run in production: billing and search.\nConfig lives in services/<name>.yaml.\n"
 }
]
EOF
```

## What to build

Read `/root/harness-lab/10-history/broken.json` and write a repaired copy to `/root/harness-lab/10-history/fixed.json`. It has **three** structural problems. Your fixed history must:

1. Keep every message from `broken.json` (same contents), in a valid order.
2. Have every assistant tool call answered by **exactly one** tool message with the matching `tool_call_id`, right after that assistant message and before anything else.
3. Have no tool message that doesn't answer a call.
4. Fill in the one missing result with the **real** output of that call - read the file from `workspace/` yourself.

Then prove the API accepts it - send it to `lab-fast` and let the model continue the task:

```bash
cd /root/harness-lab/10-history
python - <<'EOF'
import json
from openai import OpenAI
from agent import SCHEMAS
msgs = json.load(open("fixed.json"))
r = OpenAI().chat.completions.create(model="lab-fast", tools=SCHEMAS, messages=msgs)
print(r.choices[0].message.content or r.choices[0].message.tool_calls)
EOF
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Look at the order of messages 2 and 3, the id on message 5, and which ids message 6 asks for.
- Two calls in one assistant message need two tool messages after it - in either order.
- You can edit the JSON by hand, or load it in Python, fix the list and `json.dump` it.

</details>

<details><summary>Solution</summary>

```bash
cd /root/harness-lab/10-history
cat > fixed.json <<'EOF'
[
 {
  "role": "system",
  "content": "You are Stackline's project assistant. Use the tools to look at the workspace before answering. Answer briefly."
 },
 {
  "role": "user",
  "content": "Compare the ports of billing and search."
 },
 {
  "role": "assistant",
  "content": null,
  "tool_calls": [
   {
    "id": "call_1",
    "type": "function",
    "function": {
     "name": "list_dir",
     "arguments": "{\"path\": \"services\"}"
    }
   }
  ]
 },
 {
  "role": "tool",
  "tool_call_id": "call_1",
  "content": "billing.yaml\nsearch.yaml"
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
     "arguments": "{\"path\": \"services/billing.yaml\"}"
    }
   }
  ]
 },
 {
  "role": "tool",
  "tool_call_id": "call_2",
  "content": "name: billing\nport: 8081\nowner: payments team\nreplicas: 3\n"
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
     "arguments": "{\"path\": \"services/search.yaml\"}"
    }
   },
   {
    "id": "call_4",
    "type": "function",
    "function": {
     "name": "read_file",
     "arguments": "{\"path\": \"README.md\"}"
    }
   }
  ]
 },
 {
  "role": "tool",
  "tool_call_id": "call_3",
  "content": "name: search\nport: 9200\nowner: discovery team\nreplicas: 5\n"
 },
 {
  "role": "tool",
  "tool_call_id": "call_4",
  "content": "# Stackline services\nTwo services run in production: billing and search.\nConfig lives in services/<name>.yaml.\n"
 }
]
EOF
python - <<'EOF'
import json
from openai import OpenAI
from agent import SCHEMAS
msgs = json.load(open("fixed.json"))
r = OpenAI().chat.completions.create(model="lab-fast", tools=SCHEMAS, messages=msgs)
print(r.choices[0].message.content or r.choices[0].message.tool_calls)
EOF
```

</details>

## Check your work

```bash
D=/root/harness-lab/10-history; cd $D 2>/dev/null || echo "❌ create $D"
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
h, b = load("fixed.json"), load("broken.json")
def problems(h):
    out, pending = [], set()
    for i, x in enumerate(h):
        r = x.get("role")
        if r == "tool":
            if x.get("tool_call_id") not in pending:
                out.append(f"message {i}: tool result {x.get('tool_call_id')} doesn't answer a pending call")
            pending.discard(x.get("tool_call_id"))
            continue
        if pending:
            out.append(f"message {i}: calls {sorted(pending)} were never answered")
            pending = set()
        if r == "assistant":
            pending = {c["id"] for c in x.get("tool_calls") or []}
    if pending:
        out.append(f"end: calls {sorted(pending)} were never answered")
    return out
ok(isinstance(h, list) and len(h) > 0, "fixed.json is a JSON list of messages", "write the repaired history to fixed.json as a JSON list")
if isinstance(h, list) and b:
    p = problems(h)
    ok(not p, "every tool call is answered exactly once, right after its assistant message", f"fixed.json is still invalid: {p[:3]}")
    key = lambda x: (x.get("role"), x.get("content"), json.dumps(x.get("tool_calls"), sort_keys=True))
    kept = [key(x) for x in b if x.get("role") != "tool"]
    ok([key(x) for x in h if x.get("role") != "tool"] == kept, "system, user and assistant messages are all kept, in their original order", "every non-tool message from broken.json should be kept with the same content and order")
    res = {x.get("tool_call_id"): x.get("content") for x in h if x.get("role") == "tool"}
    want = {"call_1": "billing.yaml\nsearch.yaml", "call_2": Path("workspace/services/billing.yaml").read_text(),
            "call_3": Path("workspace/services/search.yaml").read_text(), "call_4": Path("workspace/README.md").read_text()}
    ok(res.get("call_1") == want["call_1"] and res.get("call_2") == want["call_2"] and res.get("call_4") == want["call_4"], "the existing results are kept and attached to the right calls", f"the results for call_1, call_2 and call_4 should be the original contents - got {list(res)}")
    ok(res.get("call_3") == want["call_3"], "the missing result is the real contents of services/search.yaml", "call_3 read services/search.yaml - its result should be that file's exact text")
    try:
        sys.path.insert(0, ".")
        from agent import SCHEMAS
        r = _C.chat.completions.create(model="lab-fast", tools=SCHEMAS, messages=h)
        ok(bool(r.choices), "the gateway accepts fixed.json as a history", "")
    except Exception as e:
        ok(False, "", f"the gateway rejected fixed.json: {str(e)[:200]}")
PYEOF
```

## What you learned

- Each assistant tool-call message must be followed by exactly one result per call id, before anything else.
- Most broken histories are ordering, id, or missing-result bugs - all fixable without starting over.
- Fill a lost result by re-running a safe read-only call, never by inventing one.
