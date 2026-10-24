---
type: task
title: "Inspect the growing history"
minutes: 9
---

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
```

## What to build

Change `/root/harness-lab/10-history/agent.py`:

1. Append the assistant message as a **plain dict** (`role`, `content`, and `tool_calls` with `id`, `type`, `function.name`, `function.arguments` when present) instead of the SDK object.
2. Before each model call, print `step N: M messages, K chars` to **stderr**, where M is `len(messages)` and K is `len(json.dumps(messages))`.
3. Accept `--dump FILE` after the question: write the whole messages list to FILE as JSON. It must hold the final history, including the last assistant message.

```bash
cd /root/harness-lab/10-history
python agent.py "Which port does the billing service use?" --dump history.json
python -m json.tool history.json | head -40
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `print(..., file=sys.stderr)` keeps stdout for the answer.
- Append the assistant dict before checking for tool calls, so the final answer lands in the dump too.

</details>

<details><summary>Solution</summary>

```bash
cd /root/harness-lab/10-history
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


def as_dict(msg):
    d = {"role": "assistant", "content": msg.content}
    if msg.tool_calls:
        d["tool_calls"] = [{"id": c.id, "type": "function",
                            "function": {"name": c.function.name, "arguments": c.function.arguments}} for c in msg.tool_calls]
    return d


def run(question, max_steps=8, dump=None):
    client = OpenAI()
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": question}]
    for step in range(1, max_steps + 1):
        print(f"step {step}: {len(messages)} messages, {len(json.dumps(messages))} chars", file=sys.stderr)
        msg = client.chat.completions.create(model="lab-fast", tools=SCHEMAS, messages=messages).choices[0].message
        messages.append(as_dict(msg))
        if dump:
            Path(dump).write_text(json.dumps(messages, indent=1))
        if not msg.tool_calls:
            return msg.content
        for call in msg.tool_calls:
            result = run_tool(call.function.name, json.loads(call.function.arguments or "{}"))
            messages.append({"role": "tool", "tool_call_id": call.id, "content": result})
        if dump:
            Path(dump).write_text(json.dumps(messages, indent=1))
    return f"stopped: reached max steps ({max_steps})"


if __name__ == "__main__":
    dump = sys.argv[sys.argv.index("--dump") + 1] if "--dump" in sys.argv else None
    answer = run(sys.argv[1], dump=dump)
    print(answer)
    sys.exit(2 if answer.startswith("stopped: reached max steps") else 0)

EOF
python agent.py "Which port does the billing service use?" --dump history.json
python -m json.tool history.json | head -40
```

</details>

## Check your work

```bash
D=/root/harness-lab/10-history; cd $D 2>/dev/null || echo "❌ create $D"
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
script = [{"tool": "list_dir", "args": {"path": "services"}}, {"tool": "read_file", "args": {"path": "services/billing.yaml"}}, "Billing uses port 8081."]
Path("/tmp/h10.json").unlink(missing_ok=True)
with MockModel(script) as m:
    rc, out, err = m.run(["python", "agent.py", "Billing port?", "--dump", "/tmp/h10.json"])
ok(rc == 0 and out == "Billing uses port 8081.", "stdout is just the answer", f"stdout should hold only the answer - got {out[-200:]!r} {err[-200:]}")
steps = [l for l in err.splitlines() if l.startswith("step ")]
import re as _re
parsed = [tuple(int(x) for x in _re.findall(r"(\d+) messages, (\d+) chars", l)[0]) for l in steps if _re.search(r"\d+ messages, \d+ chars", l)]
ok(len(parsed) == 3 and [p[0] for p in parsed] == [2, 4, 6] and parsed[0][1] < parsed[1][1] < parsed[2][1], "stderr shows 3 steps with 2, 4, 6 messages and growing size", f"expected 'step N: M messages, K chars' lines on stderr with M = 2, 4, 6 - got {steps}")
if m.requests and parsed:
    ok(parsed[0][1] == len(json.dumps(m.requests[0]["messages"])), "the char count is len(json.dumps(messages))", f"step 1 should report {len(json.dumps(m.requests[0]['messages']))} chars - got {parsed[0][1]}")
h = load("/tmp/h10.json")
ok(isinstance(h, list) and [x.get("role") for x in h] == ["system", "user", "assistant", "tool", "assistant", "tool", "assistant"], "--dump writes the full final history, ending with the answer", f"the dump should be system, user, 2 x (assistant, tool), assistant - got {[x.get('role') for x in h] if isinstance(h, list) else h}")
if isinstance(h, list) and len(h) == 7:
    a = h[2]
    tc = (a.get("tool_calls") or [{}])[0]
    ok(tc.get("id") == "call_0_0" and tc.get("type") == "function" and tc.get("function", {}).get("name") == "list_dir" and json.loads(tc["function"]["arguments"]) == {"path": "services"}, "assistant tool calls are saved as plain dicts with id, type and function", f"assistant messages should hold tool_calls [{{id, type: function, function: {{name, arguments}}}}] - got {a}")
    ok(h[3].get("tool_call_id") == "call_0_0" and "billing.yaml" in h[3].get("content", "") and h[6].get("content") == "Billing uses port 8081.", "tool results and the final answer are in the dump", f"got tool {h[3]} and last {h[6]}")
PYEOF
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- The messages list is the agent's entire memory, re-sent on every call.
- Store assistant messages as plain dicts so the history can be saved, diffed and reloaded.
- Logging message count and size per step shows the growth before it becomes a problem.
