---
type: task
title: "Compute a full trajectory's cost from the log"
minutes: 9
---

## Set up

`run.jsonl` is the transcript of one 9-step run (one step used `lab-mini` for compaction). `prices.json` has the price per **million** tokens, input and output, for each model.

```bash
mkdir -p /root/harness-lab/32-cost
cd /root/harness-lab/32-cost
cat > run.jsonl <<'EOF'
{"run_id": "20260314-101500-c7d2e1", "ts": 1773483300, "type": "run_start", "task": "Find which log has the slowest request and open a ticket about it.", "model": "lab-fast"}
{"run_id": "20260314-101500-c7d2e1", "ts": 1773483301, "type": "model_call", "step": 0, "model": "lab-fast", "prompt_tokens": 2350, "completion_tokens": 40, "finish_reason": "tool_calls"}
{"run_id": "20260314-101500-c7d2e1", "ts": 1773483302, "type": "model_call", "step": 1, "model": "lab-fast", "prompt_tokens": 3800, "completion_tokens": 45, "finish_reason": "tool_calls"}
{"run_id": "20260314-101500-c7d2e1", "ts": 1773483303, "type": "model_call", "step": 2, "model": "lab-fast", "prompt_tokens": 5250, "completion_tokens": 50, "finish_reason": "tool_calls"}
{"run_id": "20260314-101500-c7d2e1", "ts": 1773483304, "type": "model_call", "step": 3, "model": "lab-fast", "prompt_tokens": 6700, "completion_tokens": 55, "finish_reason": "tool_calls"}
{"run_id": "20260314-101500-c7d2e1", "ts": 1773483305, "type": "model_call", "step": 4, "model": "lab-fast", "prompt_tokens": 8150, "completion_tokens": 60, "finish_reason": "tool_calls"}
{"run_id": "20260314-101500-c7d2e1", "ts": 1773483306, "type": "model_call", "step": 5, "model": "lab-mini", "prompt_tokens": 7400, "completion_tokens": 260, "finish_reason": "tool_calls"}
{"run_id": "20260314-101500-c7d2e1", "ts": 1773483307, "type": "model_call", "step": 6, "model": "lab-fast", "prompt_tokens": 2300, "completion_tokens": 70, "finish_reason": "tool_calls"}
{"run_id": "20260314-101500-c7d2e1", "ts": 1773483308, "type": "model_call", "step": 7, "model": "lab-fast", "prompt_tokens": 2900, "completion_tokens": 75, "finish_reason": "tool_calls"}
{"run_id": "20260314-101500-c7d2e1", "ts": 1773483309, "type": "model_call", "step": 8, "model": "lab-fast", "prompt_tokens": 3500, "completion_tokens": 80, "finish_reason": "stop"}
{"run_id": "20260314-101500-c7d2e1", "ts": 1773483310, "type": "run_end", "status": "done", "steps": 9}
EOF
cat > prices.json <<'EOF'
{
 "lab-fast": {
  "input": 3.0,
  "output": 15.0
 },
 "lab-mini": {
  "input": 0.25,
  "output": 2.0
 }
}
EOF
```

## What to build

Write `/root/harness-lab/32-cost/cost.py`, used as `python cost.py TRANSCRIPT PRICES`. From the `model_call` events, print JSON:

```json
{"total_usd": 0.0,
 "by_model": {"lab-fast": 0.0, "lab-mini": 0.0},
 "tokens": {"input": 0, "output": 0},
 "by_step": [{"step": 0, "model": "lab-fast", "usd": 0.0}],
 "most_expensive_step": 0}
```

- Cost of a call = `(prompt_tokens x input price + completion_tokens x output price) / 1,000,000`.
- Round every dollar amount to 6 decimals.

```bash
cd /root/harness-lab/32-cost
python cost.py run.jsonl prices.json | tee cost.json
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Skip events whose type isn't `model_call`.
- `max(steps, key=lambda s: s["usd"])` finds the most expensive step.

</details>

<details><summary>Solution</summary>

```bash
cd /root/harness-lab/32-cost
cat > cost.py <<'EOF'
"""Cost of one agent run from its transcript. Usage: python cost.py TRANSCRIPT PRICES"""
import json
import sys


def cost(transcript_lines, prices):
    steps, by_model, tokens = [], {}, {"input": 0, "output": 0}
    for line in transcript_lines:
        e = json.loads(line)
        if e.get("type") != "model_call":
            continue
        p = prices[e["model"]]
        usd = (e["prompt_tokens"] * p["input"] + e["completion_tokens"] * p["output"]) / 1_000_000
        steps.append({"step": e["step"], "model": e["model"], "usd": round(usd, 6)})
        by_model[e["model"]] = by_model.get(e["model"], 0) + usd
        tokens["input"] += e["prompt_tokens"]
        tokens["output"] += e["completion_tokens"]
    total = sum(s["usd"] for s in steps)
    return {"total_usd": round(total, 6), "by_model": {m: round(v, 6) for m, v in by_model.items()}, "tokens": tokens,
            "by_step": steps, "most_expensive_step": max(steps, key=lambda s: s["usd"])["step"] if steps else None}


if __name__ == "__main__":
    lines = [l for l in open(sys.argv[1]) if l.strip()]
    print(json.dumps(cost(lines, json.load(open(sys.argv[2]))), indent=1))

EOF
python cost.py run.jsonl prices.json | tee cost.json
```

</details>

## Check your work

```bash
D=/root/harness-lab/32-cost; cd $D 2>/dev/null || echo "❌ create $D"
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
import random, tempfile
prices = json.load(open("prices.json"))
def expect(lines):
    calls = [json.loads(l) for l in lines if json.loads(l).get("type") == "model_call"]
    per = [(c["step"], c["model"], (c["prompt_tokens"] * prices[c["model"]]["input"] + c["completion_tokens"] * prices[c["model"]]["output"]) / 1e6) for c in calls]
    bym = {}
    for _, mdl, u in per:
        bym[mdl] = bym.get(mdl, 0) + u
    return {"total_usd": round(sum(u for *_, u in per), 6), "by_model": {k: round(v, 6) for k, v in bym.items()},
            "tokens": {"input": sum(c["prompt_tokens"] for c in calls), "output": sum(c["completion_tokens"] for c in calls)},
            "steps": [(s, mdl, round(u, 6)) for s, mdl, u in per], "most": max(per, key=lambda x: x[2])[0]}
def same(got, want):
    if not isinstance(got, dict):
        return False
    steps = [(s.get("step"), s.get("model"), s.get("usd")) for s in got.get("by_step") or []]
    return (abs((got.get("total_usd") or 0) - want["total_usd"]) < 2e-6 and got.get("tokens") == want["tokens"] and got.get("most_expensive_step") == want["most"]
            and set((got.get("by_model") or {}).keys()) == set(want["by_model"]) and all(abs(got["by_model"][k] - v) < 2e-6 for k, v in want["by_model"].items())
            and len(steps) == len(want["steps"]) and all(a[:2] == b[:2] and abs((a[2] or 0) - b[2]) < 2e-6 for a, b in zip(steps, want["steps"])))
lines = [l for l in open("run.jsonl") if l.strip()]
want = expect(lines)
got = load("cost.json")
ok(same(got, want), f"cost.json is right: ${want['total_usd']} in total, step {want['most']} the most expensive", f"expected total {want['total_usd']}, by_model {want['by_model']}, tokens {want['tokens']}, most expensive step {want['most']} - got {str(got)[:300]}")
rng = random.Random(7)
other = [json.dumps({"type": "run_start"})] + [json.dumps({"type": "model_call", "step": i, "model": rng.choice(["lab-fast", "lab-mini"]), "prompt_tokens": rng.randint(100, 9000), "completion_tokens": rng.randint(5, 400)}) for i in range(6)] + [json.dumps({"type": "tool_call", "step": 1})]
d = Path(tempfile.mkdtemp())
(d / "r.jsonl").write_text("\n".join(other) + "\n")
r = subprocess.run([sys.executable, "cost.py", str(d / "r.jsonl"), "prices.json"], capture_output=True, text=True, timeout=30)
try:
    g2 = json.loads(r.stdout)
except ValueError:
    g2 = None
ok(same(g2, expect(other)), "cost.py computes any transcript correctly", f"on another transcript: {r.stdout[:200]!r} {r.stderr[-150:]}")
PYEOF
```

## What you learned

- Every step re-sends the history, so agent cost grows faster than the step count.
- Per-call usage in the transcript plus a price table gives cost per run, model and step.
- The most expensive step is usually the one after the biggest tool result.
