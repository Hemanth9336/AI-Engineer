---
type: task
title: "Define a file-read tool"
minutes: 9
---

## Set up

```bash
mkdir -p /root/harness-lab/06-tools
```

## What to build

1. In `/root/harness-lab/06-tools/tools.py`, define `READ_FILE_TOOL` for a function `read_file` with one required string argument `path`. Write a description that says what it does and when to use it.
2. Write `ask_tool.py`, used as `python ask_tool.py QUESTION`, that sends QUESTION to `lab-fast` with `tools=[READ_FILE_TOOL]` and prints **one JSON line**:
   - `{"name": ..., "arguments": {...}}` if the model returned a tool call (arguments parsed from the JSON string), or
   - `{"name": null, "answer": "<text>"}` if it answered directly.

Don't run the tool yet - just see what the model asks for.

```bash
cd /root/harness-lab/06-tools
python ask_tool.py "What does notes/todo.txt say?"
python ask_tool.py "What is 12 times 12?"
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `from tools import READ_FILE_TOOL`.
- `json.loads(call.function.arguments)` turns the argument string into a dict.
- Let `OpenAI()` read the gateway URL and key from the environment - the checker points it at labmock the same way.

</details>

<details><summary>Solution</summary>

```bash
cd /root/harness-lab/06-tools
cat > tools.py <<'EOF'
READ_FILE_TOOL = {
    "type": "function",
    "function": {
        "name": "read_file",
        "description": "Read a text file from the project and return its contents. Use it whenever the answer depends on what a file says.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path relative to the project folder, for example notes/todo.txt"},
            },
            "required": ["path"],
        },
    },
}
EOF
cat > ask_tool.py <<'EOF'
import json
import sys

from openai import OpenAI

from tools import READ_FILE_TOOL

resp = OpenAI().chat.completions.create(model="lab-fast", tools=[READ_FILE_TOOL], messages=[{"role": "user", "content": sys.argv[1]}])
msg = resp.choices[0].message
if msg.tool_calls:
    call = msg.tool_calls[0]
    print(json.dumps({"name": call.function.name, "arguments": json.loads(call.function.arguments)}))
else:
    print(json.dumps({"name": None, "answer": msg.content}))
EOF
python ask_tool.py "What does notes/todo.txt say?"
python ask_tool.py "What is 12 times 12?"
```

</details>

## Check your work

```bash
D=/root/harness-lab/06-tools; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/ask_tool.py 2>/dev/null && [ -s $D/ask_tool.py ] && echo "✅ ask_tool.py reads the key from the environment" || echo "❌ ask_tool.py must not contain a key - let the SDK read it from the environment"
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
sys.path.insert(0, ".")
try:
    from tools import READ_FILE_TOOL as W
    f = W["function"]
    p = f["parameters"]
    good = (W.get("type") == "function" and f.get("name") == "read_file" and len(f.get("description", "")) >= 20 and p.get("type") == "object"
            and p["properties"]["path"]["type"] == "string" and p.get("required") == ["path"])
except Exception as e:
    good = False
ok(good, "READ_FILE_TOOL defines read_file with a required string path and a real description", "READ_FILE_TOOL should be a function tool named read_file, with a description of 20+ characters and required [path] of type string")
def ask(script, q):
    with MockModel(script) as m:
        rc, out, err = m.run(["python", "ask_tool.py", q])
    try:
        return json.loads(out), m.requests
    except ValueError:
        return {"error": out[:150] + err[-150:]}, m.requests
r, reqs = ask([{"tool": "read_file", "args": {"path": "config/app.yaml"}}], "What port is set in config/app.yaml?")
ok(r == {"name": "read_file", "arguments": {"path": "config/app.yaml"}}, "a scripted tool call is printed as name plus parsed arguments", f"for a read_file call expected {{'name': 'read_file', 'arguments': {{'path': 'config/app.yaml'}}}} - got {r}")
sent = [((t.get("function") or {}).get("name")) for t in (reqs[0].get("tools") or [])] if reqs else []
ok(sent == ["read_file"], "ask_tool.py offers exactly the read_file tool", f"the request should offer tools=[READ_FILE_TOOL] - it offered {sent}")
r, _ = ask(["12 times 12 is 144."], "What is 12 times 12?")
ok(r == {"name": None, "answer": "12 times 12 is 144."}, "a direct answer prints name null and the text", f"a plain reply should print {{'name': None, 'answer': ...}} - got {r}")
rows = [json.loads(l) for l in open("/var/log/ailab/requests.jsonl")]
ok(any(x.get("model") == "lab-fast" and "read_file" in (x.get("tools") or []) and x.get("client", "").startswith("OpenAI/Python") for x in rows), "the gateway logged your real lab-fast call offering read_file", "run ask_tool.py against the lab gateway at least once - no lab-fast call offering read_file yet")
PYEOF
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- A tool is a name, a description that says when to use it, and a JSON Schema for its arguments.
- The reply is either text or a tool call whose arguments are a JSON string you must parse.
- A scripted stand-in model makes harness behavior testable - the code can't tell it from a real one.
