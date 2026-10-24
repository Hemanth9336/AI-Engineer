---
type: task
title: "Turn the tool loop into a multi-turn agent"
minutes: 10
---

## Set up

```bash
mkdir -p /root/fde-lab/20-agents
cd /root/fde-lab/20-agents
cat > parcels.json <<'EOF'
{
  "MER-60311": {
    "status": "in transit to Leeds hub",
    "eta": "2026-03-17"
  },
  "MER-55120": {
    "status": "out for delivery",
    "eta": "2026-03-15"
  }
}
EOF
rm -f tickets.jsonl
```

## What to build

Write `/root/fde-lab/20-agents/agent.py`, a multi-turn support agent on `lab-fast`:

- Two tools:
  - `track_parcel(order_id)` - status from `parcels.json`, or `{"error": "unknown order"}`.
  - `create_ticket(order_id, summary, priority)` - `priority` is an enum of `low`, `normal` and `urgent`. It appends `{"ticket_id": "T-XXXXXX", "order_id", "summary", "priority"}` as one JSON line to `tickets.jsonl` and returns it.
- A system message saying it's Meridian's support agent and should use the tools.
- Read user turns from standard input until EOF. For each turn, run the tool loop until the model answers, then print `assistant: <answer>`. Keep **all** messages - including tool calls and results - in the history across turns.
- Print each tool call to **stderr** as `[tool] name(args)` so you can watch the agent work.

```bash
cd /root/fde-lab/20-agents
printf "Where is my order MER-60311?\nIt was promised for yesterday. Please open an urgent ticket for it.\n" | python agent.py
cat tickets.jsonl
```

The second turn says "it" - the agent must work out the order from the history.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Two nested loops: the outer one reads user turns, the inner one is the tool loop.
- Append the final assistant answer to the history too, as a plain `{"role": "assistant", "content": ...}`.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/20-agents
cat > agent.py <<'EOF'
import json
import sys
import uuid
from pathlib import Path

from openai import OpenAI

HERE = Path(__file__).parent
PARCELS = json.loads((HERE / "parcels.json").read_text())
TOOLS = [
    {"type": "function", "function": {
        "name": "track_parcel",
        "description": "Look up the delivery status of a Meridian order by its order id (like MER-12345).",
        "parameters": {"type": "object", "properties": {"order_id": {"type": "string"}}, "required": ["order_id"]}}},
    {"type": "function", "function": {
        "name": "create_ticket",
        "description": "Open a support ticket for an order when the customer asks for follow-up. Returns the ticket id.",
        "parameters": {"type": "object", "properties": {
            "order_id": {"type": "string"},
            "summary": {"type": "string", "description": "One sentence describing the problem"},
            "priority": {"type": "string", "enum": ["low", "normal", "urgent"]}},
            "required": ["order_id", "summary", "priority"]}}},
]


def track_parcel(order_id):
    p = PARCELS.get(order_id.strip().upper())
    return {"order_id": order_id, **p} if p else {"error": "unknown order"}


def create_ticket(order_id, summary, priority):
    ticket = {"ticket_id": "T-" + uuid.uuid4().hex[:6].upper(), "order_id": order_id, "summary": summary, "priority": priority}
    with open(HERE / "tickets.jsonl", "a") as f:
        f.write(json.dumps(ticket) + "\n")
    return ticket


FUNCS = {"track_parcel": track_parcel, "create_ticket": create_ticket}
client = OpenAI()
messages = [{"role": "system", "content": "You are Meridian Logistics' support agent. Use the tools to look up orders and open tickets. Answer in at most two sentences."}]

while True:
    try:
        text = input().strip()
    except EOFError:
        break
    if not text:
        continue
    messages.append({"role": "user", "content": text})
    while True:
        msg = client.chat.completions.create(model="lab-fast", tools=TOOLS, messages=messages).choices[0].message
        if not msg.tool_calls:
            messages.append({"role": "assistant", "content": msg.content})
            print(f"assistant: {msg.content}")
            break
        messages.append(msg)
        for call in msg.tool_calls:
            name, args = call.function.name, json.loads(call.function.arguments)
            result = FUNCS[name](**args) if name in FUNCS else {"error": f"unknown tool {name}"}
            print(f"  [tool] {name}({args})", file=sys.stderr)
            messages.append({"role": "tool", "tool_call_id": call.id, "content": json.dumps(result)})

EOF
printf "Where is my order MER-60311?\nIt was promised for yesterday. Please open an urgent ticket for it.\n" | python agent.py
cat tickets.jsonl
```

</details>

## Check your work

```bash
D=/root/fde-lab/20-agents; cd $D 2>/dev/null || echo "❌ create $D"
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
Path("tickets.jsonl").unlink(missing_ok=True)
before = sum(1 for _ in open("/var/log/ailab/requests.jsonl"))
r = subprocess.run([sys.executable, "agent.py"], input="Hi, can you check order MER-55120 for me?\nThe customer is furious - open an urgent ticket for that order please.\n", capture_output=True, text=True)
rows = [json.loads(l) for l in open("/var/log/ailab/requests.jsonl")][before:]
lines = [l for l in r.stdout.splitlines() if l.startswith("assistant: ")]
ok(r.returncode == 0 and len(lines) == 2, "two user turns produce two assistant answers", f"expected two 'assistant: ' lines - got {r.stdout[-300:]!r} {r.stderr[-300:]}")
tickets = [json.loads(l) for l in open("tickets.jsonl")] if Path("tickets.jsonl").exists() else []
ok(len(tickets) == 1 and tickets[0].get("order_id") == "MER-55120" and tickets[0].get("priority") == "urgent" and str(tickets[0].get("ticket_id", "")).startswith("T-"), "an urgent ticket for MER-55120 was written to tickets.jsonl", f"expected one urgent ticket for MER-55120 in tickets.jsonl - got {tickets}")
calls = [n for x in rows for n in (x.get("tool_calls") or [])]
ok(calls == ["track_parcel", "create_ticket"], "the agent called track_parcel, then create_ticket", f"expected tool calls track_parcel then create_ticket - got {calls}")
second = [x for x in rows if "create_ticket" in (x.get("tool_calls") or [])]
ok(second and second[0].get("roles", []).count("tool") >= 1 and second[0]["roles"][0] == "system", "turn two still carried turn one's tool call and result in its history", "the second turn's request should include the first turn's tool messages")
ok("[tool]" in r.stderr and "[tool]" not in r.stdout, "tool calls are traced on stderr", "print each tool call to stderr as [tool] name(args)")
PYEOF
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- An agent is a model in a loop choosing tools until it's done.
- Keep tool calls and results in the history so later turns can refer back.
- Action tools need narrow parameters, limits in code and an audit trail.
