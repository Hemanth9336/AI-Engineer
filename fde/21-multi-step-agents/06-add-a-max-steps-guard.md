---
type: task
title: "Add a max-steps guard"
minutes: 8
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

Add a guard to `/root/fde-lab/21-multistep/agent.py`:

- `run_agent(question, ask, max_steps=6)` makes at most `max_steps` calls to `ask`.
- If it hasn't got a final answer by then, it returns exactly `Stopped after N steps without an answer.` (with N = `max_steps`).
- Keep the retry handling from the previous task.

```bash
cd /root/fde-lab/21-multistep
python agent.py "Can I collect order MER-81234 today, and until what time?"
```

The checker drives `run_agent` with a fake model that never stops calling tools.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Replace `while True:` with `for step in range(max_steps):` and return the stop message after the loop.

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
STOPPED = "Stopped after {n} steps without an answer."
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


def run_agent(question, ask, max_steps=6):
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": question}]
    for step in range(max_steps):
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

    return STOPPED.format(n=max_steps)


def openai_ask(messages):
    from openai import OpenAI

    msg = OpenAI().chat.completions.create(model="lab-fast", tools=TOOLS, messages=messages).choices[0].message
    calls = [{"id": c.id, "name": c.function.name, "arguments": json.loads(c.function.arguments)} for c in msg.tool_calls or []]
    return {"content": msg.content, "tool_calls": calls}


if __name__ == "__main__":
    print(run_agent(sys.argv[1], openai_ask))

EOF
python agent.py "Can I collect order MER-81234 today, and until what time?"
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
    calls = []
    def stubborn(messages):
        calls.append(1)
        return {"content": None, "tool_calls": [{"id": f"c{len(calls)}", "name": "track_parcel", "arguments": {"order_id": "MER-81234"}}]}
    out = agent.run_agent("loop forever", stubborn, max_steps=4)
    ok(out == "Stopped after 4 steps without an answer." and len(calls) == 4, "a model that never stops is cut off after max_steps calls", f"with max_steps=4 expected 4 ask() calls and the stop message - got {len(calls)} calls, {out!r}")
    calls.clear()
    out = agent.run_agent("loop forever", stubborn)
    ok(out == "Stopped after 6 steps without an answer." and len(calls) == 6, "the default limit is 6 steps", f"the default max_steps should be 6 - got {len(calls)} calls, {out!r}")
    quick = iter([{"content": "Done.", "tool_calls": []}])
    ok(agent.run_agent("hi", lambda m: next(quick), max_steps=1) == "Done.", "an answer on the last allowed step is still returned", "an answer on the final allowed step should be returned, not the stop message")
rc, out, err = run("agent.py", "Is MER-81234 ready to pick up today? Until when is the depot open?")
ok(rc == 0 and "18:00" in out, "normal questions still get answered", f"the agent should still answer normal questions - got {out[:200]!r} {err[-200:]}")
PYEOF
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Every agent loop needs a hard step limit.
- When the guard fires, return a fixed message and log the trace.
- Set the limit from real traces, with headroom above normal runs.
