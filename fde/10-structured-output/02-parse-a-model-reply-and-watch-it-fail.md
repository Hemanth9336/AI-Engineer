---
type: task
title: "Parse a model reply and watch it fail"
minutes: 7
---

## Set up

```bash
mkdir -p /root/fde-lab/10-structured
```

## What to build

Write `/root/fde-lab/10-structured/parse.py` that:

1. Asks `lab-mini` (no JSON mode, no system message): `Extract the order id and city from this message and reply with JSON: Hi, order MER-55120 was supposed to arrive at our Leeds store yesterday.`
2. Tries `json.loads()` on the raw reply.
3. Writes `result.json`: `{"raw": <reply>, "parsed": <true|false>, "error": <the exception message, or null>, "data": <the parsed object, or null>}`.

```bash
cd /root/fde-lab/10-structured
python parse.py
cat result.json
```

Your script must not crash when parsing fails - catching the failure is the point. Did your model wrap the JSON in text or fences?

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `except json.JSONDecodeError as e: error = str(e)`.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/10-structured
cat > parse.py <<'EOF'
import json

from openai import OpenAI

PROMPT = "Extract the order id and city from this message and reply with JSON: Hi, order MER-55120 was supposed to arrive at our Leeds store yesterday."
raw = OpenAI().chat.completions.create(model="lab-mini", messages=[{"role": "user", "content": PROMPT}]).choices[0].message.content
try:
    result = {"raw": raw, "parsed": True, "error": None, "data": json.loads(raw)}
except json.JSONDecodeError as e:
    result = {"raw": raw, "parsed": False, "error": str(e), "data": None}
json.dump(result, open("result.json", "w"), indent=2)
print(result["parsed"], result["error"])
EOF
python parse.py
cat result.json
```

</details>

## Check your work

```bash
D=/root/fde-lab/10-structured; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/parse.py 2>/dev/null && [ -s $D/parse.py ] && echo "✅ parse.py reads the key from the environment" || echo "❌ parse.py must not contain a key - let the SDK read it from the environment"
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
r = load("result.json") or {}
ok(isinstance(r.get("raw"), str) and r["raw"], "result.json holds the raw reply", "result.json should hold the raw reply in 'raw'")
try:
    real, err = json.loads(r.get("raw") or ""), None
except ValueError as e:
    real, err = None, e
if err:
    ok(r.get("parsed") is False and r.get("error") and r.get("data") is None, "the parse failure was caught and recorded", "the raw reply isn't valid JSON - parsed should be false, with the error message and data null")
else:
    ok(r.get("parsed") is True and r.get("error") is None and r.get("data") == real, "the reply parsed and data holds the object", "the raw reply is valid JSON - parsed should be true, error null and data the parsed object")
PYEOF
jq -se 'any(.[]; .ok and .api == "chat.completions" and .model == "lab-mini" and (.client | startswith("OpenAI/Python")) and (.json_mode | not) and (.system | not))' /var/log/ailab/requests.jsonl >/dev/null 2>&1 && echo "✅ the gateway logged a plain lab-mini call without JSON mode" || echo "❌ make one lab-mini call without JSON mode or a system message"
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Asking for JSON in words often returns JSON wrapped in text or fences.
- `json.loads()` fails loudly - catch it and record what happened.
- Rare failures become daily failures at production volume.
