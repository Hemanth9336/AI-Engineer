---
type: task
title: "A flaky tool, an agent that retries"
minutes: 10
---

## Set up

`flaky.py` has `fetch_status(service)`: it raises `TimeoutError` on its first `FLAKY_FAILS` calls in each process (default 2), then works.

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
cat > flaky.py <<'EOF'
"""A status API that times out the first few calls in each process (FLAKY_FAILS, default 2)."""
import os

_calls = {"n": 0}


def fetch_status(service):
    _calls["n"] += 1
    if _calls["n"] <= int(os.environ.get("FLAKY_FAILS", "2")):
        raise TimeoutError("status API timed out after 2s")
    return {"service": service, "status": "healthy", "p95_ms": 182}
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

1. Write `/root/harness-lab/09-errors/retry.py` with `with_retries(fn, *args, attempts=3, base_delay=0.5, **kwargs)`:
   - call `fn(*args, **kwargs)` and return its result;
   - on `TimeoutError` or `ConnectionError`, sleep `base_delay * 2 ** i` (0.5 s, then 1 s, ...) with `time.sleep` and try again;
   - after the last attempt, re-raise the error;
   - any **other** exception is raised immediately, with no retry and no sleep.
2. In `agent.py`, add a `fetch_status(service)` tool that calls `flaky.fetch_status` **through** `with_retries`. When all attempts fail, the error must still reach the model as `error: TimeoutError: ...` - the loop must not crash.

```bash
cd /root/harness-lab/09-errors
python agent.py "Is the search service healthy?"
FLAKY_FAILS=5 python agent.py "Is the search service healthy?"
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `import time` at the top and call `time.sleep(...)` - the checker replaces `retry.time.sleep` to record your delays without waiting.
- Catch only `(TimeoutError, ConnectionError)`; let everything else propagate.
- Reuse the catch-all `run_tool` from the previous task so the final TimeoutError becomes text.

</details>

<details><summary>Solution</summary>

```bash
cd /root/harness-lab/09-errors
cat > retry.py <<'EOF'
import time

RETRYABLE = (TimeoutError, ConnectionError)


def with_retries(fn, *args, attempts=3, base_delay=0.5, **kwargs):
    for i in range(attempts):
        try:
            return fn(*args, **kwargs)
        except RETRYABLE:
            if i == attempts - 1:
                raise
            time.sleep(base_delay * 2 ** i)

EOF
cat > agent.py <<'EOF'
import json
import sys
from pathlib import Path

from openai import OpenAI

from flaky import fetch_status
from retry import with_retries

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
SCHEMAS.append({"type": "function", "function": {
    "name": "fetch_status",
    "description": "Get the live health status and p95 latency of a Stackline service.",
    "parameters": {"type": "object", "properties": {"service": {"type": "string", "description": "Service name, for example search"}},
                   "required": ["service"]}}})

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


def fetch_status_retried(service):
    return with_retries(fetch_status, service)


IMPL = {"list_dir": list_dir, "read_file": read_file, "fetch_status": fetch_status_retried}


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
            result = run_tool(call.function.name, json.loads(call.function.arguments or "{}"))
            messages.append({"role": "tool", "tool_call_id": call.id, "content": result})
    return f"stopped: reached max steps ({max_steps})"


if __name__ == "__main__":
    answer = run(sys.argv[1])
    print(answer)
    sys.exit(2 if answer.startswith("stopped: reached max steps") else 0)

EOF
python agent.py "Is the search service healthy?"
FLAKY_FAILS=5 python agent.py "Is the search service healthy?" || true
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
sys.path.insert(0, ".")
try:
    import retry
    delays = []
    retry.time.sleep = lambda s: delays.append(s)
    calls = {"n": 0}
    def fails(k, exc=TimeoutError):
        def fn(x, y=0):
            calls["n"] += 1
            if calls["n"] <= k:
                raise exc("boom")
            return x + y
        return fn
    calls["n"] = 0
    r = retry.with_retries(fails(2), 40, y=2)
    ok(r == 42 and calls["n"] == 3 and delays == [0.5, 1.0], "two timeouts then success: 3 calls, waits of 0.5s and 1s, result returned", f"expected result 42 after 3 calls with delays [0.5, 1.0] - got {r}, {calls['n']} calls, {delays}")
    calls["n"], delays[:] = 0, []
    try:
        retry.with_retries(fails(9, ConnectionError), 1, attempts=4, base_delay=0.1)
        ok(False, "", "a tool that always fails should re-raise after the last attempt")
    except ConnectionError:
        ok(calls["n"] == 4 and [round(d, 3) for d in delays] == [0.1, 0.2, 0.4], "always failing: re-raised after 4 attempts with 0.1, 0.2, 0.4s waits", f"attempts=4, base_delay=0.1 should make 4 calls and wait [0.1, 0.2, 0.4] - got {calls['n']} calls, {delays}")
    calls["n"], delays[:] = 0, []
    try:
        retry.with_retries(fails(9, ValueError), 1)
        ok(False, "", "a ValueError should be raised, not swallowed")
    except ValueError:
        ok(calls["n"] == 1 and delays == [], "a non-retryable ValueError is raised at once, no sleep", f"ValueError should fail after 1 call with no sleep - got {calls['n']} calls, {delays}")
except Exception as e:
    ok(False, "", f"retry.py should define with_retries(fn, *args, attempts=3, base_delay=0.5, **kwargs) - {type(e).__name__}: {e}")
script = [{"tool": "fetch_status", "args": {"service": "search"}}, "Search is healthy."]
with MockModel(script) as m:
    rc, out, err = m.run(["python", "agent.py", "Is search healthy?"], timeout=40, env={"FLAKY_FAILS": "2"})
res = [x.get("content", "") for x in (m.requests[-1]["messages"] if m.requests else []) if x.get("role") == "tool"]
ok(rc == 0 and len(res) == 1 and "healthy" in res[0] and "error" not in res[0], "two timeouts are retried away - the model sees the real status", f"with FLAKY_FAILS=2 the tool result should be the healthy status - got {res} {err[-300:]}")
with MockModel(script) as m:
    rc, out, err = m.run(["python", "agent.py", "Is search healthy?"], timeout=40, env={"FLAKY_FAILS": "5"})
res = [x.get("content", "") for x in (m.requests[-1]["messages"] if m.requests else []) if x.get("role") == "tool"]
ok(rc == 0 and len(res) == 1 and res[0].startswith("error: TimeoutError"), "after the last retry the timeout reaches the model as text", f"with FLAKY_FAILS=5 the tool result should be 'error: TimeoutError: ...' and the run should finish - got rc {rc}, {res} {err[-300:]}")
PYEOF
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Retry transient errors (timeouts, connection drops, 429/5xx); send permanent ones straight back.
- Exponential backoff waits longer after each failure; cap the attempts.
- When retries run out, the error still goes to the model as text.
