---
type: task
title: "Estimate an agent's monthly cost"
minutes: 8
---

## Scenario

Stackline wants to run a log-triage agent 5,000 times a day and asks what it will cost per month on each model tier. You measured one typical trajectory: four steps, with input tokens growing as history builds up.

## Set up

Prices are in dollars per million tokens. They are example prices for the course - real prices change, so always check the provider's page.

```bash
mkdir -p /root/harness-lab/05-tokens
cd /root/harness-lab/05-tokens
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
  "name": "Stackline log-triage agent",
  "tasks_per_day": 5000,
  "days": 30,
  "steps": [
    {
      "input": 800,
      "output": 60
    },
    {
      "input": 1400,
      "output": 50
    },
    {
      "input": 2900,
      "output": 80
    },
    {
      "input": 3100,
      "output": 40
    }
  ]
}
EOF
```

## What to build

Write `/root/harness-lab/05-tokens/agent_cost.py`, used as `python agent_cost.py WORKLOAD_FILE PRICES_FILE`, that prints JSON:

```json
{
  "tasks_per_month": 150000,
  "tokens_per_task": {"input": 8200, "output": 230},
  "per_model": {
    "lab-mini": {"per_task": 0.000912, "per_month": 136.8},
    "...": "..."
  },
  "cheapest": "lab-mini"
}
```

- `tasks_per_month` = tasks per day x days.
- `tokens_per_task` = the sum of input and of output tokens over all steps.
- `per_task` = the cost of one task (all steps), rounded to **6** decimals.
- `per_month` = the unrounded per-task cost x tasks per month, rounded to **2** decimals.
- One entry per model in the prices file; `cheapest` has the lowest monthly cost.

```bash
cd /root/harness-lab/05-tokens
python agent_cost.py workload.json prices.json > agent_estimate.json
cat agent_estimate.json
```

The checker also runs your script on a longer trajectory and different prices.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `inp = sum(s["input"] for s in w["steps"])`.
- Round only when writing the result, not before multiplying.

</details>

<details><summary>Solution</summary>

```bash
cd /root/harness-lab/05-tokens
cat > agent_cost.py <<'EOF'
import json
import sys

w = json.load(open(sys.argv[1]))
prices = json.load(open(sys.argv[2]))
tasks = w["tasks_per_day"] * w["days"]
inp = sum(s["input"] for s in w["steps"])
out = sum(s["output"] for s in w["steps"])
per_model = {}
for model, p in prices.items():
    cost = inp / 1e6 * p["input"] + out / 1e6 * p["output"]
    per_model[model] = {"per_task": round(cost, 6), "per_month": round(cost * tasks, 2)}
cheapest = min(per_model, key=lambda m: per_model[m]["per_month"])
print(json.dumps({"tasks_per_month": tasks, "tokens_per_task": {"input": inp, "output": out},
                  "per_model": per_model, "cheapest": cheapest}, indent=2))
EOF
python agent_cost.py workload.json prices.json > agent_estimate.json
cat agent_estimate.json
```

</details>

## Check your work

```bash
D=/root/harness-lab/05-tokens; cd $D 2>/dev/null || echo "❌ create $D"
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
sys.path.insert(0, '/opt/harness')
from labmock import MockModel
def expect(w, prices):
    n = w["tasks_per_day"] * w["days"]
    i, o = sum(s["input"] for s in w["steps"]), sum(s["output"] for s in w["steps"])
    pm = {}
    for m, p in prices.items():
        c = i / 1e6 * p["input"] + o / 1e6 * p["output"]
        pm[m] = {"per_task": round(c, 6), "per_month": round(c * n, 2)}
    return {"tasks_per_month": n, "tokens_per_task": {"input": i, "output": o}, "per_model": pm, "cheapest": min(pm, key=lambda m: pm[m]["per_month"])}
want = expect(load("workload.json"), load("prices.json"))
ok(load("agent_estimate.json") == want, "agent_estimate.json is right for the log-triage agent", f"agent_estimate.json should be {want}"[:400])
w2 = {"name": "x", "tasks_per_day": 1200, "days": 22, "steps": [{"input": 900 + 1700 * k, "output": 70} for k in range(9)]}
p2 = {"model-a": {"input": 0.25, "output": 2.0}, "model-b": {"input": 0.15, "output": 0.6}, "model-c": {"input": 1.0, "output": 4.0}}
Path("/tmp/aw2.json").write_text(json.dumps(w2)); Path("/tmp/ap2.json").write_text(json.dumps(p2))
rc, out, err = run("agent_cost.py", "/tmp/aw2.json", "/tmp/ap2.json")
try:
    got = json.loads(out)
except ValueError:
    got = None
ok(got == expect(w2, p2), "a 9-step trajectory with different prices is computed correctly", f"for the checker's workload expected {expect(w2, p2)} - got {out[:300]!r} {err[-150:]}")
PYEOF
```

## What you learned

- An agent task costs the sum of every step's input and output tokens.
- Re-sent history makes input tokens dominate - more steps raise the cost faster than linearly.
- Keep the assumptions (tasks, steps, prices) next to the total so the levers are visible.
