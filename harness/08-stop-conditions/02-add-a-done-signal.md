---
type: task
title: "Add a done signal"
minutes: 9
---

## Set up

```bash
mkdir -p /root/harness-lab/08-stop/workspace/services
cd /root/harness-lab/08-stop
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
echo 'agent.py is the loop from topic 07'
```

## What to build

Change `/root/harness-lab/08-stop/agent.py` so the agent ends only through a `finish` tool:

1. Add a `finish` tool with one required string argument `answer` (append it to `SCHEMAS`).
2. In the loop:
   - if any tool call is `finish`, return its `answer` immediately;
   - otherwise run the tool calls as before;
   - if the reply is plain text with no tool calls, append it as an assistant message, then append a user message `Call finish with your final answer when you are done.` and loop again.
3. After **2** nudges without a `finish`, return the text `stopped: no finish after 2 nudges`.

```bash
cd /root/harness-lab/08-stop
python agent.py "Which port does the billing service use?"
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `fin = next((c for c in msg.tool_calls or [] if c.function.name == "finish"), None)`.
- Append plain text as `{"role": "assistant", "content": msg.content}`.

</details>

<details><summary>Solution</summary>

```bash
cd /root/harness-lab/08-stop
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

FINISH = {"type": "function", "function": {
    "name": "finish",
    "description": "Call this exactly once, when the task is complete, with your final answer for the user.",
    "parameters": {"type": "object", "properties": {
        "answer": {"type": "string", "description": "The final answer, complete and self-contained"}},
        "required": ["answer"]}}}
SCHEMAS.append(FINISH)


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
    nudges = 0
    while True:
        msg = client.chat.completions.create(model="lab-fast", tools=SCHEMAS, messages=messages).choices[0].message
        fin = next((c for c in msg.tool_calls or [] if c.function.name == "finish"), None)
        if fin:
            return json.loads(fin.function.arguments or "{}").get("answer", "")
        if not msg.tool_calls:
            if nudges == 2:
                return "stopped: no finish after 2 nudges"
            nudges += 1
            messages.append({"role": "assistant", "content": msg.content or ""})
            messages.append({"role": "user", "content": "Call finish with your final answer when you are done."})
            continue
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
D=/root/harness-lab/08-stop; cd $D 2>/dev/null || echo "❌ create $D"
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
script = ["Let me look at the services folder first.", {"tool": "read_file", "args": {"path": "services/billing.yaml"}},
          {"tool": "finish", "args": {"answer": "Billing uses port 8081."}}]
with MockModel(script) as m:
    rc, out, err = m.run(["python", "agent.py", "Billing port?"])
ok(rc == 0 and out == "Billing uses port 8081.", "the agent returns the finish answer, not the thinking-out-loud text", f"expected the finish answer 'Billing uses port 8081.' - got {out[-200:]!r} {err[-300:]}")
names = sorted(((t.get("function") or {}).get("name")) for t in (m.requests[0].get("tools") or [])) if m.requests else []
ok("finish" in names and "read_file" in names, "a finish tool is offered alongside the workspace tools", f"tools offered should include finish - got {names}")
msgs = m.requests[1]["messages"] if len(m.requests) > 1 else []
ok(len(m.requests) == 3 and [x.get("role") for x in msgs][-2:] == ["assistant", "user"] and msgs[-1].get("content") == "Call finish with your final answer when you are done.", "plain text gets appended plus the nudge, and the loop continues", f"after a text reply the next request should end with that assistant text and the nudge user message - got {[x.get('role') for x in msgs]}")
with MockModel(["Thinking...", "Still thinking...", "Hmm.", "Never finishing."]) as m:
    rc, out, err = m.run(["python", "agent.py", "x"], timeout=20)
ok(rc == 0 and out == "stopped: no finish after 2 nudges" and len(m.requests) == 3, "after 2 ignored nudges the agent stops", f"a model that never calls finish should get 2 nudges then 'stopped: no finish after 2 nudges' (3 calls) - got {out[-120:]!r} after {len(m.requests)} calls")
with MockModel([{"tool": "finish", "args": {"answer": "Nothing to do."}}]) as m:
    rc, out, err = m.run(["python", "agent.py", "x"])
ok(out == "Nothing to do." and len(m.requests) == 1, "finish on the first step ends after one call", f"got {out!r} after {len(m.requests)} calls")
PYEOF
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- A finish tool makes 'done' explicit; plain text becomes thinking out loud, not the end.
- Nudge a model that answers in text, but bound the nudges.
- A structured finish payload is something the harness can check before accepting.
