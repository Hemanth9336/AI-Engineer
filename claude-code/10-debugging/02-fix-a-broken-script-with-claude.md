---
type: task
title: "Fix a broken script with Claude"
minutes: 12
---

## Set up

Set up creates `/root/cc-lab/10-debug` with `csv_total.py`, which is supposed to print the total of the `amount` column of a CSV file. It crashes.

```bash
mkdir -p /root/cc-lab/10-debug/data && cd /root/cc-lab/10-debug
[ -f csv_total.py ] || cat > csv_total.py <<'EOF'
"""Print the total of the amount column. Usage: python3 csv_total.py ORDERS_CSV"""
import sys


def total(path):
    lines = open(path).read().split("\n")[1:]
    s = 0.0
    for line in lines:
        order_id, customer, amount = line.split(",")
        s += float(amount)
    return s


if __name__ == "__main__":
    print(f"total: {total(sys.argv[1]):.2f}")
EOF
cat > data/orders.csv <<'EOF'
order_id,customer,amount
1001,Acme Ltd,250.00
1002,"Smith, J",99.50
1003,Bolt & Co,1200.25
EOF
claude --version
```

## What to build

1. Reproduce the crash and save the traceback to `error.txt`.
2. Give Claude the error, permission to run the script, and a clear definition of "fixed".
3. Run it yourself afterwards - it should print `total: 1549.75`.

```bash
cd /root/cc-lab/10-debug
grep -q Traceback error.txt 2>/dev/null || python3 csv_total.py data/orders.csv 2> error.txt || true
cat error.txt
claude -p "csv_total.py crashes on data/orders.csv with the error below. Find the root cause, fix it properly (customer names can contain commas inside quotes, and files can have blank lines), then run python3 csv_total.py data/orders.csv to confirm.

$(cat error.txt)" --permission-mode acceptEdits --allowedTools "Bash(python3 csv_total.py:*)" --max-turns 12
python3 csv_total.py data/orders.csv
```

Then read the fix. Would it survive a CSV with a blank line in the middle, or another quoted name with a comma?

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- The crash is `ValueError: too many values to unpack` - a quoted name contains a comma.
- Python's `csv` module understands quoting; splitting on commas does not.

</details>

<details><summary>Solution</summary>

```bash
cd /root/cc-lab/10-debug
grep -q Traceback error.txt 2>/dev/null || python3 csv_total.py data/orders.csv 2> error.txt || true
cat error.txt
claude -p "csv_total.py crashes on data/orders.csv with the error below. Find the root cause, fix it properly (customer names can contain commas inside quotes, and files can have blank lines), then run python3 csv_total.py data/orders.csv to confirm.

$(cat error.txt)" --permission-mode acceptEdits --allowedTools "Bash(python3 csv_total.py:*)" --max-turns 12
python3 csv_total.py data/orders.csv
```

</details>

## Check your work

```bash
D=/root/cc-lab/10-debug; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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
err = text("error.txt")
ok("Traceback" in err and "ValueError" in err, "error.txt holds the original traceback", "save the crash to error.txt: python3 csv_total.py data/orders.csv 2> error.txt")
with tempfile.TemporaryDirectory() as t:
    f = os.path.join(t, "o.csv")
    Path(f).write_text('order_id,customer,amount\r\n1,"Lee, Kim",10.10\r\n\r\n2,"North, South and East",5\r\n3,Plain,0.40\r\n\r\n')
    rc, out, errs = sh([sys.executable, "csv_total.py", f])
    ok(rc == 0 and out.strip() == "total: 15.50", "an unseen CSV with quoted commas, blank lines and CRLF gives total: 15.50", f"expected 'total: 15.50' - got {(out + errs).strip()[-200:]!r}")
rc, out, errs = sh([sys.executable, "csv_total.py", "data/orders.csv"])
ok(rc == 0 and out.strip() == "total: 1549.75", "data/orders.csv gives total: 1549.75", f"python3 csv_total.py data/orders.csv should print 'total: 1549.75' - got {(out + errs).strip()[-200:]!r}")
src = text("csv_total.py")
ok("except" not in src or "csv" in src, "the fix handles the data instead of swallowing errors", "don't hide the crash with try/except - parse the CSV properly")
def verified(rows):
    us = uses(rows)
    edit = max((i for i, u in enumerate(us) if u.get("name") in ("Edit", "Write")), default=None)
    return edit is not None and any(u.get("name") == "Bash" and "csv_total.py" in u["input"].get("command", "") for u in us[edit + 1:])
hits = [rows for rows in ran(r"Traceback") if verified(rows)]
ok(hits, "Claude got the traceback, fixed the script, and re-ran it to confirm", "no session here where Claude received the traceback and ran csv_total.py after its fix")
PYEOF
```

## What you learned

- Give Claude the full error, the reproduce command and what correct looks like.
- Allow the reproduce command so Claude can verify its own fix.
- Check the fix addresses the root cause, then pin it with a test.
