---
type: task
title: "Define a weather lookup tool"
minutes: 7
---

## Set up

```bash
mkdir -p /root/fde-lab/11-tools
```

## What to build

1. In `/root/fde-lab/11-tools/tools.py`, define `WEATHER_TOOL` for a function `get_weather` with a required string `city` and an optional `unit` that is one of `celsius` or `fahrenheit`. Write a description that says when to use it.
2. Write `ask_tool.py`, used as `python ask_tool.py QUESTION`, that sends QUESTION to `lab-fast` with `tools=[WEATHER_TOOL]` and prints **one JSON line**:
   - `{"name": ..., "arguments": {...}}` if the model returned a tool call (arguments parsed from the JSON string), or
   - `{"name": null, "answer": "<text>"}` if it answered directly.

Don't run the tool yet - just see what the model asks for.

```bash
cd /root/fde-lab/11-tools
python ask_tool.py "What's the weather in Rotterdam right now?"
python ask_tool.py "What is 12 times 12?"
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `from tools import WEATHER_TOOL`.
- `json.loads(call.function.arguments)` turns the argument string into a dict.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/11-tools
cat > tools.py <<'EOF'
WEATHER_TOOL = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get the current weather for a city. Use it whenever the user asks about weather, rain or temperature somewhere.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name, for example Rotterdam"},
                "unit": {"type": "string", "enum": ["celsius", "fahrenheit"], "description": "Temperature unit, default celsius"},
            },
            "required": ["city"],
        },
    },
}
EOF
cat > ask_tool.py <<'EOF'
import json
import sys

from openai import OpenAI

from tools import WEATHER_TOOL

resp = OpenAI().chat.completions.create(model="lab-fast", tools=[WEATHER_TOOL], messages=[{"role": "user", "content": sys.argv[1]}])
msg = resp.choices[0].message
if msg.tool_calls:
    call = msg.tool_calls[0]
    print(json.dumps({"name": call.function.name, "arguments": json.loads(call.function.arguments)}))
else:
    print(json.dumps({"name": None, "answer": msg.content}))
EOF
python ask_tool.py "What's the weather in Rotterdam right now?"
python ask_tool.py "What is 12 times 12?"
```

</details>

## Check your work

```bash
D=/root/fde-lab/11-tools; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/ask_tool.py 2>/dev/null && [ -s $D/ask_tool.py ] && echo "✅ ask_tool.py reads the key from the environment" || echo "❌ ask_tool.py must not contain a key - let the SDK read it from the environment"
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
    from tools import WEATHER_TOOL as W
    f = W["function"]
    p = f["parameters"]
    good = (W.get("type") == "function" and f.get("name") == "get_weather" and len(f.get("description", "")) >= 20 and p.get("type") == "object"
            and p["properties"]["city"]["type"] == "string" and sorted(p["properties"]["unit"]["enum"]) == ["celsius", "fahrenheit"] and p.get("required") == ["city"])
except Exception as e:
    good = False
ok(good, "WEATHER_TOOL defines get_weather with a required city, a unit enum and a real description", "WEATHER_TOOL should be a function tool named get_weather, with a description, required [city] and unit enum [celsius, fahrenheit]")
def ask(q):
    rc, out, err = run("ask_tool.py", q)
    try:
        return json.loads(out)
    except ValueError:
        return {"error": out[:150] + err[-150:]}
r = ask("Do I need an umbrella in Leeds today?")
ok(r.get("name") == "get_weather" and str(r.get("arguments", {}).get("city", "")).lower() == "leeds", "a weather question returns a get_weather call for Leeds", f"expected {{'name': 'get_weather', 'arguments': {{'city': 'Leeds'}}}} - got {r}")
r = ask("Translate 'good morning' into Dutch.")
ok(r.get("name") is None and r.get("answer"), "an unrelated question is answered directly", f"an unrelated question should print name null and the answer - got {r}")
rows = [json.loads(l) for l in open("/var/log/ailab/requests.jsonl")]
ok(any(x.get("model") == "lab-fast" and "get_weather" in (x.get("tools") or []) and "get_weather" in (x.get("tool_calls") or []) for x in rows), "the gateway logged a lab-fast call that offered get_weather and got a tool call back", "no lab-fast call offering get_weather that returned a tool call")
PYEOF
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- A tool is a name, a description that says when to use it, and a JSON Schema for its arguments.
- The model returns a tool call - name plus a JSON string of arguments - instead of text.
- The model decides whether to call; unrelated questions get a normal answer.
