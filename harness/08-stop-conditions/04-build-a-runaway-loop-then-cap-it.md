---
type: task
title: "Build a runaway loop, then cap it"
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

**Part 1 - build a runaway.** Write `/root/harness-lab/08-stop/runaway.json`, a labmock script (a JSON list of steps) for a model that **never stops**: every reply is a `list_dir` call on `.`. Remember that labmock repeats the last step forever.

Watch the uncapped topic 07 loop spin (press Ctrl+C after a few seconds):

```bash
cd /root/harness-lab/08-stop
python /opt/harness/labmock.py runaway.json --port 4599 &
OPENAI_BASE_URL=http://127.0.0.1:4599/v1 OPENAI_API_KEY=mock timeout 5 python agent.py "List the workspace" ; echo "exit: $?"
kill %1
```

**Part 2 - cap it.** Change `agent.py`:

1. `run(question, max_steps=8)` makes at most `max_steps` model calls.
2. If the limit is reached, `run` returns `stopped: reached max steps (N)`.
3. The command line accepts `--max-steps N` after the question, defaulting to 8.
4. When the run was stopped by the limit, print the message and exit with status **2**; a normal answer exits with **0**.

Keep the `finish` tool from the previous task if you built it - the checker accepts either an answer from `finish` or a plain text answer.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- A one-step script is enough: `[{"tool": "list_dir", "args": {"path": "."}}]`.
- `for step in range(max_steps):` instead of `while True:`.
- `sys.exit(2)` after printing when the result starts with `stopped: reached max steps`.

</details>

<details><summary>Solution</summary>

```bash
cd /root/harness-lab/08-stop
cat > runaway.json <<'EOF'
[{"tool": "list_dir", "args": {"path": "."}}]
EOF
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
    limit = int(sys.argv[sys.argv.index("--max-steps") + 1]) if "--max-steps" in sys.argv else 8
    answer = run(sys.argv[1], max_steps=limit)
    print(answer)
    sys.exit(2 if answer.startswith("stopped: reached max steps") else 0)

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
spec = load("runaway.json")
last = spec[-1] if isinstance(spec, list) and spec else {}
ok(isinstance(last, dict) and (last.get("tool") or (last.get("calls") or [{}])[0].get("tool")) and last.get("tool") != "finish", "runaway.json ends with a repeating tool call", f"runaway.json should be a list whose last step is a tool call (not finish) - got {spec}")
if isinstance(spec, list) and spec:
    with MockModel(spec) as m:
        rc, out, err = m.run(["python", "agent.py", "List the workspace"], timeout=20)
    ok(rc == 2 and out.endswith("stopped: reached max steps (8)") and len(m.requests) == 8, "your runaway script is stopped after 8 calls with exit status 2", f"against runaway.json the agent should make 8 calls, print 'stopped: reached max steps (8)' and exit 2 - got rc {rc}, {len(m.requests)} calls, {out[-120:]!r} {err[-200:]}")
with MockModel([{"tool": "list_dir", "args": {"path": "services"}}]) as m:
    rc, out, err = m.run(["python", "agent.py", "x", "--max-steps", "3"], timeout=20)
ok(rc == 2 and out.endswith("stopped: reached max steps (3)") and len(m.requests) == 3, "--max-steps 3 stops after 3 calls", f"--max-steps 3 should stop after 3 calls with exit 2 - got rc {rc}, {len(m.requests)} calls, {out[-120:]!r}")
with MockModel([{"tool": "read_file", "args": {"path": "services/billing.yaml"}}, {"tool": "finish", "args": {"answer": "Billing uses port 8081."}}, "Billing uses port 8081."]) as m:
    rc, out, err = m.run(["python", "agent.py", "Billing port?"], timeout=20)
ok(rc == 0 and out.strip().endswith("Billing uses port 8081.") and len(m.requests) <= 3, "a normal run still answers and exits 0", f"a normal 2-step run should print the answer and exit 0 - got rc {rc}, {out[-120:]!r} {err[-200:]}")
PYEOF
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- labmock can script a model that never stops - the fastest way to test a stop condition.
- The harness owns the step limit; hitting it returns a clear 'stopped' result and a non-zero exit status.
- Size limits from traces of good runs, and pair them with token budgets.
