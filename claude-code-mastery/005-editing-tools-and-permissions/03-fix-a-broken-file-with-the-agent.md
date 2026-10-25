---
type: task
title: "Fix a broken file with the agent"
minutes: 23
---

## Set up

Set up creates `/root/mastery/005-fix` with `prices.py`, whose `apply_discount` subtracts the percentage instead of applying it, and a failing `test_prices.py`.

```bash
mkdir -p /root/mastery/005-fix && cd /root/mastery/005-fix
cat > prices.py <<'EOF'
"""Order pricing helpers."""


def subtotal(items):
    return sum(i["price"] * i["qty"] for i in items)


def apply_discount(total, pct):
    """Return total reduced by pct percent, rounded to cents."""
    return total - pct
EOF
cat > test_prices.py <<'EOF'
import unittest

from prices import apply_discount, subtotal


class PricesTest(unittest.TestCase):
    def test_subtotal(self):
        self.assertEqual(subtotal([{"price": 5, "qty": 2}, {"price": 1.5, "qty": 4}]), 16)

    def test_discount(self):
        self.assertEqual(apply_discount(200, 10), 180)


if __name__ == "__main__":
    unittest.main()
EOF
```

## What to build

Run the same fix twice from `/root/mastery/005-fix` and keep both envelopes.

1. Run this prompt headless with **no permission flags**, saving `--output-format json` to `denied.json`:

   > Fix apply_discount in prices.py so the tests pass, then run python3 -m unittest to confirm.

   Look at `permission_denials` - the run "succeeded" but changed nothing.
2. Run the same prompt again with the least access that works - edits allowed, and only the unit test command pre-approved - saving the envelope to `fixed.json`.
3. Confirm `python3 -m unittest` passes.

The checker also calls `apply_discount` with values the tests never use.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `--permission-mode acceptEdits` covers the edit; it does not cover running the tests.
- `--allowedTools "Bash(python3 -m unittest *)"` - the space before `*` is part of the rule.

</details>

<details><summary>Solution</summary>

```bash
cd /root/mastery/005-fix
claude -p "Fix apply_discount in prices.py so the tests pass, then run python3 -m unittest to confirm." --output-format json > denied.json
jq .permission_denials denied.json
claude -p "Fix apply_discount in prices.py so the tests pass, then run python3 -m unittest to confirm." --permission-mode acceptEdits --allowedTools "Bash(python3 -m unittest *)" --output-format json > fixed.json
jq '{subtype, permission_denials}' fixed.json
python3 -m unittest -q
```

</details>

## Check your work

```bash
D=/root/mastery/005-fix; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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

den = load("denied.json") or {}
names = {d.get("tool_name") for d in den.get("permission_denials") or []}
ok(den.get("type") == "result" and bool(names & {"Edit", "Write"}),
   "denied.json shows the first run's edit was refused", "save a run with no permission flags as denied.json - its permission_denials should list the refused Edit")
fx = load("fixed.json") or {}
ok(fx.get("subtype") == "success" and not fx.get("permission_denials"),
   "fixed.json is a successful run with nothing denied", f"fixed.json should succeed with an empty permission_denials - got {fx.get('permission_denials')}")
rc, out, err = sh("python3 -m unittest -q")
ok(rc == 0, "the tests pass", "python3 -m unittest still fails: " + err.strip()[-200:])
probe = sh("python3 -c 'from prices import apply_discount as a; print(a(50, 20), a(19.99, 15))'")[1].split()
ok(probe == ["40.0", "16.99"], "apply_discount is right on values the tests never used",
   f"apply_discount(50, 20) should be 40.0 and apply_discount(19.99, 15) 16.99 - got {probe}")
f, rows = transcript(fx.get("session_id", "none"))
seq = [(u.get("name"), u["input"]) for u in uses(rows)]
read_i = next((i for i, (n, a) in enumerate(seq) if n == "Read" and str(a.get("file_path", "")).endswith("prices.py")), None)
edit_i = next((i for i, (n, a) in enumerate(seq) if n in ("Edit", "Write") and str(a.get("file_path", "")).endswith("prices.py")), None)
test_i = next((i for i, (n, a) in enumerate(seq) if n == "Bash" and "unittest" in a.get("command", "")), None)
ok(None not in (read_i, edit_i, test_i) and read_i < edit_i < test_i,
   "the fixing run read the file, edited it, then ran the tests",
   "in fixed.json's transcript the agent should Read prices.py, Edit it, then run python3 -m unittest")
PYEOF
```

## What you learned

- Edit needs a prior Read and an exact string to replace; Write creates or overwrites whole files.
- Headless runs start in Manual mode: anything that would prompt is denied, and permission_denials shows it.
- Grant the narrowest access that works: acceptEdits for edits, an allow rule for the one command.
