---
type: task
title: "Run a multi-tool task and capture the whole run"
minutes: 23
---

## Set up

Set up creates `/root/mastery/002-loop` with `inventory.csv` (stock levels) and `audit.py` (prints the SKUs that need reordering).

```bash
mkdir -p /root/mastery/002-loop && cd /root/mastery/002-loop
cat > inventory.csv <<'EOF'
sku,name,qty,reorder_at
SKU-101,steel bolts,240,100
SKU-104,hex nuts,35,80
SKU-150,washers,500,200
SKU-221,cable ties,12,50
SKU-307,wood screws,90,90
EOF
cat > audit.py <<'EOF'
"""Print every SKU whose stock is below its reorder level, one per line."""
import csv

with open("inventory.csv", newline="") as f:
    for row in csv.DictReader(f):
        if int(row["qty"]) < int(row["reorder_at"]):
            print(row["sku"])
EOF
```

## What to build

In `/root/mastery/002-loop`, run one headless task that needs three different tools, and keep both halves of the record.

1. Run this prompt with `claude -p`, pre-approving just the two tools that change something - `--allowedTools "Bash(python3 audit.py)" Write` - and saving the envelope with `--output-format json > run.json`:

   > Read inventory.csv to learn its columns, then run python3 audit.py, then write the SKUs it prints to restock.txt, one per line.

2. Read `subtype`, `num_turns`, and `total_cost_usd` from `run.json` with `jq`.
3. Use the envelope's `session_id` to find the run's transcript under `~/.claude/projects/` and copy it to `transcript.jsonl` in the folder.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `jq -r .session_id run.json` prints the id without quotes.
- The transcript is `~/.claude/projects/<folder>/<session_id>.jsonl` - a glob over the folder part is fine.

</details>

<details><summary>Solution</summary>

```bash
cd /root/mastery/002-loop
claude -p "Read inventory.csv to learn its columns, then run python3 audit.py, then write the SKUs it prints to restock.txt, one per line." --allowedTools "Bash(python3 audit.py)" Write --output-format json > run.json
jq '{subtype, num_turns, total_cost_usd}' run.json
sid=$(jq -r .session_id run.json)
cp ~/.claude/projects/*/"$sid".jsonl transcript.jsonl
cat restock.txt
```

</details>

## Check your work

```bash
D=/root/mastery/002-loop; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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
def transcript(sid):
    for f in glob.glob(os.path.expanduser(f"~/.claude/projects/*/{sid}.jsonl")):
        rows = []
        for line in open(f, errors="replace"):
            try:
                rows.append(json.loads(line))
            except ValueError:
                pass
        return f, rows
    return None, []

run = load("run.json") or {}
ok(run.get("type") == "result" and run.get("subtype") == "success" and run.get("is_error") is False,
   "run.json is a successful JSON envelope", "save the envelope: claude -p \"...\" --output-format json > run.json")
ok((run.get("num_turns") or 0) >= 3, f"the loop went around {run.get('num_turns')} times",
   f"the run should take several turns (read, run, write) - num_turns is {run.get('num_turns')}")
import csv
want = [r["sku"] for r in csv.DictReader(open("inventory.csv")) if int(r["qty"]) < int(r["reorder_at"])]
got = [l.strip() for l in text("restock.txt").splitlines() if l.strip()]
ok(got == want, f"restock.txt lists the {len(want)} low-stock SKUs", f"restock.txt should list {want}, one per line - got {got}")
f, rows = transcript(run.get("session_id", "none"))
names = {u.get("name") for u in uses(rows)}
ok({"Read", "Bash", "Write"} <= names, "the transcript shows Read, Bash, and Write tool calls",
   f"the run's transcript should show Read, Bash and Write calls - found {sorted(names) or 'no transcript for this session_id'}")
copy = [r for r in (json.loads(l) for l in text("transcript.jsonl").splitlines() if l.strip().startswith("{"))]
ok(bool(copy) and f and text("transcript.jsonl") == text(f),
   "transcript.jsonl is the full transcript of that run", "copy ~/.claude/projects/*/<session_id>.jsonl to transcript.jsonl")
PYEOF
```

## What you learned

- One prompt becomes a loop: each tool call is a turn, and the run ends when the model answers without a tool.
- `--output-format json` gives the envelope - result, cost, turns, denials - but not the steps.
- The `session_id` links the envelope to the transcript, which holds every tool call and result.
