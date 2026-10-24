---
type: task
title: "Extract ticket fields into valid JSON"
minutes: 7
---

## Set up

```bash
mkdir -p /root/fde-lab/10-structured
```

## What to build

Write `/root/fde-lab/10-structured/extract.py`, used as `python extract.py TICKET_TEXT`, that prints one JSON object with exactly the keys `order_id`, `issue` and `urgency`.

- Use `lab-mini`, `temperature=0` and `response_format={"type": "json_object"}`.
- Use this system prompt (or your own improvement of it):
  ```text
  Extract fields from a Meridian Logistics support ticket. Reply with a JSON object with exactly these keys: "order_id" (like MER-12345, or null if none is mentioned), "issue" (one of: damaged, late, lost, address, billing, other), "urgency" (one of: low, medium, high). Example: {"order_id": "MER-10001", "issue": "late", "urgency": "medium"}
  ```
- Parse the reply with `json.loads()` and print it with `json.dumps()`.

```bash
cd /root/fde-lab/10-structured
python extract.py "Order MER-55120 arrived with two crushed cases. We need a refund before Friday."
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Put the system prompt in a Python variable; mind the quotes - triple quotes are easiest.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/10-structured
cat > extract.py <<'EOF'
import json
import sys

from openai import OpenAI

SYSTEM = 'Extract fields from a Meridian Logistics support ticket. Reply with a JSON object with exactly these keys: "order_id" (like MER-12345, or null if none is mentioned), "issue" (one of: damaged, late, lost, address, billing, other), "urgency" (one of: low, medium, high). Example: {"order_id": "MER-10001", "issue": "late", "urgency": "medium"}'
resp = OpenAI().chat.completions.create(
    model="lab-mini",
    temperature=0,
    response_format={"type": "json_object"},
    messages=[{"role": "system", "content": SYSTEM}, {"role": "user", "content": sys.argv[1]}],
)
print(json.dumps(json.loads(resp.choices[0].message.content)))
EOF
python extract.py "Order MER-55120 arrived with two crushed cases. We need a refund before Friday."
```

</details>

## Check your work

```bash
D=/root/fde-lab/10-structured; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/extract.py 2>/dev/null && [ -s $D/extract.py ] && echo "✅ extract.py reads the key from the environment" || echo "❌ extract.py must not contain a key - let the SDK read it from the environment"
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
cases = [("Hello, I was billed twice for order MER-70412 last month, please fix it when you can.", {"order_id": "MER-70412", "issue": "billing"}),
         ("Do you have a phone number for the Rotterdam depot?", {"order_id": None, "issue": "other"})]
for text, want in cases:
    rc, out, err = run("extract.py", text)
    try:
        d = json.loads(out)
    except ValueError:
        d = None
    good = isinstance(d, dict) and set(d) == {"order_id", "issue", "urgency"} and d.get("urgency") in ("low", "medium", "high")
    ok(good and all(d.get(k) == v for k, v in want.items()), f"'{text[:40]}...' -> {want}", f"'{text[:40]}...' should print a JSON object with exactly order_id, issue, urgency matching {want} - got {out[:200]!r} {err[-150:]}")
PYEOF
jq -se 'any(.[]; .ok and .api == "chat.completions" and .model == "lab-mini" and (.client | startswith("OpenAI/Python")) and .json_mode and .temperature == 0)' /var/log/ailab/requests.jsonl >/dev/null 2>&1 && echo "✅ the gateway logged lab-mini calls in JSON mode at temperature 0" || echo "❌ no lab-mini call with response_format json_object at temperature 0"
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- `response_format={"type": "json_object"}` guarantees valid JSON syntax.
- The prompt must still name the fields, allowed values and what to do when data is missing.
- Valid JSON is not the same as the right shape - that's the next lesson.
