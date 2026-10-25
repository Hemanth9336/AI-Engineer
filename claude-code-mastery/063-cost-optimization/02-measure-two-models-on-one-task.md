---
type: task
title: "Measure two models on one task"
minutes: 30
---

## Set up

Set up creates `/root/mastery/063-cost` with two invoice cases in `cases/` and their expected totals. Case `b` lists a subtotal, VAT, and shipping before the total.

```bash
rm -rf /root/mastery/063-cost && mkdir -p /root/mastery/063-cost/cases && cd /root/mastery/063-cost
cat > cases/a.txt <<'EOF'
Invoice INV-7 from Northwind GmbH
Date: 2026-10-02
Total due: 1,240.50 EUR
EOF
cat > cases/a.expected <<'EOF'
1240.50
EOF
cat > cases/b.txt <<'EOF'
Invoice INV-9 from Contoso Ltd
Subtotal 900.00
VAT 171.00
Shipping 0.00
Total 1,071.00 EUR (pay by 2026-11-01)
EOF
cat > cases/b.expected <<'EOF'
1071.00
EOF
jq --version
```

## What to build

1. Write `measure.sh`. It runs every `cases/*.txt` on `--model haiku` and `--model sonnet`, with `--tools ""`, `--max-turns 1`, `--output-format json`, and this prompt:
   > Extract the total amount due from the invoice on stdin. Reply with the number only, digits and a dot, no thousands separator, no currency.

   Save each envelope as `runs/<model>-<case>.json`.
2. Write `compare.py [RUNS_DIR] [CASES_DIR]` (defaults `runs`, `cases`). It writes `comparison.json`:
   - `models.<model>`: `cost_usd` (the sum of `total_cost_usd`), `input_tokens`, `output_tokens`, `duration_ms`, `passed`, `total`, and `failed`.
     - A case passes when the envelope isn't an error and `.result` stripped equals `cases/<case>.expected` stripped.
   - `choice`: the cheapest model that passed every case, or `null`.
3. Run both scripts.

The checker re-runs `compare.py` on hidden run folders: one where both models pass, one with an error envelope, and one where nothing passes.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `Path(f).stem.split("-", 1)` splits `haiku-b` into the model and the case.
- `min(passing, key=lambda n: models[n]["cost_usd"])` picks the cheapest of the passing models.

</details>

<details><summary>Solution</summary>

```bash
cd /root/mastery/063-cost
cat > measure.sh <<'EOF'
#!/usr/bin/env bash
# measure.sh - run every case on every model and keep each envelope in runs/<model>-<case>.json
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p runs
prompt="Extract the total amount due from the invoice on stdin. Reply with the number only, digits and a dot, no thousands separator, no currency."
for model in haiku sonnet; do
  for f in cases/*.txt; do
    c=$(basename "$f" .txt)
    claude -p "$prompt" --model "$model" --tools "" --max-turns 1 --output-format json < "$f" > "runs/$model-$c.json" || true
    echo "$model $c: $(jq -r '.result' "runs/$model-$c.json") (\$$(jq -r '.total_cost_usd' "runs/$model-$c.json"))"
  done
done
EOF
cat > compare.py <<'EOF'
#!/usr/bin/env python3
"""compare.py [RUNS_DIR] [CASES_DIR] - score every model on every case and pick the cheapest one that passed them all."""
import json
import sys
from pathlib import Path

runs = Path(sys.argv[1] if len(sys.argv) > 1 else "runs")
cases = Path(sys.argv[2] if len(sys.argv) > 2 else "cases")
expected = {p.stem: p.read_text().strip() for p in sorted(cases.glob("*.expected"))}

models = {}
for f in sorted(runs.glob("*.json")):
    model, case = f.stem.split("-", 1)
    env = json.loads(f.read_text())
    usage = env.get("usage") or {}
    m = models.setdefault(model, {"cost_usd": 0.0, "input_tokens": 0, "output_tokens": 0, "duration_ms": 0, "passed": 0, "total": 0, "failed": []})
    m["cost_usd"] += env.get("total_cost_usd") or 0
    m["input_tokens"] += usage.get("input_tokens") or 0
    m["output_tokens"] += usage.get("output_tokens") or 0
    m["duration_ms"] += env.get("duration_ms") or 0
    m["total"] += 1
    if not env.get("is_error") and str(env.get("result", "")).strip() == expected.get(case):
        m["passed"] += 1
    else:
        m["failed"].append(case)

for m in models.values():
    m["cost_usd"] = round(m["cost_usd"], 6)
passing = [name for name, m in models.items() if m["total"] == len(expected) and m["passed"] == m["total"]]
choice = min(passing, key=lambda n: models[n]["cost_usd"]) if passing else None
out = {"cases": sorted(expected), "models": models, "choice": choice}
Path("comparison.json").write_text(json.dumps(out, indent=2) + "\n")
for name, m in models.items():
    print(f"{name:8} {m['passed']}/{m['total']} passed  ${m['cost_usd']:.6f}  {m['input_tokens']} in / {m['output_tokens']} out")
print("choice:", choice)
EOF
chmod +x measure.sh compare.py
./measure.sh
python3 compare.py runs cases
cat comparison.json
```

</details>

## Check your work

```bash
D=/root/mastery/063-cost; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
python3 - <<'PYEOF'
import glob, hashlib, json, os, re, subprocess, sys, tempfile
from pathlib import Path
sys.excepthook = lambda t, e, tb: print(f"❌ check stopped: {t.__name__}: {e}")
def ok(cond, good, bad):
    print(("✅ " + good) if cond else ("❌ " + bad))
def load(p):
    try:
        return json.loads(Path(p).read_text())
    except Exception:
        return None
def text(p):
    try:
        return Path(p).read_text()
    except Exception:
        return ""
def sha(p):
    try:
        return hashlib.sha256(Path(p).read_bytes()).hexdigest()
    except Exception:
        return None
def sh(cmd, cwd=None, env=None, input=None, timeout=60):
    try:
        r = subprocess.run(cmd, shell=isinstance(cmd, str), capture_output=True, text=True, cwd=cwd, input=input,
                           timeout=timeout, env=dict(os.environ, **(env or {})))
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return 124, "", "timed out"
def sessions(d):
    # Claude Code saves every session (console or -p) as ~/.claude/projects/<dir>/<id>.jsonl, one JSON row per event
    real, out = os.path.realpath(d), []
    for f in sorted(glob.glob(os.path.expanduser("~/.claude/projects/*/*.jsonl")), key=os.path.getmtime):
        rows = []
        for line in open(f, errors="replace"):
            try:
                rows.append(json.loads(line))
            except ValueError:
                pass
        if any(r.get("cwd") and os.path.realpath(r["cwd"]) == real for r in rows):
            out.append(rows)
    return out
def ran(pat, d=None):
    return [rows for rows in sessions(d or os.getcwd()) if any(re.search(pat, p, re.I | re.S) for p in prompts(rows))]
def content(r):
    c = (r.get("message") or {}).get("content")
    return c if isinstance(c, list) else ([{"type": "text", "text": c}] if isinstance(c, str) else [])
def prompts(rows):
    return [b.get("text", "") for r in rows if r.get("type") == "user" and not r.get("isMeta") for b in content(r) if b.get("type") == "text"]
def uses(rows):
    return [b for r in rows if r.get("type") == "assistant" for b in content(r) if b.get("type") == "tool_use"]
def results(rows):
    return [b for r in rows if r.get("type") == "user" for b in content(r) if b.get("type") == "tool_result"]
def models(rows):
    return {(r.get("message") or {}).get("model") for r in rows if r.get("type") == "assistant"} - {None, "<synthetic>"}
def is_haiku(m):
    return bool(m) and ("haiku" in m.lower() or m == os.environ.get("ANTHROPIC_DEFAULT_HAIKU_MODEL"))
def events(p):
    out = []
    for line in text(p).splitlines():
        try:
            out.append(json.loads(line))
        except ValueError:
            pass
    return out
def init(ev):
    return next((e for e in ev if e.get("type") == "system" and e.get("subtype") == "init"), {})
def result(ev):
    return next((e for e in ev if e.get("type") == "result"), {})
def ev_uses(ev):
    return [b for e in ev if e.get("type") == "assistant" for b in content(e) if b.get("type") == "tool_use"]
import shutil
files = sorted(p.name for p in Path("runs").glob("*.json"))
ok(files == ["haiku-a.json", "haiku-b.json", "sonnet-a.json", "sonnet-b.json"], "runs/ holds one envelope per model and case", f"run ./measure.sh - runs/ has {files}")
envs = {f: load(Path("runs", f)) or {} for f in files}
mu = {f: sorted((e.get("modelUsage") or {}).keys()) for f, e in envs.items()}
ok(all(e.get("type") == "result" and isinstance(e.get("total_cost_usd"), (int, float)) for e in envs.values())
   and all(("mini" in mu[f][0] or "haiku" in mu[f][0]) for f in files if f.startswith("haiku")) and all(mu[f] and "mini" not in mu[f][0] for f in files if f.startswith("sonnet")),
   "each envelope is a real JSON result, run on the model its name says", f"use --model haiku / --model sonnet with --output-format json - modelUsage {mu}")
cmp_ = load("comparison.json") or {}
m = cmp_.get("models") or {}
want = {k: round(sum((envs.get(f"{k}-{c}.json") or {}).get("total_cost_usd") or 0 for c in "ab"), 6) for k in ("haiku", "sonnet")}
ok(m and all(abs((m.get(k) or {}).get("cost_usd", -1) - want[k]) < 1e-6 for k in want), "comparison.json sums each model's cost from its envelopes",
   f"cost_usd per model should be the sum of total_cost_usd - want {want}, got " + str({k: v.get('cost_usd') for k, v in m.items()}))
ok((m.get("haiku") or {}).get("passed") == 1 and (m.get("sonnet") or {}).get("passed") == 2 and cmp_.get("choice") == "sonnet",
   "haiku missed the hard case, so the choice is sonnet - the cheapest model that passed every case",
   "score answers against cases/*.expected and choose the cheapest model with every case passed - got " + str({k: v.get('passed') for k, v in m.items()}) + f", choice {cmp_.get('choice')}")
def env(cost, result, err=False):
    return json.dumps({"type": "result", "subtype": "error_max_turns" if err else "success", "is_error": err, "result": result,
                       "total_cost_usd": cost, "duration_ms": 100, "usage": {"input_tokens": 10, "output_tokens": 2}})
def trial(rows):
    with tempfile.TemporaryDirectory() as t:
        shutil.copy("compare.py", t)
        Path(t, "r").mkdir(); Path(t, "c").mkdir()
        for c, exp in (("x", "1.00"), ("y", "2.00"), ("z", "3.00")):
            Path(t, "c", f"{c}.expected").write_text(exp + "\n")
        for name, body in rows.items():
            Path(t, "r", name).write_text(body)
        sh([sys.executable, "compare.py", "r", "c"], cwd=t)
        return (load(Path(t, "comparison.json")) or {}).get("choice", "missing")
both = {f"{mdl}-{c}.json": env(cost, v) for mdl, cost in (("small", 0.001), ("big", 0.01)) for c, v in (("x", "1.00"), ("y", "2.00"), ("z", "3.00"))}
ok(trial(both) == "small", "hidden runs where both models pass every case: the cheaper one wins", f"choose the cheapest passing model - got {trial(both)!r}")
errs = dict(both, **{"small-z.json": env(0.001, "3.00", err=True)})
ok(trial(errs) == "big", "an error envelope counts as a failure even if its result text looks right", f"treat is_error as a failed case - got {trial(errs)!r}")
none = {k: env(0.001, "nope") for k in both}
ok(trial(none) is None, "when no model passes everything, choice is null", f"choice should be null when nothing passes - got {trial(none)!r}")
PYEOF
```

## What you learned

- Compare models on the same prompt, tools, and cases, with answers checked deterministically.
- Decide by the cheapest model that passes every case; per-call price alone hides the failures.
- total_cost_usd, modelUsage, and usage in the envelope are all you need to measure cost per task.
