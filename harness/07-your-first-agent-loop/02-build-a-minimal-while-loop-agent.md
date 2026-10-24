---
type: task
title: "Build a minimal while-loop agent"
minutes: 11
---

## Set up

`workspace/` is a tiny project: a README and one config file per service. Your agent may only look at it through its tools.

```bash
mkdir -p /root/harness-lab/07-loop/workspace/services
cd /root/harness-lab/07-loop
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
```

## What to build

Write `/root/harness-lab/07-loop/agent.py`, used as `python agent.py QUESTION`:

1. Two tools, with schemas in a list called `SCHEMAS`:
   - `list_dir(path)` - the names inside `workspace/<path>`, sorted, one per line, folders ending in `/`; or `error: no such folder <path>`.
   - `read_file(path)` - the text of `workspace/<path>`; or `error: no such file <path>`.
2. A `run_tool(name, args)` that dispatches from a dict and returns `error: unknown tool <name>` for anything else.
3. A function `run(question)` with the loop from the lesson: a system message, the user question, then call `lab-fast` with `tools=SCHEMAS` until the reply has no tool calls, and return its text.
4. `print(run(sys.argv[1]))` under `if __name__ == "__main__":`.

```bash
cd /root/harness-lab/07-loop
python agent.py "Which port does the billing service use?"
```

The checker replays a scripted model that takes three tool steps before answering, and checks every request your loop sends.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `WORK = Path(__file__).parent / "workspace"`, then `WORK / path`.
- `sorted(c.name + ("/" if c.is_dir() else "") for c in p.iterdir())`.
- `json.loads(call.function.arguments or "{}")` copes with a tool call that has no arguments.

</details>

<details><summary>Solution</summary>

```bash
cd /root/harness-lab/07-loop
cat > agent.py <<'EOF'
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


def run(question):
    client = OpenAI()
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": question}]
    while True:
        msg = client.chat.completions.create(model="lab-fast", tools=SCHEMAS, messages=messages).choices[0].message
        if not msg.tool_calls:
            return msg.content
        messages.append(msg)
        for call in msg.tool_calls:
            result = run_tool(call.function.name, json.loads(call.function.arguments or "{}"))
            messages.append({"role": "tool", "tool_call_id": call.id, "content": result})


if __name__ == "__main__":
    print(run(sys.argv[1]))

EOF
python agent.py "Which port does the billing service use?"
```

</details>

## Check your work

```bash
D=/root/harness-lab/07-loop; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/agent.py 2>/dev/null && [ -s $D/agent.py ] && echo "✅ agent.py reads the key from the environment" || echo "❌ agent.py must not contain a key - let the SDK read it from the environment"
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
script = [{"tool": "list_dir", "args": {"path": "."}}, {"tool": "list_dir", "args": {"path": "services"}},
          {"tool": "read_file", "args": {"path": "services/search.yaml"}}, "Search runs on port 9200."]
with MockModel(script) as m:
    rc, out, err = m.run(["python", "agent.py", "Which port does search use?"])
ok(rc == 0 and out == "Search runs on port 9200.", "agent.py loops through three tool steps and prints the answer", f"agent.py should keep calling the model until it answers - got {out[-200:]!r} {err[-300:]}")
ok(len(m.requests) == 4, "four model calls: three tool steps and the answer", f"expected 4 model calls - labmock saw {len(m.requests)}")
last = m.requests[-1]["messages"] if m.requests else []
roles = [x.get("role") for x in last]
ok(roles == ["system", "user", "assistant", "tool", "assistant", "tool", "assistant", "tool"], "the last request carries the whole history in order", f"the 4th request should be system, user, then 3 x (assistant, tool) - got {roles}")
tools = [x.get("content", "") for x in last if x.get("role") == "tool"]
ok(len(tools) == 3 and "README.md" in tools[0] and "services/" in tools[0] and tools[1].split() == ["billing.yaml", "search.yaml"] and "port: 9200" in tools[2],
   "list_dir and read_file return the right workspace contents", f"tool results should be the sorted listing (folders with /) and the file text - got {[t[:60] for t in tools]}")
sent = sorted(((t.get("function") or {}).get("name")) for t in (m.requests[0].get("tools") or [])) if m.requests else []
ok(sent == ["list_dir", "read_file"], "every call offers list_dir and read_file", f"tools offered should be list_dir and read_file - got {sent}")
with MockModel([{"tool": "read_file", "args": {"path": "nope.txt"}}, {"tool": "delete_everything", "args": {}}, "Done."]) as m:
    rc, out, err = m.run(["python", "agent.py", "x"])
tools = [x.get("content", "") for x in (m.requests[-1]["messages"] if m.requests else []) if x.get("role") == "tool"]
ok(rc == 0 and len(tools) == 2 and tools[0].startswith("error") and "unknown tool" in tools[1], "missing files and unknown tools come back as error results", f"expected error results for a missing file and an unknown tool - got {tools} {err[-200:]}")
rows = [json.loads(l) for l in open("/var/log/ailab/requests.jsonl")]
ok(any(x.get("model") == "lab-fast" and sorted(x.get("tools") or []) == ["list_dir", "read_file"] and x.get("client", "").startswith("OpenAI/Python") for x in rows), "the gateway logged your agent's real lab-fast calls", "run agent.py against the lab gateway at least once")
PYEOF
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- An agent loop is a tool cycle repeated until the model answers instead of calling a tool.
- Each request carries the full history: system, user, then assistant and tool messages in order.
- The model chooses the number of steps - which is why the harness must later bound it.
