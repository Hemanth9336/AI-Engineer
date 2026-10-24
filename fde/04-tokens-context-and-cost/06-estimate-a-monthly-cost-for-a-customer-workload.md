---
type: task
title: "Estimate a monthly cost for a customer workload"
minutes: 8
---

## Scenario

Meridian Logistics wants a support assistant for its 400 agents and asks what it will cost per month on each model tier.

## Set up

Prices are in dollars per million tokens. They are example prices for the course - real prices change, so always check the provider's page.

```bash
mkdir -p /root/fde-lab/04-tokens
cd /root/fde-lab/04-tokens
cat > prices.json <<'EOF'
{
  "lab-mini": {
    "input": 0.1,
    "output": 0.4
  },
  "lab-fast": {
    "input": 0.4,
    "output": 1.6
  },
  "lab-smart": {
    "input": 3.0,
    "output": 15.0
  }
}
EOF
cat > workload.json <<'EOF'
{
  "name": "Meridian support assistant",
  "requests_per_day": 12000,
  "avg_input_tokens": 2500,
  "avg_output_tokens": 300,
  "days": 30
}
EOF
```

## What to build

Write `/root/fde-lab/04-tokens/cost.py`, used as `python cost.py WORKLOAD_FILE PRICES_FILE`, that prints JSON:

```json
{
  "requests_per_month": 360000,
  "per_model": {
    "lab-mini": {"per_request": 0.00037, "per_month": 133.2},
    "...": "..."
  },
  "cheapest": "lab-mini"
}
```

- `requests_per_month` = requests per day x days.
- `per_request` = input and output cost for one average request, rounded to **6** decimals.
- `per_month` = the unrounded per-request cost x requests per month, rounded to **2** decimals.
- One entry per model in the prices file; `cheapest` is the model with the lowest monthly cost.

```bash
cd /root/fde-lab/04-tokens
python cost.py workload.json prices.json > estimate.json
cat estimate.json
```

The checker runs your script on a different workload and price list.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `cost = w["avg_input_tokens"] / 1e6 * p["input"] + w["avg_output_tokens"] / 1e6 * p["output"]`.
- Round only when writing the result, not before multiplying.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/04-tokens
cat > cost.py <<'EOF'
import json
import sys

w = json.load(open(sys.argv[1]))
prices = json.load(open(sys.argv[2]))
requests = w["requests_per_day"] * w["days"]
per_model = {}
for model, p in prices.items():
    cost = w["avg_input_tokens"] / 1e6 * p["input"] + w["avg_output_tokens"] / 1e6 * p["output"]
    per_model[model] = {"per_request": round(cost, 6), "per_month": round(cost * requests, 2)}
cheapest = min(per_model, key=lambda m: per_model[m]["per_month"])
print(json.dumps({"requests_per_month": requests, "per_model": per_model, "cheapest": cheapest}, indent=2))
EOF
python cost.py workload.json prices.json > estimate.json
cat estimate.json
```

</details>

## Check your work

```bash
D=/root/fde-lab/04-tokens; cd $D 2>/dev/null || echo "❌ create $D"
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
def expect(w, prices):
    req = w["requests_per_day"] * w["days"]
    pm = {}
    for m, p in prices.items():
        c = w["avg_input_tokens"] / 1e6 * p["input"] + w["avg_output_tokens"] / 1e6 * p["output"]
        pm[m] = {"per_request": round(c, 6), "per_month": round(c * req, 2)}
    return {"requests_per_month": req, "per_model": pm, "cheapest": min(pm, key=lambda m: pm[m]["per_month"])}
e = load("estimate.json")
ok(e == expect(load("workload.json"), load("prices.json")), "estimate.json is right for the Meridian workload", f"estimate.json should be {expect(load('workload.json'), load('prices.json'))}"[:400])
w2 = {"name": "x", "requests_per_day": 850, "avg_input_tokens": 6100, "avg_output_tokens": 900, "days": 22}
p2 = {"model-a": {"input": 0.25, "output": 2.0}, "model-b": {"input": 0.15, "output": 0.6}}
Path("/tmp/w2.json").write_text(json.dumps(w2)); Path("/tmp/p2.json").write_text(json.dumps(p2))
rc, out, err = run("cost.py", "/tmp/w2.json", "/tmp/p2.json")
try:
    got = json.loads(out)
except ValueError:
    got = None
ok(got == expect(w2, p2), "a different workload and price list are computed correctly", f"for the checker's workload expected {expect(w2, p2)} - got {out[:300]!r} {err[-150:]}")
PYEOF
```

## What you learned

- Cost per request = input tokens x input price + output tokens x output price (per million).
- Multiply by realistic volume - model choice can change the bill 10x or more.
- Show the assumptions with the total so the customer can adjust them.
