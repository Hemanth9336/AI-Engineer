---
type: task
title: "Enforce a per-task token budget"
minutes: 10
---

## Set up

```bash
mkdir -p /root/harness-lab/32-cost/workspace/services
cd /root/harness-lab/32-cost
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

Change `/root/harness-lab/32-cost/agent.py`:

1. Arguments: `python agent.py "question" [--max-steps N] [--budget-tokens N]` (defaults 8 and 50,000).
2. Track `spent` = the sum of `prompt_tokens + completion_tokens` from every response.
3. **Before** every call except the first, if `spent + <the last call's prompt_tokens>` would exceed the budget, stop and return `stopped: token budget reached (<spent> of <budget> tokens used)`.
4. Exit codes: **4** for the budget, **2** for max steps, 0 when done.

```bash
cd /root/harness-lab/32-cost
python agent.py "Which port does the billing service use?" --budget-tokens 20000
python agent.py "Which port does the billing service use?" --budget-tokens 10; echo "exit $?"
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `resp.usage` is on the response, so keep the response, not just `.choices[0].message`.
- The first call always runs - you can't know its cost before it happens.

</details>

<details><summary>Solution</summary>

```bash
cd /root/harness-lab/32-cost
cat > agent.py <<'EOF'
import argparse
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


def run(question, max_steps=8, budget=50000):
    client = OpenAI()
    spent, last_prompt = 0, 0
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": question}]
    for _ in range(max_steps):
        if spent and spent + last_prompt > budget:
            return f"stopped: token budget reached ({spent} of {budget} tokens used)"
        resp = client.chat.completions.create(model="lab-fast", tools=SCHEMAS, messages=messages)
        spent += resp.usage.prompt_tokens + resp.usage.completion_tokens
        last_prompt = resp.usage.prompt_tokens
        msg = resp.choices[0].message
        if not msg.tool_calls:
            return msg.content
        messages.append(msg)
        for call in msg.tool_calls:
            result = run_tool(call.function.name, json.loads(call.function.arguments or "{}"))
            messages.append({"role": "tool", "tool_call_id": call.id, "content": result})
    return f"stopped: reached max steps ({max_steps})"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("question")
    ap.add_argument("--max-steps", type=int, default=8)
    ap.add_argument("--budget-tokens", type=int, default=50000)
    a = ap.parse_args()
    answer = run(a.question, a.max_steps, a.budget_tokens)
    print(answer)
    sys.exit(4 if answer.startswith("stopped: token budget") else 2 if answer.startswith("stopped: reached max steps") else 0)

EOF
python agent.py "Which port does the billing service use?" --budget-tokens 20000
python agent.py "Which port does the billing service use?" --budget-tokens 10 || echo "stopped with exit $?"
```

</details>

## Check your work

```bash
D=/root/harness-lab/32-cost; cd $D 2>/dev/null || echo "❌ create $D"
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
step = {"tool": "list_dir", "args": {"path": "."}, "usage": [1000, 50]}
with MockModel([step] * 5 + [{"text": "done", "usage": [1000, 50]}]) as m:
    rc, out, err = m.run(["python", "agent.py", "go", "--budget-tokens", "2500"], timeout=30)
ok(rc == 4 and len(m.requests) == 2 and out.endswith("stopped: token budget reached (2100 of 2500 tokens used)"), "with a 2,500-token budget the agent stops before a third call would cross it (exit 4)", f"exit {rc}, {len(m.requests)} calls, output {out[-90:]!r}; {err[-150:]}")
with MockModel([step, step, {"text": "done", "usage": [1000, 50]}]) as m:
    rc, out, err = m.run(["python", "agent.py", "go", "--budget-tokens", "10000"], timeout=30)
ok(rc == 0 and out.endswith("done") and len(m.requests) == 3, "a run inside the budget finishes normally", f"exit {rc}, output {out[-60:]!r}")
with MockModel([{"tool": "list_dir", "args": {"path": "."}, "usage": [10, 5]}]) as m:
    rc, out, err = m.run(["python", "agent.py", "go", "--max-steps", "3"], timeout=30)
ok(rc == 2 and len(m.requests) == 3, "--max-steps still works (exit 2)", f"exit {rc}, {len(m.requests)} calls")
with MockModel([{"text": "hi", "usage": [99999, 5]}]) as m:
    rc, out, err = m.run(["python", "agent.py", "go", "--budget-tokens", "10"], timeout=30)
ok(rc == 0 and len(m.requests) == 1, "the first call always runs", f"exit {rc}, {len(m.requests)} calls")
PYEOF
jq -se 'any(.[]; .ok and .api == "chat.completions" and .model == "lab-fast" and (.client | startswith("OpenAI/Python")))' /var/log/ailab/requests.jsonl >/dev/null 2>&1 && echo "✅ you ran the budgeted agent on the real model" || echo "❌ run agent.py against the gateway"
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Step limits stop endless loops; token budgets stop expensive ones.
- Check the budget before each call, using actual usage and the last prompt size as the estimate.
- Stop with a distinct status and exit code, and set the budget from eval data.
