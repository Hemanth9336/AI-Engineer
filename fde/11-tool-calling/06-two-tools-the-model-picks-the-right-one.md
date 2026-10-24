---
type: task
title: "Two tools, the model picks the right one"
minutes: 8
---

## Set up

`parcels.json` is your stand-in for Meridian's order system.

```bash
mkdir -p /root/fde-lab/11-tools
cd /root/fde-lab/11-tools
cat > weather.json <<'EOF'
{
  "rotterdam": {
    "temp_c": 11,
    "conditions": "light rain"
  },
  "leeds": {
    "temp_c": 8,
    "conditions": "overcast"
  },
  "hamburg": {
    "temp_c": 4,
    "conditions": "clear"
  }
}
EOF
cat > parcels.json <<'EOF'
{
  "MER-55120": {
    "status": "out for delivery",
    "eta": "2026-03-15"
  },
  "MER-70413": {
    "status": "held at depot HH-02",
    "eta": null
  },
  "MER-60311": {
    "status": "in transit to Leeds hub",
    "eta": "2026-03-17"
  }
}
EOF
```

## What to build

Give the model a choice.

1. Add `TRACK_TOOL` to `tools.py`: a function `track_parcel` with a required string `order_id`, described so the model uses it for any question about where an order is.
2. Write `assistant.py`, used as `python assistant.py QUESTION`: the same tool loop as `loop.py`, but offering **both** tools, with `track_parcel(order_id)` returning `{"order_id", "status", "eta"}` from `parcels.json` or `{"error": "unknown order"}`.
3. Print the final answer.

```bash
cd /root/fde-lab/11-tools
python assistant.py "Where is my parcel MER-55120?"
python assistant.py "Is it raining in Rotterdam?"
```

The definition to start from:

```python
TRACK_TOOL = {
    "type": "function",
    "function": {
        "name": "track_parcel",
        "description": "Look up the delivery status of a Meridian order by its order id (like MER-12345). Use it for any question about where an order is.",
        "parameters": {
            "type": "object",
            "properties": {"order_id": {"type": "string", "description": "Order id, for example MER-55120"}},
            "required": ["order_id"],
        },
    },
}
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Import `get_weather` from `loop.py`? No - `loop.py` runs on import. Copy the function, or move it into `tools.py`.
- `TOOLS = {"get_weather": get_weather, "track_parcel": track_parcel}`.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/11-tools
cat >> tools.py <<'EOF'


TRACK_TOOL = {
    "type": "function",
    "function": {
        "name": "track_parcel",
        "description": "Look up the delivery status of a Meridian order by its order id (like MER-12345). Use it for any question about where an order is.",
        "parameters": {
            "type": "object",
            "properties": {"order_id": {"type": "string", "description": "Order id, for example MER-55120"}},
            "required": ["order_id"],
        },
    },
}
EOF
cat > assistant.py <<'EOF'
import json
import sys
from pathlib import Path

from openai import OpenAI

from tools import TRACK_TOOL, WEATHER_TOOL

HERE = Path(__file__).parent
WEATHER = json.loads((HERE / "weather.json").read_text())
PARCELS = json.loads((HERE / "parcels.json").read_text())


def get_weather(city, unit="celsius"):
    w = WEATHER.get(city.strip().lower())
    if not w:
        return {"error": "unknown city"}
    temp = w["temp_c"] if unit == "celsius" else round(w["temp_c"] * 9 / 5 + 32, 1)
    return {"city": city, "temp": temp, "unit": unit, "conditions": w["conditions"]}


def track_parcel(order_id):
    p = PARCELS.get(order_id.strip().upper())
    if not p:
        return {"error": "unknown order"}
    return {"order_id": order_id, "status": p["status"], "eta": p["eta"]}


TOOLS = {"get_weather": get_weather, "track_parcel": track_parcel}

client = OpenAI()
messages = [{"role": "user", "content": sys.argv[1]}]
while True:
    msg = client.chat.completions.create(model="lab-fast", tools=[WEATHER_TOOL, TRACK_TOOL], messages=messages).choices[0].message
    if not msg.tool_calls:
        print(msg.content)
        break
    messages.append(msg)
    for call in msg.tool_calls:
        name, args = call.function.name, json.loads(call.function.arguments)
        result = TOOLS[name](**args) if name in TOOLS else {"error": f"unknown tool {name}"}
        messages.append({"role": "tool", "tool_call_id": call.id, "content": json.dumps(result)})
EOF
python assistant.py "Where is my parcel MER-55120?"
python assistant.py "Is it raining in Rotterdam?"
```

</details>

## Check your work

```bash
D=/root/fde-lab/11-tools; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/assistant.py 2>/dev/null && [ -s $D/assistant.py ] && echo "✅ assistant.py reads the key from the environment" || echo "❌ assistant.py must not contain a key - let the SDK read it from the environment"
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
    from tools import TRACK_TOOL as T
    good = T["function"]["name"] == "track_parcel" and T["function"]["parameters"]["required"] == ["order_id"] and len(T["function"].get("description", "")) >= 20
except Exception:
    good = False
ok(good, "TRACK_TOOL defines track_parcel with a required order_id", "add TRACK_TOOL (track_parcel, required order_id, a real description) to tools.py")
for q, tool, want in (("Has order MER-70413 moved yet?", "track_parcel", "hh-02"), ("Is it cold in Hamburg right now?", "get_weather", "4")):
    before = sum(1 for _ in open("/var/log/ailab/requests.jsonl"))
    rc, out, err = run("assistant.py", q)
    rows = [json.loads(l) for l in open("/var/log/ailab/requests.jsonl")][before:]
    called = [n for r in rows for n in (r.get("tool_calls") or [])]
    offered = rows[0].get("tools") if rows else []
    ok(sorted(offered or []) == ["get_weather", "track_parcel"] and called == [tool] and want in out.lower(), f"'{q}' -> the model called {tool} and the answer uses its result", f"'{q}' should offer both tools, call only {tool} and answer from its result - offered {offered}, called {called}, answer {out[:150]!r} {err[-150:]}")
PYEOF
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- With several tools, the descriptions decide which one the model picks.
- The same loop handles any number of tools via a dispatch table.
- Check which tool was called - wrong-tool calls are a real failure mode to test for.
