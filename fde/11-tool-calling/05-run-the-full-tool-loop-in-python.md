---
type: task
title: "Run the full tool loop in Python"
minutes: 7
---

## Set up

`weather.json` is your stand-in weather service: current conditions for a few cities.

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

Write `/root/fde-lab/11-tools/loop.py`, used as `python loop.py QUESTION`:

1. Implement `get_weather(city, unit="celsius")` using `weather.json` (look the city up lowercased). Return `{"city", "temp", "unit", "conditions"}` - converting to Fahrenheit when asked - or `{"error": "unknown city"}`.
2. Run the tool loop from the lesson with `tools=[WEATHER_TOOL]` on `lab-fast`, dispatching by name from a dict.
3. Print the final answer.

```bash
cd /root/fde-lab/11-tools
python loop.py "Is it raining in Rotterdam?"
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Fahrenheit: `c * 9 / 5 + 32`.
- `TOOLS = {"get_weather": get_weather}` then `TOOLS[name](**args)` - check the name is in the dict first.
- Append `msg` itself (the SDK object) before the tool results.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/11-tools
cat > loop.py <<'EOF'
import json
import sys
from pathlib import Path

from openai import OpenAI

from tools import WEATHER_TOOL

DATA = json.loads(Path(__file__).with_name("weather.json").read_text())


def get_weather(city, unit="celsius"):
    w = DATA.get(city.strip().lower())
    if not w:
        return {"error": "unknown city"}
    temp = w["temp_c"] if unit == "celsius" else round(w["temp_c"] * 9 / 5 + 32, 1)
    return {"city": city, "temp": temp, "unit": unit, "conditions": w["conditions"]}


TOOLS = {"get_weather": get_weather}


def run_tool(name, args):
    if name not in TOOLS:
        return {"error": f"unknown tool {name}"}
    return TOOLS[name](**args)


client = OpenAI()
messages = [{"role": "user", "content": sys.argv[1]}]
while True:
    msg = client.chat.completions.create(model="lab-fast", tools=[WEATHER_TOOL], messages=messages).choices[0].message
    if not msg.tool_calls:
        print(msg.content)
        break
    messages.append(msg)
    for call in msg.tool_calls:
        result = run_tool(call.function.name, json.loads(call.function.arguments))
        messages.append({"role": "tool", "tool_call_id": call.id, "content": json.dumps(result)})
EOF
python loop.py "Is it raining in Rotterdam?"
```

</details>

## Check your work

```bash
D=/root/fde-lab/11-tools; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/loop.py 2>/dev/null && [ -s $D/loop.py ] && echo "✅ loop.py reads the key from the environment" || echo "❌ loop.py must not contain a key - let the SDK read it from the environment"
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
src = Path("loop.py").read_text() if Path("loop.py").exists() else ""
ns = {"__file__": str(Path("loop.py").resolve()), "__name__": "loop"}
try:
    exec(compile(src.split("client = OpenAI()")[0], "loop.py", "exec"), ns)
    gw = ns["get_weather"]
    good = (gw("Leeds") == {"city": "Leeds", "temp": 8, "unit": "celsius", "conditions": "overcast"}
            and gw("hamburg", "fahrenheit")["temp"] == 39.2 and gw("Atlantis") == {"error": "unknown city"})
except Exception as e:
    good = False
ok(good, "get_weather reads weather.json, converts units and reports unknown cities", "get_weather('Leeds') should return city/temp/unit/conditions from weather.json, convert to fahrenheit, and return {'error': 'unknown city'} otherwise")
before = sum(1 for _ in open("/var/log/ailab/requests.jsonl"))
rc, out, err = run("loop.py", "Should our Leeds driver expect rain today?")
rows = [json.loads(l) for l in open("/var/log/ailab/requests.jsonl")][before:]
ok(rc == 0 and "overcast" in out.lower(), "the final answer uses the tool result for Leeds", f"the answer should come from the tool result (overcast in Leeds) - got {out[:200]!r} {err[-200:]}")
ok(len(rows) >= 2 and "get_weather" in (rows[0].get("tool_calls") or []) and "tool" in (rows[-1].get("roles") or []) and rows[-1].get("roles", [])[-2:-1] == ["assistant"], "the loop sent the tool result back after the assistant's tool call", "after the tool call, send the assistant message and then a tool message with the result")
PYEOF
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- The tool loop: call, run the requested tool, append the result, call again until there's a text answer.
- Each result is a `tool` message with the matching `tool_call_id`, after the assistant's tool-call message.
- Dispatch tools from a fixed table and return errors as results.
