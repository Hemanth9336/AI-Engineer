---
type: task
title: "An agent that must chain two tool calls"
minutes: 7
---

## Set up

`parcels.json` gives each order's status and depot; `depots.json` gives each depot's hours today.

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

Write `/root/fde-lab/21-multistep/agent.py`:

- Tools `track_parcel(order_id)` (returns status **and** `depot`) and `depot_hours(depot_id)`, from the JSON files.
- `run_agent(question, ask)`: the tool loop, with the model call injected. `ask(messages)` returns `{"content": str|None, "tool_calls": [{"id", "name", "arguments": dict}]}`. Append the assistant tool-call message in API format, then one `tool` message per call. Return the final text.
- `openai_ask(messages)`: calls `lab-fast` with the tools and converts the response to that dict.
- Trace each call to stderr as `[tool] name(args)`.
- `python agent.py QUESTION` prints the answer.

```bash
cd /root/fde-lab/21-multistep
python agent.py "Can I collect order MER-81234 today, and until what time?"
```

You should see two tool calls in the trace, the second using the depot id from the first.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Assistant tool-call message: `{"role": "assistant", "content": ..., "tool_calls": [{"id": ..., "type": "function", "function": {"name": ..., "arguments": json.dumps(args)}}]}`.
- Import the SDK inside `openai_ask`, so tests can import `run_agent` without a key.

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


def run_tool(fn, args):
    return fn(**args)


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
    seen = []
    script = iter([
        {"content": None, "tool_calls": [{"id": "c1", "name": "track_parcel", "arguments": {"order_id": "MER-81234"}}]},
        {"content": None, "tool_calls": [{"id": "c2", "name": "depot_hours", "arguments": {"depot_id": "RTM-01"}}]},
        {"content": "Yes, until 18:00.", "tool_calls": []},
    ])
    def ask(messages):
        seen.append(json.loads(json.dumps(messages, default=str)))
        return next(script)
    out = agent.run_agent("Can I collect MER-81234?", ask)
    tool_msgs = [m for m in seen[-1] if m.get("role") == "tool"]
    ok(out == "Yes, until 18:00." and len(seen) == 3, "run_agent runs a scripted two-step plan and returns the final text", f"expected 3 ask() calls and the final text - got {len(seen)} calls, {out!r}")
    ok(len(tool_msgs) == 2 and tool_msgs[0]["tool_call_id"] == "c1" and "RTM-01" in tool_msgs[0]["content"] and "18:00" in tool_msgs[1]["content"]
       and seen[1][-2]["role"] == "assistant" and seen[1][-2]["tool_calls"][0]["function"]["name"] == "track_parcel", "each tool result follows its assistant tool-call message, with real data", "append the assistant tool-call message, then a tool message (matching id) with the tool's JSON result")
before = sum(1 for _ in open("/var/log/ailab/requests.jsonl"))
rc, out, err = run("agent.py", "Is MER-81234 ready to pick up today? Until when is the depot open?")
rows = [json.loads(l) for l in open("/var/log/ailab/requests.jsonl")][before:]
calls = [n for x in rows for n in (x.get("tool_calls") or [])]
ok(rc == 0 and calls == ["track_parcel", "depot_hours"] and "18:00" in out, "the real agent chained track_parcel then depot_hours and answered with the closing time", f"expected tool calls track_parcel then depot_hours and 18:00 in the answer - got {calls}, {out[:200]!r} {err[-200:]}")
ok(err.count("[tool]") == 2, "both tool calls were traced on stderr", f"expected two [tool] lines on stderr - got {err[-300:]!r}")
PYEOF
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Multi-step questions need tool calls in sequence, each using the last result.
- Descriptions and return values that expose the ids the next step needs help the model plan.
- Inject the model call so the loop can be tested with scripted replies.
