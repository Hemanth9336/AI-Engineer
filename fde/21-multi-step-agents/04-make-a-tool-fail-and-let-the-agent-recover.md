---
type: task
title: "Make a tool fail and let the agent recover"
minutes: 7
---

## Set up

```bash
mkdir -p /root/fde-lab/21-multistep
cd /root/fde-lab/21-multistep
cat > parcels.json <<'EOF'
{
  "MER-81234": {
    "status": "held at depot RTM-01",
    "depot": "RTM-01"
  },
  "MER-81240": {
    "status": "out for delivery",
    "depot": null
  }
}
EOF
cat > depots.json <<'EOF'
{
  "RTM-01": {
    "name": "Rotterdam Waalhaven",
    "today": "opens 07:00, closes 18:00"
  },
  "LDS-02": {
    "name": "Leeds Stourton",
    "today": "opens 06:00, closes 20:00"
  }
}
EOF
```

## What to build

Make the agent from the previous task survive a depot API outage. Update `/root/fde-lab/21-multistep/agent.py`:

1. `depot_hours` raises `ConnectionError("depot API timed out")` when the environment variable `DEPOT_API_DOWN` is set (this simulates the outage).
2. Add `run_tool(fn, args, retries=1)`: call `fn(**args)`; on any exception, log `[tool error] attempt N: <error>` to stderr and retry, up to `retries` extra times; then return `{"error": "<function name> unavailable: <last error>"}`.
3. Use `run_tool` for every tool call in `run_agent`.

```bash
cd /root/fde-lab/21-multistep
DEPOT_API_DOWN=1 python agent.py "Can I collect order MER-81234 today, and until what time?"
```

The agent should still answer - saying what it found, and what it couldn't check.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `fn.__name__` gives the function's name for the error message.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/21-multistep
cat > agent.py <<'EOF'
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).parent
PARCELS = json.loads((HERE / "parcels.json").read_text())
DEPOTS = json.loads((HERE / "depots.json").read_text())
SYSTEM = "You are Meridian Logistics' operations assistant. Use the tools; look up an order's depot before answering questions about collecting it."
TOOLS = [
    {"type": "function", "function": {
        "name": "track_parcel",
        "description": "Status of a Meridian order by order id, including the depot holding it.",
        "parameters": {"type": "object", "properties": {"order_id": {"type": "string"}}, "required": ["order_id"]}}},
    {"type": "function", "function": {
        "name": "depot_hours",
        "description": "Today's opening hours for a depot, by depot id like RTM-01.",
        "parameters": {"type": "object", "properties": {"depot_id": {"type": "string"}}, "required": ["depot_id"]}}},
]


def track_parcel(order_id):
    p = PARCELS.get(order_id.strip().upper())
    return {"order_id": order_id, **p} if p else {"error": "unknown order"}


def depot_hours(depot_id):
    if os.environ.get("DEPOT_API_DOWN"):
        raise ConnectionError("depot API timed out")
    d = DEPOTS.get(depot_id.strip().upper())
    return {"depot_id": depot_id, **d} if d else {"error": "unknown depot"}


FUNCS = {"track_parcel": track_parcel, "depot_hours": depot_hours}


def run_tool(fn, args, retries=1):
    for attempt in range(retries + 1):
        try:
            return fn(**args)
        except Exception as e:
            print(f"  [tool error] attempt {attempt + 1}: {e}", file=sys.stderr)
            last = e
    return {"error": f"{fn.__name__} unavailable: {last}"}


def run_agent(question, ask):
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": question}]
    while True:
        reply = ask(messages)
        if not reply["tool_calls"]:
            return reply["content"]
        messages.append({"role": "assistant", "content": reply["content"], "tool_calls": [
            {"id": c["id"], "type": "function", "function": {"name": c["name"], "arguments": json.dumps(c["arguments"])}} for c in reply["tool_calls"]]})
        for c in reply["tool_calls"]:
            print(f"  [tool] {c['name']}({c['arguments']})", file=sys.stderr)
            fn = FUNCS.get(c["name"])
            result = run_tool(fn, c["arguments"]) if fn else {"error": f"unknown tool {c['name']}"}
            messages.append({"role": "tool", "tool_call_id": c["id"], "content": json.dumps(result)})


def openai_ask(messages):
    from openai import OpenAI

    msg = OpenAI().chat.completions.create(model="lab-fast", tools=TOOLS, messages=messages).choices[0].message
    calls = [{"id": c.id, "name": c.function.name, "arguments": json.loads(c.function.arguments)} for c in msg.tool_calls or []]
    return {"content": msg.content, "tool_calls": calls}


if __name__ == "__main__":
    print(run_agent(sys.argv[1], openai_ask))

EOF
DEPOT_API_DOWN=1 python agent.py "Can I collect order MER-81234 today, and until what time?"
```

</details>

## Check your work

```bash
D=/root/fde-lab/21-multistep; cd $D 2>/dev/null || echo "❌ create $D"
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
sys.path.insert(0, ".")
try:
    import agent
except Exception as e:
    agent = None
    print(f"❌ import agent failed: {e}")
if agent:
    n = []
    def flaky(x):
        n.append(1)
        if len(n) == 1:
            raise TimeoutError("slow")
        return {"x": x}
    ok(agent.run_tool(flaky, {"x": 1}) == {"x": 1} and len(n) == 2, "a tool that fails once succeeds on the retry", f"run_tool should retry once and return the result - got {len(n)} calls")
    m = []
    def broken():
        m.append(1)
        raise ConnectionError("down")
    r = agent.run_tool(broken, {}, retries=2)
    ok(len(m) == 3 and r == {"error": "broken unavailable: down"}, "a tool that keeps failing is tried retries+1 times, then returns an error result", f"with retries=2 expected 3 attempts and {{'error': 'broken unavailable: down'}} - got {len(m)} attempts, {r}")
env = dict(os.environ, DEPOT_API_DOWN="1")
before = sum(1 for _ in open("/var/log/ailab/requests.jsonl"))
r = subprocess.run([sys.executable, "agent.py", "Is MER-81234 ready to pick up today? Until when is the depot open?"], capture_output=True, text=True, env=env)
rows = [json.loads(l) for l in open("/var/log/ailab/requests.jsonl")][before:]
ok(r.returncode == 0 and r.stdout.strip() and r.stderr.count("[tool error]") == 2, "during the outage the agent retried once and still answered", f"with DEPOT_API_DOWN=1 expected two [tool error] lines and an answer - got exit {r.returncode}, {r.stdout[-200:]!r} {r.stderr[-300:]!r}")
last = rows[-1] if rows else {}
ok("tool" in (last.get("roles") or []) and ("rotterdam" in r.stdout.lower() or "rtm-01" in r.stdout.lower()), "the model got the error as a tool result and still reported the depot it found", f"the answer should still mention the depot it found (RTM-01) - got {r.stdout[-200:]!r}")
PYEOF
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Retry transient tool failures a small, fixed number of times.
- Return exhausted failures as error results so the model can respond honestly.
- Simulate failures in tests - don't wait for the first real outage.
