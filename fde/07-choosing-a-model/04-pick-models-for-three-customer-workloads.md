---
type: task
title: "Pick models for three customer workloads"
minutes: 9
---

## Scenario

Meridian Logistics has three candidate workloads. You've measured each model's quality on a sample, its typical latency, and its cost.

## Set up

```bash
mkdir -p /root/fde-lab/07-models
cd /root/fde-lab/07-models
cat > catalog.json <<'EOF'
{
  "lab-mini": {
    "quality": 0.72,
    "latency_s": 0.6,
    "cost_per_1k_requests": 0.35
  },
  "lab-fast": {
    "quality": 0.83,
    "latency_s": 1.1,
    "cost_per_1k_requests": 1.4
  },
  "lab-smart": {
    "quality": 0.92,
    "latency_s": 3.2,
    "cost_per_1k_requests": 9.5
  },
  "lab-reasoning": {
    "quality": 0.95,
    "latency_s": 14.0,
    "cost_per_1k_requests": 22.0
  }
}
EOF
cat > workloads.json <<'EOF'
[
  {
    "id": "ticket-routing",
    "description": "Classify 40,000 support tickets a day into 6 queues",
    "min_quality": 0.7,
    "max_latency_s": 2
  },
  {
    "id": "live-chat",
    "description": "Answer support agents' questions during live calls",
    "min_quality": 0.8,
    "max_latency_s": 2
  },
  {
    "id": "contract-review",
    "description": "Flag risky clauses in 30 carrier contracts a week",
    "min_quality": 0.9,
    "max_latency_s": 60
  }
]
EOF
```

## What to build

Write `/root/fde-lab/07-models/pick.py`, used as `python pick.py CATALOG WORKLOADS`, that prints JSON mapping each workload id to a choice:

```json
{
  "ticket-routing": {"model": "lab-mini", "monthly_note": "..."},
  "...": "..."
}
```

Rule: the **cheapest** model whose `quality >= min_quality` **and** `latency_s <= max_latency_s`. If no model qualifies, use `null` for `model`. `monthly_note` is free text for the customer - one sentence on why.

```bash
cd /root/fde-lab/07-models
python pick.py catalog.json workloads.json > picks.json
cat picks.json
```

The checker also runs it on a different catalog and workloads.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `fits = [m for m, s in catalog.items() if s["quality"] >= w["min_quality"] and s["latency_s"] <= w["max_latency_s"]]`.
- `min(fits, key=lambda m: catalog[m]["cost_per_1k_requests"]) if fits else None`.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/07-models
cat > pick.py <<'EOF'
import json
import sys

catalog = json.load(open(sys.argv[1]))
workloads = json.load(open(sys.argv[2]))
picks = {}
for w in workloads:
    fits = [m for m, s in catalog.items() if s["quality"] >= w["min_quality"] and s["latency_s"] <= w["max_latency_s"]]
    model = min(fits, key=lambda m: catalog[m]["cost_per_1k_requests"]) if fits else None
    note = (f"{model} is the cheapest model meeting quality {w['min_quality']} within {w['max_latency_s']}s."
            if model else "No model meets both the quality and latency requirements - revisit the requirements or improve the prompt and retrieval.")
    picks[w["id"]] = {"model": model, "monthly_note": note}
print(json.dumps(picks, indent=2))
EOF
python pick.py catalog.json workloads.json > picks.json
cat picks.json
```

</details>

## Check your work

```bash
D=/root/fde-lab/07-models; cd $D 2>/dev/null || echo "❌ create $D"
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
def expect(cat, wl):
    out = {}
    for w in wl:
        fits = [m for m, s in cat.items() if s["quality"] >= w["min_quality"] and s["latency_s"] <= w["max_latency_s"]]
        out[w["id"]] = min(fits, key=lambda m: cat[m]["cost_per_1k_requests"]) if fits else None
    return out
def models(p):
    return {k: v.get("model") for k, v in p.items()} if isinstance(p, dict) and all(isinstance(v, dict) and str(v.get("monthly_note", "")).strip() for v in p.values()) else None
ok(models(load("picks.json")) == expect(load("catalog.json"), load("workloads.json")), "picks.json picks the right model for each Meridian workload", f"picks.json should choose {expect(load('catalog.json'), load('workloads.json'))}, each with a monthly_note")
cat = {"a": {"quality": 0.9, "latency_s": 5, "cost_per_1k_requests": 4}, "b": {"quality": 0.8, "latency_s": 1, "cost_per_1k_requests": 2}, "c": {"quality": 0.95, "latency_s": 2, "cost_per_1k_requests": 8}}
wl = [{"id": "x", "min_quality": 0.85, "max_latency_s": 3}, {"id": "y", "min_quality": 0.85, "max_latency_s": 10}, {"id": "z", "min_quality": 0.99, "max_latency_s": 10}]
Path("/tmp/cat2.json").write_text(json.dumps(cat)); Path("/tmp/wl2.json").write_text(json.dumps(wl))
rc, out, err = run("pick.py", "/tmp/cat2.json", "/tmp/wl2.json")
try:
    got = models(json.loads(out))
except ValueError:
    got = None
ok(got == expect(cat, wl), "a different catalog and workloads are picked correctly, including no fit", f"for the checker's data expected {expect(cat, wl)} - got {got} {err[-150:]}")
PYEOF
```

## What you learned

- Turn requirements into numbers: minimum quality, maximum latency, volume.
- Choose the cheapest model that meets them - not the biggest.
- Sometimes nothing fits; say so and change the requirements or the approach.
