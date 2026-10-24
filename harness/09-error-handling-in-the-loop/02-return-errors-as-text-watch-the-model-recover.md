---
type: task
title: "Return errors as text, watch the model recover"
minutes: 9
---

## Set up

`ops.py` is a tiny service API: `get_service(name)` raises `KeyError` for unknown names, and `restart_count(name, days)` raises `ValueError` when `days` is over 30.

```bash
mkdir -p /root/harness-lab/09-errors/workspace/services
cd /root/harness-lab/09-errors
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
cat > ops.py <<'EOF'
"""Stackline's internal service API, as Python functions. They raise on bad input - like most real code."""
SERVICES = {"billing": {"port": 8081, "status": "healthy"}, "search": {"port": 9200, "status": "degraded"}}
RESTARTS_PER_WEEK = {"billing": 2, "search": 7}


def get_service(name):
    return SERVICES[name]


def restart_count(name, days):
    if days > 30:
        raise ValueError("days must be 30 or less")
    return RESTARTS_PER_WEEK[name] * days // 7
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

Change `/root/harness-lab/09-errors/agent.py`:

1. Add two tools backed by `ops.py`: `get_service(name)` and `restart_count(name, days)` (an integer). Return their results as strings.
2. Make `run_tool` catch **any** exception from a tool and return `error: <ExceptionName>: <message>`, for example `error: KeyError: 'payments'`.
3. If a tool call's arguments aren't valid JSON, don't crash: send back a result starting `error: arguments were not valid JSON`.
4. Unknown tools keep returning `error: unknown tool <name>`.

```bash
cd /root/harness-lab/09-errors
python agent.py "Which port does the payments service use?"
```

The checker scripts a model that hits all four kinds of error in one run, then answers. Your agent must survive them all.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `except Exception as e: return f"error: {type(e).__name__}: {e}"`.
- Wrap `json.loads(call.function.arguments)` in its own `try` / `except json.JSONDecodeError`.
- Every tool call still needs exactly one tool message - including the failed ones.

</details>

<details><summary>Solution</summary>

```bash
cd /root/harness-lab/09-errors
cat > agent.py <<'EOF'
import json
import sys
from pathlib import Path

from openai import OpenAI

from ops import get_service, restart_count

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
SCHEMAS += [
    {"type": "function", "function": {
        "name": "get_service",
        "description": "Get the port and health status of a Stackline service by name.",
        "parameters": {"type": "object", "properties": {"name": {"type": "string", "description": "Service name, for example billing"}},
                       "required": ["name"]}}},
    {"type": "function", "function": {
        "name": "restart_count",
        "description": "How many times a service restarted in the last N days (N at most 30).",
        "parameters": {"type": "object", "properties": {"name": {"type": "string"}, "days": {"type": "integer"}},
                       "required": ["name", "days"]}}},
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


IMPL = {"list_dir": list_dir, "read_file": read_file, "get_service": get_service, "restart_count": restart_count}


def run_tool(name, args):
    if name not in IMPL:
        return f"error: unknown tool {name}"
    try:
        return str(IMPL[name](**args))
    except Exception as e:
        return f"error: {type(e).__name__}: {e}"


def run(question, max_steps=8):
    client = OpenAI()
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": question}]
    for _ in range(max_steps):
        msg = client.chat.completions.create(model="lab-fast", tools=SCHEMAS, messages=messages).choices[0].message
        if not msg.tool_calls:
            return msg.content
        messages.append(msg)
        for call in msg.tool_calls:
            try:
                args = json.loads(call.function.arguments or "{}")
            except json.JSONDecodeError:
                result = f"error: arguments were not valid JSON: {call.function.arguments}"
            else:
                result = run_tool(call.function.name, args)
            messages.append({"role": "tool", "tool_call_id": call.id, "content": result})
    return f"stopped: reached max steps ({max_steps})"


if __name__ == "__main__":
    answer = run(sys.argv[1])
    print(answer)
    sys.exit(2 if answer.startswith("stopped: reached max steps") else 0)

EOF
python agent.py "Which port does the payments service use?"
```

</details>

## Check your work

```bash
D=/root/harness-lab/09-errors; cd $D 2>/dev/null || echo "❌ create $D"
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
script = [{"tool": "get_service", "args": {"name": "payments"}}, {"tool": "get_service", "args": {"name": "billing"}},
          {"tool": "restart_count", "args": {"name": "search", "days": 90}}, {"tool": "get_service", "raw_args": "{name: search"},
          {"tool": "restart_count", "args": {"name": "search"}}, {"tool": "page_oncall", "args": {}}, "Billing is on 8081; there is no payments service."]
with MockModel(script) as m:
    rc, out, err = m.run(["python", "agent.py", "Which port does payments use?"], timeout=30)
ok(rc == 0 and out.endswith("Billing is on 8081; there is no payments service."), "the agent survives six bad tool steps and answers", f"the run should finish with the scripted answer - got rc {rc}, {out[-200:]!r} {err[-400:]}")
res = [x.get("content", "") for x in (m.requests[-1]["messages"] if m.requests else []) if x.get("role") == "tool"]
ok(len(res) == 6, "every tool call got exactly one tool message", f"6 tool calls should produce 6 tool messages - got {len(res)}")
if len(res) == 6:
    ok(res[0].startswith("error: KeyError") and "payments" in res[0], "an exception inside a tool becomes 'error: KeyError: ...'", f"get_service('payments') should return 'error: KeyError: ...' - got {res[0][:120]!r}")
    ok("8081" in res[1] and not res[1].startswith("error"), "a good call still returns the real result", f"get_service('billing') should include 8081 - got {res[1][:120]!r}")
    ok(res[2].startswith("error: ValueError") and "30" in res[2], "a bad argument value becomes 'error: ValueError: ...'", f"restart_count(days=90) should return 'error: ValueError: days must be 30 or less' - got {res[2][:120]!r}")
    ok(res[3].startswith("error: arguments were not valid JSON"), "malformed JSON arguments are reported, not crashed on", f"arguments '{{name: search' should give 'error: arguments were not valid JSON...' - got {res[3][:120]!r}")
    ok(res[4].startswith("error") and "days" in res[4], "a missing argument becomes an error naming it", f"restart_count without days should return an error mentioning days - got {res[4][:120]!r}")
    ok(res[5].startswith("error: unknown tool") and "page_oncall" in res[5], "an unknown tool name is reported", f"page_oncall should give 'error: unknown tool page_oncall' - got {res[5][:120]!r}")
PYEOF
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Nothing a tool does may crash the loop - catch it and send it back as the result.
- Malformed JSON arguments fail before your tool runs; handle them in the loop.
- Error results let the model recover the way a person would: look around, then try again or ask.
