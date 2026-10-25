---
type: challenge
title: "Challenge: measure two models and write the rubric"
minutes: 22
---

## Scenario

Your team lead asks: "Should data questions like this go to haiku or sonnet?" Opinions are cheap. You will answer with measurements, and leave behind a rubric the team can apply without re-running the experiment.

## Set up

Set up creates `/root/mastery/038-measure/data/orders.csv`: 60 orders with `order_id`, `region`, and `amount_cents`.

```bash
rm -rf /root/mastery/038-measure && mkdir -p /root/mastery/038-measure/data && cd /root/mastery/038-measure
cat > data/orders.csv <<'EOF'
order_id,region,amount_cents
1001,US,9969
1002,EU,11915
1003,EU,3788
1004,US,6193
1005,EU,9580
1006,US,3072
1007,APAC,2372
1008,APAC,19972
1009,US,5682
1010,APAC,15241
1011,EU,12068
1012,APAC,14450
1013,EU,6991
1014,EU,5345
1015,US,13400
1016,APAC,4180
1017,EU,12975
1018,EU,17125
1019,US,4046
1020,APAC,11305
1021,APAC,6109
1022,US,9105
1023,LATAM,1808
1024,APAC,13963
1025,EU,5318
1026,EU,5345
1027,US,21323
1028,APAC,19576
1029,EU,18998
1030,LATAM,9873
1031,US,18635
1032,LATAM,6473
1033,US,7033
1034,EU,11132
1035,EU,2748
1036,LATAM,2813
1037,EU,15003
1038,LATAM,20127
1039,US,7785
1040,US,18158
1041,LATAM,15815
1042,EU,2773
1043,LATAM,13471
1044,EU,5529
1045,APAC,2218
1046,LATAM,7356
1047,EU,13642
1048,US,20186
1049,US,16815
1050,US,10638
1051,LATAM,19733
1052,EU,1805
1053,LATAM,11396
1054,LATAM,11880
1055,US,8590
1056,EU,17453
1057,APAC,5235
1058,US,15270
1059,APAC,9119
1060,EU,12535
EOF
echo "$(($(wc -l < data/orders.csv) - 1)) orders"
```

## What to build

The task every run performs:
> Using python3, count the rows in data/orders.csv where region is EU and amount_cents is greater than 10000. Reply with only the number.

1. `measure.sh`: compute the true answer yourself with a python3 one-liner (your oracle). Then run the task **3 times with `--model haiku` and 3 times with `--model sonnet`**, with the same tools (`Bash(python3 *)`), `--max-turns 6`, JSON output, and stdin closed.
   - Save each run as `runs/<model>-<n>.json`.
   - Append one row per run to `measurements.csv` with the header `model,run,correct,wall_s,duration_ms,turns,cost_usd,input_tokens,output_tokens`. `correct` is `1` or `0` against your oracle, and `wall_s` is your own wall clock.
2. `summarize.py <csv> <out.json>`: per model, `runs`, `successes`, `success_rate` (4 decimals), `median_wall_s` (3), `median_cost_usd` (6), `total_cost_usd` (6), and `cost_per_success` (6, or `null` when nothing passed). Write it to `summary.json`.
3. `rubric.md` with three sections:
   - `## Measurements`: a table quoting each model's median cost with 4 decimals.
   - `## Rubric`: at least three rules, one of them deciding by cost per success.
   - `## Decision`: the tier for this task class, and when to escalate.

The checker matches every CSV row to its JSON file, re-scores each answer, recomputes your summary, and feeds `summarize.py` a test CSV of its own.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `TIMEFORMAT=%R` plus `{ time cmd; } 2>&1` captures bash's wall clock as plain seconds.
- jq's `@csv` turns an array into one correctly quoted CSV line.
- Cost per success divides the total cost of all runs by the number of passes, failed runs included.

</details>

<details><summary>Solution</summary>

```bash
cd /root/mastery/038-measure
cat > measure.sh <<'EOF'
#!/usr/bin/env bash
# measure.sh - the same task, 3 runs per model; one JSON file and one CSV row per run.
set -uo pipefail
cd "$(dirname "$0")"
P='Using python3, count the rows in data/orders.csv where region is EU and amount_cents is greater than 10000. Reply with only the number.'
want=$(python3 -c 'import csv; print(sum(1 for r in csv.DictReader(open("data/orders.csv")) if r["region"] == "EU" and int(r["amount_cents"]) > 10000))')
mkdir -p runs
echo "model,run,correct,wall_s,duration_ms,turns,cost_usd,input_tokens,output_tokens" > measurements.csv
TIMEFORMAT=%R
for model in haiku sonnet; do
  for i in 1 2 3; do
    out=runs/$model-$i.json
    wall=$( { time claude -p "$P" --model "$model" --allowedTools "Bash(python3 *)" --max-turns 6 \
                --output-format json < /dev/null > "$out" 2>/dev/null; } 2>&1 )
    got=$(jq -r '.result // ""' "$out" 2>/dev/null | tr -d '[:space:]')
    correct=0; [ "$got" = "$want" ] && correct=1
    jq -r --arg m "$model" --arg i "$i" --arg c "$correct" --arg w "$wall" \
      '[$m, $i, $c, $w, .duration_ms, .num_turns, .total_cost_usd, .usage.input_tokens, .usage.output_tokens] | @csv' "$out" >> measurements.csv \
      || echo "$model,$i,0,$wall,0,0,0,0,0" >> measurements.csv
  done
done
python3 summarize.py measurements.csv summary.json
EOF
cat > summarize.py <<'EOF'
#!/usr/bin/env python3
"""summarize.py <measurements.csv> <summary.json> - per model: success rate, medians, and cost per successful run."""
import csv
import json
import statistics
import sys

rows = list(csv.DictReader(open(sys.argv[1])))
out = {}
for model in sorted({r["model"] for r in rows}):
    rs = [r for r in rows if r["model"] == model]
    wins = sum(r["correct"] == "1" for r in rs)
    total = sum(float(r["cost_usd"]) for r in rs)
    out[model] = {
        "runs": len(rs),
        "successes": wins,
        "success_rate": round(wins / len(rs), 4),
        "median_wall_s": round(statistics.median(float(r["wall_s"]) for r in rs), 3),
        "median_cost_usd": round(statistics.median(float(r["cost_usd"]) for r in rs), 6),
        "total_cost_usd": round(total, 6),
        "cost_per_success": round(total / wins, 6) if wins else None,
    }
json.dump(out, open(sys.argv[2], "w"), indent=2)
print(json.dumps(out, indent=2))
EOF
chmod +x measure.sh summarize.py
./measure.sh
python3 - <<'PY'
import json
s = json.load(open("summary.json"))
row = lambda m, v: f"| {m} | {v['successes']}/{v['runs']} | {v['median_wall_s']} s | ${v['median_cost_usd']:.4f} | " + (f"${v['cost_per_success']:.4f}" if v["cost_per_success"] is not None else "n/a") + " |"
eligible = [m for m, v in s.items() if v["success_rate"] == 1.0]
pick = min(eligible, key=lambda m: (s[m]["cost_per_success"], s[m]["median_wall_s"])) if eligible else "sonnet"
open("rubric.md", "w").write("\n".join([
    "# Model tier rubric - data questions with an oracle", "",
    "## Measurements", "",
    "Task: count EU orders over 100.00 in data/orders.csv. Three runs per model, scored against an independent python3 count.", "",
    "| Model | Passed | Median wall | Median cost | Cost per success |", "|---|---|---|---|---|",
    *[row(m, v) for m, v in s.items()], "",
    "## Rubric", "",
    "- A tier is eligible only if it passed every measured run of this task class.",
    "- Among eligible tiers, choose the lowest cost per success; break ties with median wall time.",
    "- If a run fails its check twice, escalate to the next tier up and log the escalation.",
    "- Re-measure when a model version changes, for a new task class, or monthly.", "",
    "## Decision", "",
    f"Use **{pick}** for data questions that have an oracle; escalate to the next tier up after two failed checks.", ""]))
print(open("rubric.md").read())
PY
```

</details>

## Check your work

```bash
D=/root/mastery/038-measure; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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
WANT = '10'

import csv, io, statistics
want = WANT
rows = list(csv.DictReader(io.StringIO(text("measurements.csv"))))
cols = ["model", "run", "correct", "wall_s", "duration_ms", "turns", "cost_usd", "input_tokens", "output_tokens"]
ok(rows and list(rows[0].keys()) == cols, "measurements.csv has the expected columns", f"measurements.csv header should be {','.join(cols)}")
per = {m: [r for r in rows if r.get("model") == m] for m in ("haiku", "sonnet")}
ok(len(rows) == 6 and all(len(v) == 3 for v in per.values()), "three runs per model, six rows", f"expected 3 haiku and 3 sonnet rows - got { {m: len(v) for m, v in per.items()} }")
def mods(env):
    return set((env.get("modelUsage") or {}).keys())
bad, wrong = [], []
for r in rows:
    env = load(f"runs/{r.get('model')}-{r.get('run')}.json") or {}
    if not env:
        bad.append(f"runs/{r.get('model')}-{r.get('run')}.json missing")
        continue
    same = (str(env.get("num_turns")) == r["turns"] and abs(float(env.get("total_cost_usd") or 0) - float(r["cost_usd"] or 0)) < 1e-9
            and str(env.get("duration_ms")) == r["duration_ms"] and str((env.get("usage") or {}).get("input_tokens")) == r["input_tokens"])
    if not same:
        bad.append(f"{r['model']}-{r['run']}")
    got = "".join(str(env.get("result") or "").split())
    if (got == want) != (r["correct"] == "1"):
        wrong.append(f"{r['model']}-{r['run']}: result {got!r}, scored {r['correct']}")
ok(rows and not bad, "every CSV row matches its run's JSON envelope", f"these rows don't match runs/<model>-<run>.json: {bad}")
ok(rows and not wrong, f"each run is scored against the true answer ({want})", f"correct column disagrees with the real answer: {wrong}")
hk = [r for r in per["haiku"] if any(is_haiku(x) for x in mods(load(f"runs/haiku-{r['run']}.json") or {}))]
sn = [r for r in per["sonnet"] if any(not is_haiku(x) for x in mods(load(f"runs/sonnet-{r['run']}.json") or {}))]
ok(len(hk) == 3 and len(sn) == 3, "haiku runs used the haiku tier and sonnet runs did not", "run the haiku rows with --model haiku and the sonnet rows with --model sonnet (check modelUsage)")
ok(all(r["wall_s"] and float(r["wall_s"]) > 0 for r in rows), "every run has a measured wall time", "fill wall_s with the wall-clock seconds of each run")
sm = load("summary.json") or {}
def expect(rs):
    wins = sum(r["correct"] == "1" for r in rs)
    tot = sum(float(r["cost_usd"]) for r in rs)
    return {"runs": len(rs), "successes": wins, "success_rate": round(wins / len(rs), 4),
            "median_wall_s": round(statistics.median(float(r["wall_s"]) for r in rs), 3),
            "median_cost_usd": round(statistics.median(float(r["cost_usd"]) for r in rs), 6),
            "total_cost_usd": round(tot, 6), "cost_per_success": round(tot / wins, 6) if wins else None}
def close(a, b):
    return a == b or (isinstance(a, (int, float)) and isinstance(b, (int, float)) and abs(a - b) < 1e-6)
diff = [m for m in per if per[m] and not all(close((sm.get(m) or {}).get(k), v) for k, v in expect(per[m]).items())]
ok(sm and not diff, "summary.json matches a recomputation from the CSV", f"summary.json disagrees with measurements.csv for {diff}")
with tempfile.TemporaryDirectory() as t:
    Path(t, "m.csv").write_text(",".join(cols) + "\n" + "\n".join([
        "a,1,1,1.0,10,2,0.01,5,1", "a,2,0,5.0,10,2,0.02,5,1", "a,3,1,3.0,10,2,0.03,5,1",
        "b,1,0,2.0,10,2,0.05,5,1", "b,2,0,2.0,10,2,0.05,5,1"]) + "\n")
    rc, out, err = sh([sys.executable, "summarize.py", str(Path(t, "m.csv")), str(Path(t, "s.json"))])
    got = load(Path(t, "s.json")) or {}
a, b = got.get("a") or {}, got.get("b") or {}
ok(rc == 0 and close(a.get("success_rate"), 0.6667) and close(a.get("median_wall_s"), 3.0) and close(a.get("median_cost_usd"), 0.02) and close(a.get("cost_per_success"), 0.03),
   "summarize.py computes success rate, medians, and cost per success", f"on a test CSV, model a should give success_rate 0.6667, median_wall_s 3.0, median_cost_usd 0.02, cost_per_success 0.03 - got {a or err[-200:]}")
ok(rc == 0 and b.get("successes") == 0 and b.get("cost_per_success") is None, "a model with no passes gets cost_per_success null", f"a model that never passed must have cost_per_success null - got {b}")
rb = text("rubric.md")
heads = [h for h in ("## Measurements", "## Rubric", "## Decision") if h not in rb]
ok(rb and not heads, "rubric.md has Measurements, Rubric, and Decision sections", f"rubric.md is missing {heads}")
quoted = [m for m in per if (sm.get(m) or {}).get("median_cost_usd") is not None and f"{sm[m]['median_cost_usd']:.4f}" not in rb]
ok(rb and sm and not quoted, "the rubric quotes each model's measured median cost", f"quote each model's median cost from summary.json with 4 decimals in rubric.md - missing for {quoted}")
sec = rb.split("## Rubric")[-1].split("## Decision")[0] if "## Rubric" in rb else ""
ok(sum(1 for l in sec.splitlines() if l.strip().startswith(("-", "*", "1", "2", "3", "4", "5"))) >= 3 and "cost per success" in sec.lower(),
   "the rubric has at least three rules and uses cost per success", "write at least three rules under ## Rubric, including how cost per success decides between eligible tiers")
dec = rb.split("## Decision")[-1].lower() if "## Decision" in rb else ""
ok(("haiku" in dec or "sonnet" in dec) and "escalat" in dec, "the decision names a tier and an escalation path", "under ## Decision, name the tier to use and when to escalate")
PYEOF
```

## What you learned

- Compare tiers on the same task with an oracle, several runs each, and report medians.
- Cost per successful task, not price per token, decides which tier is cheaper.
- A rubric turns one experiment into a rule: eligibility floor, cost per success, escalation, re-measure triggers.
