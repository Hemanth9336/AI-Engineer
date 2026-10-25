---
type: task
title: "Plan before you build"
minutes: 10
---

## Set up

Set up creates `/root/cc-lab/08-plan` with `report.py`, a small script that does everything in one function, and `data/sales.csv`.

```bash
mkdir -p /root/cc-lab/08-plan/data && cd /root/cc-lab/08-plan
[ -f report.py ] || cat > report.py <<'EOF'
"""Print a sales report per region. Usage: python3 report.py SALES_CSV"""
import csv
import sys


def main(path):
    totals = {}
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            totals[row["region"]] = totals.get(row["region"], 0) + int(row["amount_cents"])
    lines = ["Sales by region", "---------------"]
    for region, cents in sorted(totals.items(), key=lambda kv: (-kv[1], kv[0])):
        lines.append(f"{region:<10} {cents / 100:>10.2f}")
    lines.append("---------------")
    lines.append(f"{'TOTAL':<10} {sum(totals.values()) / 100:>10.2f}")
    print("\n".join(lines))


if __name__ == "__main__":
    main(sys.argv[1])
EOF
cat > data/sales.csv <<'EOF'
region,amount_cents
north,120050
south,98000
north,4500
east,98000
west,15025
south,2000
EOF
claude --version
```

## What to build

You'll split `report.py` into `load.py` (`load_sales(path)` - a list of `(region, amount_cents)` tuples, in file order) and `render.py` (`render(rows)` - the report text), with `report.py` still the entry point and its output byte-for-byte unchanged.

1. **Plan, read-only.** Save the current output, ask for a plan in plan mode, and save the plan to `PLAN.md` (the plan can arrive in an `ExitPlanMode` call or in the final result, so take both):

```bash
cd /root/cc-lab/08-plan
python3 report.py data/sales.csv > before.txt
claude -p "Plan how to split report.py into load.py (load_sales(path) returning a list of (region, amount_cents) tuples in file order) and render.py (render(rows) returning the report text), keeping report.py as the entry point with byte-identical output. Do not change any files yet." \
  --permission-mode plan --max-turns 8 --output-format stream-json --verbose > plan.jsonl
{ jq -r 'select(.type == "assistant") | .message.content[] | select(.type == "tool_use" and .name == "ExitPlanMode") | .input.plan' plan.jsonl
  jq -r 'select(.type == "result") | .result' plan.jsonl; } > PLAN.md
cat PLAN.md
```

2. **Review** `PLAN.md`. Does it name both new files and say how to check the output? If not, ask again with more detail.
3. **Build** from the plan, then compare:

```bash
claude -p "Implement the plan in PLAN.md exactly. Then run python3 report.py data/sales.csv to confirm the output is unchanged." \
  --permission-mode acceptEdits --allowedTools "Bash(python3 report.py:*)" --max-turns 14
python3 report.py data/sales.csv | diff before.txt - && echo "output unchanged"
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- In plan mode, any attempted edit is refused and listed in `permission_denials` - `plan.jsonl` shows whether that happened.
- `render(rows)` returns the text; `report.py` prints it.

</details>

<details><summary>Solution</summary>

```bash
cd /root/cc-lab/08-plan
python3 report.py data/sales.csv > before.txt
claude -p "Plan how to split report.py into load.py (load_sales(path) returning a list of (region, amount_cents) tuples in file order) and render.py (render(rows) returning the report text), keeping report.py as the entry point with byte-identical output. Do not change any files yet." \
  --permission-mode plan --max-turns 8 --output-format stream-json --verbose > plan.jsonl
{ jq -r 'select(.type == "assistant") | .message.content[] | select(.type == "tool_use" and .name == "ExitPlanMode") | .input.plan' plan.jsonl
  jq -r 'select(.type == "result") | .result' plan.jsonl; } > PLAN.md
cat PLAN.md
claude -p "Implement the plan in PLAN.md exactly. Then run python3 report.py data/sales.csv to confirm the output is unchanged." \
  --permission-mode acceptEdits --allowedTools "Bash(python3 report.py:*)" --max-turns 14
python3 report.py data/sales.csv | diff before.txt - && echo "output unchanged"
```

</details>

## Check your work

```bash
D=/root/cc-lab/08-plan; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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
ev = events("plan.jsonl")
ok(init(ev).get("permissionMode") == "plan", "plan.jsonl was a plan-mode run", "plan.jsonl should be a claude -p run with --permission-mode plan and --output-format stream-json --verbose")
writes = [u for u in ev_uses(ev) if u.get("name") in ("Edit", "Write", "NotebookEdit")]
errs = {b.get("tool_use_id") for e in ev if e.get("type") == "user" for b in content(e) if b.get("type") == "tool_result" and b.get("is_error")}
ok(ev and all(u.get("id") in errs for u in writes), "nothing was changed during planning", "a file edit succeeded during the plan run - plan with --permission-mode plan")
plan = text("PLAN.md")
ok(len([l for l in plan.splitlines() if l.strip()]) >= 3 and "load.py" in plan and "render.py" in plan, "PLAN.md is a real plan naming load.py and render.py", "PLAN.md should hold the plan (at least 3 lines, naming load.py and render.py)")
def reference(rows):
    totals = {}
    for region, cents in rows:
        totals[region] = totals.get(region, 0) + cents
    lines = ["Sales by region", "---------------"]
    for region, cents in sorted(totals.items(), key=lambda kv: (-kv[1], kv[0])):
        lines.append(f"{region:<10} {cents / 100:>10.2f}")
    lines.append("---------------")
    lines.append(f"{'TOTAL':<10} {sum(totals.values()) / 100:>10.2f}")
    return "\n".join(lines)
rows = [("emea", 50000), ("apac", 125), ("emea", 999), ("amer", 50999), ("apac", 1)]
with tempfile.TemporaryDirectory() as t:
    csvp = os.path.join(t, "s.csv")
    Path(csvp).write_text("region,amount_cents\n" + "".join(f"{r},{c}\n" for r, c in rows))
    code = "import json, sys; sys.path.insert(0, '.'); from load import load_sales; from render import render; r = load_sales(sys.argv[1]); print(json.dumps([list(x) for x in r])); print(json.dumps(render(r)))"
    rc, out, err = sh([sys.executable, "-c", code, csvp])
    parts = out.splitlines()
    ok(rc == 0 and len(parts) == 2 and json.loads(parts[0]) == [list(x) for x in rows], "load.load_sales returns (region, amount_cents) tuples in file order", f"load_sales on an unseen CSV is wrong: {(out + err)[-300:]}")
    ok(rc == 0 and len(parts) == 2 and json.loads(parts[1]) == reference(rows), "render.render produces the original report text", "render(rows) should return exactly the old report text")
    rc, out, err = sh([sys.executable, "report.py", csvp])
    ok(rc == 0 and out.rstrip("\n") == reference(rows), "python3 report.py prints byte-identical output on an unseen CSV", f"report.py output changed: {(out + err)[:300]!r}")
src = text("report.py")
ok("load_sales" in src and "render" in src and "csv.DictReader" not in src, "report.py is now a thin entry point using load and render", "report.py should import load_sales and render instead of parsing the CSV itself")
PYEOF
```

## What you learned

- Plan mode lets Claude explore and propose while the harness blocks every change.
- A saved plan is a reviewable artifact - and a precise brief for the build step.
- Refactors are verified by unchanged behavior: same output before and after.
