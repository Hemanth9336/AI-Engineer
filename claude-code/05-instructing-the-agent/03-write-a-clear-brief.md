---
type: task
title: "Write a clear brief"
minutes: 9
---

## Set up

Set up creates `/root/cc-lab/05-brief`: a small stock module, its test and a CSV of stock levels.

```bash
mkdir -p /root/cc-lab/05-brief/data && cd /root/cc-lab/05-brief
cat > inventory.py <<'EOF'
"""Stock helpers for the warehouse dashboard."""
import csv


def load_stock(path):
    """Read a CSV with columns sku,name,qty and return a list of dicts with qty as an int."""
    with open(path, newline="") as f:
        return [{"sku": r["sku"], "name": r["name"], "qty": int(r["qty"])} for r in csv.DictReader(f)]
EOF
cat > test_inventory.py <<'EOF'
import unittest

from inventory import load_stock


class LoadStockTest(unittest.TestCase):
    def test_load(self):
        rows = load_stock("data/stock.csv")
        self.assertEqual(rows[0], {"sku": "A-100", "name": "Bolts", "qty": 120})


if __name__ == "__main__":
    unittest.main()
EOF
cat > data/stock.csv <<'EOF'
sku,name,qty
A-100,Bolts,120
A-101,Nuts,3
B-200,Washers,0
B-201,Hinges,7
C-300,Brackets,2
C-301,Screws,3
EOF
claude --version
```

## What to build

1. Write `/root/cc-lab/05-brief/brief.md` asking for a `low_stock(rows, threshold=5)` function in `inventory.py`, using exactly these four sections:
   - `## Goal` - name the function, its parameters and what it returns (SKUs with qty below the threshold, lowest qty first, ties by SKU);
   - `## Context` - what Claude needs to know (the existing `load_stock`, how tests run);
   - `## Constraints` - at least two bullet points (for example: standard library only, don't touch `data/`, add a test);
   - `## Done when` - a command to run, in backticks, and the expected result for `data/stock.csv`.
2. Hand the brief to Claude and check the result:

```bash
cd /root/cc-lab/05-brief
claude -p "$(cat brief.md)" --permission-mode acceptEdits --allowedTools "Bash(python3 -m unittest:*)" --max-turns 12
python3 -m unittest -q
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Expected for data/stock.csv with the default threshold: `["B-200", "C-300", "A-101", "C-301"]`.
- `$(cat brief.md)` passes the whole file as the prompt.

</details>

<details><summary>Solution</summary>

```bash
cd /root/cc-lab/05-brief
cat > brief.md <<'EOF'
## Goal
Add `low_stock(rows, threshold=5)` to inventory.py. It returns the SKUs whose qty is below `threshold`, lowest qty first, ties broken by SKU.

## Context
- inventory.py already has `load_stock(path)`, which returns dicts with `sku`, `name` and `qty` (an int).
- Tests live in test_inventory.py and run with `python3 -m unittest -q`.

## Constraints
- Standard library only.
- Don't change `load_stock` or anything in data/.
- Add at least one test for `low_stock` to test_inventory.py.

## Done when
- `python3 -m unittest -q` passes.
- `low_stock(load_stock("data/stock.csv"))` returns `["B-200", "C-300", "A-101", "C-301"]`.
EOF
cd /root/cc-lab/05-brief
claude -p "$(cat brief.md)" --permission-mode acceptEdits --allowedTools "Bash(python3 -m unittest:*)" --max-turns 12
python3 -m unittest -q
```

</details>

## Check your work

```bash
D=/root/cc-lab/05-brief; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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
brief = text("brief.md")
secs = {}
cur = None
for line in brief.splitlines():
    m = re.match(r"^##\s+(.+?)\s*$", line)
    if m:
        cur = m.group(1).strip().lower()
        secs[cur] = []
    elif cur and line.strip():
        secs[cur].append(line.strip())
for name in ("goal", "context", "constraints", "done when"):
    ok(secs.get(name), f"brief.md has a ## {name.capitalize()} section with content", f"brief.md needs a non-empty '## {name.capitalize()}' section")
ok("low_stock" in " ".join(secs.get("goal", [])) and "threshold" in " ".join(secs.get("goal", [])), "the Goal names low_stock and its threshold", "the Goal should name low_stock(rows, threshold=5)")
ok(sum(1 for l in secs.get("constraints", []) if l.startswith(("-", "*"))) >= 2, "Constraints has at least two bullets", "list at least two constraints as bullets")
ok("`" in " ".join(secs.get("done when", [])), "Done when gives a command in backticks", "Done when should include a command in backticks, like `python3 -m unittest -q`")
sys.path.insert(0, os.getcwd())
try:
    import inventory
    f = getattr(inventory, "low_stock", None)
except Exception as e:
    f = None
rows = [{"sku": "Z-9", "name": "z", "qty": 1}, {"sku": "A-1", "name": "a", "qty": 4}, {"sku": "B-2", "name": "b", "qty": 1}, {"sku": "C-3", "name": "c", "qty": 5}, {"sku": "D-4", "name": "d", "qty": 30}]
try:
    got = (f(rows), f(rows, threshold=2), f(rows, 50), f([]))
except Exception as e:
    got = repr(e)
ok(got == (["B-2", "Z-9", "A-1"], ["B-2", "Z-9"], ["B-2", "Z-9", "A-1", "C-3", "D-4"], []), "low_stock is right on unseen rows (default and custom thresholds, ties, empty list)", f"low_stock on unseen rows gave {got}")
rc, out, err = sh([sys.executable, "-m", "unittest", "-q"])
ok(rc == 0 and "low_stock" in text("test_inventory.py"), "test_inventory.py tests low_stock and all tests pass", "add a low_stock test to test_inventory.py and make python3 -m unittest -q pass: " + err[-200:])
ok(text("data/stock.csv").strip() == 'sku,name,qty\nA-100,Bolts,120\nA-101,Nuts,3\nB-200,Washers,0\nB-201,Hinges,7\nC-300,Brackets,2\nC-301,Screws,3', "data/stock.csv is untouched", "data/stock.csv changed - the brief said not to touch data/")
ok(ran(r"##\s*Done when"), "Claude Code received your brief as the prompt", "no session in this folder got the brief - run claude -p \"$(cat brief.md)\" ...")
PYEOF
```

## What you learned

- A brief has four parts: goal, context, constraints, done when.
- "Done when" with a command lets Claude check its own work before it reports back.
- Long briefs live in files: `claude -p "$(cat brief.md)"`.
