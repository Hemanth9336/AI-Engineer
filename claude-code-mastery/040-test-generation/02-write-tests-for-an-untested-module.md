---
type: task
title: "Write tests for an untested module"
minutes: 30
---

## Set up

Set up creates `/root/mastery/040-testgen/pricing/discounts.py` (bulk tiers, rounding, coupons, no tests) and three mutants in `mutants/`, each a copy with one deliberate bug.

```bash
rm -rf /root/mastery/040-testgen && mkdir -p /root/mastery/040-testgen/pricing /root/mastery/040-testgen/tests /root/mastery/040-testgen/mutants && cd /root/mastery/040-testgen
cat > pricing/__init__.py <<'EOF'

EOF
cat > pricing/discounts.py <<'EOF'
COUPONS = {"WELCOME10": 10, "VIP25": 25}


def bulk_discount_pct(qty):
    """Percent off for buying qty units: 10+ -> 5, 50+ -> 10, 100+ -> 15. Negative qty raises ValueError."""
    if qty < 0:
        raise ValueError("qty must be >= 0")
    if qty >= 100:
        return 15
    if qty >= 50:
        return 10
    if qty >= 10:
        return 5
    return 0


def apply_pct(cents, pct):
    """Take pct percent off cents, rounding the discount half up to the nearest cent."""
    return cents - (cents * pct + 50) // 100


def checkout_total(unit_cents, qty, coupon=None):
    """Bulk discount first, then an optional coupon on the discounted total. Unknown coupons raise KeyError."""
    total = apply_pct(unit_cents * qty, bulk_discount_pct(qty))
    if coupon is not None:
        if coupon not in COUPONS:
            raise KeyError(coupon)
        total = apply_pct(total, COUPONS[coupon])
    return total
EOF
cat > tests/__init__.py <<'EOF'

EOF
cat > mutants/m1_fifty_boundary.py <<'EOF'
COUPONS = {"WELCOME10": 10, "VIP25": 25}


def bulk_discount_pct(qty):
    """Percent off for buying qty units: 10+ -> 5, 50+ -> 10, 100+ -> 15. Negative qty raises ValueError."""
    if qty < 0:
        raise ValueError("qty must be >= 0")
    if qty >= 100:
        return 15
    if qty > 50:
        return 10
    if qty >= 10:
        return 5
    return 0


def apply_pct(cents, pct):
    """Take pct percent off cents, rounding the discount half up to the nearest cent."""
    return cents - (cents * pct + 50) // 100


def checkout_total(unit_cents, qty, coupon=None):
    """Bulk discount first, then an optional coupon on the discounted total. Unknown coupons raise KeyError."""
    total = apply_pct(unit_cents * qty, bulk_discount_pct(qty))
    if coupon is not None:
        if coupon not in COUPONS:
            raise KeyError(coupon)
        total = apply_pct(total, COUPONS[coupon])
    return total
EOF
cat > mutants/m2_vip_rate.py <<'EOF'
COUPONS = {"WELCOME10": 10, "VIP25": 20}


def bulk_discount_pct(qty):
    """Percent off for buying qty units: 10+ -> 5, 50+ -> 10, 100+ -> 15. Negative qty raises ValueError."""
    if qty < 0:
        raise ValueError("qty must be >= 0")
    if qty >= 100:
        return 15
    if qty >= 50:
        return 10
    if qty >= 10:
        return 5
    return 0


def apply_pct(cents, pct):
    """Take pct percent off cents, rounding the discount half up to the nearest cent."""
    return cents - (cents * pct + 50) // 100


def checkout_total(unit_cents, qty, coupon=None):
    """Bulk discount first, then an optional coupon on the discounted total. Unknown coupons raise KeyError."""
    total = apply_pct(unit_cents * qty, bulk_discount_pct(qty))
    if coupon is not None:
        if coupon not in COUPONS:
            raise KeyError(coupon)
        total = apply_pct(total, COUPONS[coupon])
    return total
EOF
cat > mutants/m3_coupon_first.py <<'EOF'
COUPONS = {"WELCOME10": 10, "VIP25": 25}


def bulk_discount_pct(qty):
    """Percent off for buying qty units: 10+ -> 5, 50+ -> 10, 100+ -> 15. Negative qty raises ValueError."""
    if qty < 0:
        raise ValueError("qty must be >= 0")
    if qty >= 100:
        return 15
    if qty >= 50:
        return 10
    if qty >= 10:
        return 5
    return 0


def apply_pct(cents, pct):
    """Take pct percent off cents, rounding the discount half up to the nearest cent."""
    return cents - (cents * pct + 50) // 100


def checkout_total(unit_cents, qty, coupon=None):
    """Bulk discount first, then an optional coupon on the discounted total. Unknown coupons raise KeyError."""
    total = unit_cents * qty
    if coupon is not None:
        if coupon not in COUPONS:
            raise KeyError(coupon)
        total = apply_pct(total, COUPONS[coupon])
    total = apply_pct(total, bulk_discount_pct(qty))
    return total
EOF
ls mutants
```

## What to build

1. Run Claude headless, allowing `Read`, `Write`, and `Bash(python3 -m unittest *)`, saving `testgen.json`:
   > Write tests/test_discounts.py for pricing/discounts.py using unittest. Test the contract in the docstrings: every tier boundary, rounding, coupon order, and every error case. Compute expected values by hand, not by running the code. Then run the tests.
2. Write `prove.sh`. It runs the suite on the real code (it must pass), then copies each `mutants/*.py` over `pricing/discounts.py` and runs the suite again.
   - Print `KILLED <file>` when the suite fails and `SURVIVED <file>` when it passes.
   - Exit with the number of survivors.
   - **Always** restore the original, even on error.
3. If a mutant survives, tell Claude which one and have it add a test. Don't edit `pricing/discounts.py`.

The checker also runs your suite against five hidden mutants, and feeds `prove.sh` a mutant that can't be killed to confirm it reports `SURVIVED`.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `trap '...' EXIT` restores the original whatever happens.
- Boundary values (9/10, 49/50, 99/100) kill most comparison mutants; exact rounding cases kill the rest.
- Percentages commute, so applying the coupon first only changes the result through rounding - search for a small input where it does.

</details>

<details><summary>Solution</summary>

```bash
cd /root/mastery/040-testgen
claude -p 'Write tests/test_discounts.py for pricing/discounts.py using unittest. Test the contract in the docstrings: every tier boundary, rounding, coupon order, and every error case. Compute expected values by hand, not by running the code. Then run the tests.' --allowedTools Read Write "Bash(python3 -m unittest *)" --output-format json < /dev/null > testgen.json
jq -r .result testgen.json
cat > prove.sh <<'EOF'
#!/usr/bin/env bash
# prove.sh - the suite must pass on the real code and fail on every mutant. Always restores the original.
set -u
cd "$(dirname "$0")"
orig=$(mktemp)
cp pricing/discounts.py "$orig"
trap 'cp "$orig" pricing/discounts.py; rm -f "$orig"' EXIT
python3 -m unittest -q 2>/dev/null || { echo "FAIL suite does not pass on the original code"; exit 1; }
survivors=0
for m in mutants/*.py; do
  cp "$m" pricing/discounts.py
  if python3 -m unittest -q 2>/dev/null; then echo "SURVIVED $m"; survivors=$((survivors + 1)); else echo "KILLED $m"; fi
done
exit $survivors
EOF
chmod +x prove.sh
./prove.sh; echo "prove exit $?"
```

</details>

## Check your work

```bash
D=/root/mastery/040-testgen; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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
def rtext(b):
    c = b.get("content")
    return c if isinstance(c, str) else " ".join(x.get("text", "") for x in (c or []) if isinstance(x, dict))
def result_for(rows, pred):
    ids = [u["id"] for u in uses(rows) if pred(u)]
    return [b for b in results(rows) if b.get("tool_use_id") in ids]
def run_rows(p):
    env = load(p) or {}
    return transcript(env.get("session_id") or "none")[1]
ORIG = 'COUPONS = {"WELCOME10": 10, "VIP25": 25}\n\n\ndef bulk_discount_pct(qty):\n    """Percent off for buying qty units: 10+ -> 5, 50+ -> 10, 100+ -> 15. Negative qty raises ValueError."""\n    if qty < 0:\n        raise ValueError("qty must be >= 0")\n    if qty >= 100:\n        return 15\n    if qty >= 50:\n        return 10\n    if qty >= 10:\n        return 5\n    return 0\n\n\ndef apply_pct(cents, pct):\n    """Take pct percent off cents, rounding the discount half up to the nearest cent."""\n    return cents - (cents * pct + 50) // 100\n\n\ndef checkout_total(unit_cents, qty, coupon=None):\n    """Bulk discount first, then an optional coupon on the discounted total. Unknown coupons raise KeyError."""\n    total = apply_pct(unit_cents * qty, bulk_discount_pct(qty))\n    if coupon is not None:\n        if coupon not in COUPONS:\n            raise KeyError(coupon)\n        total = apply_pct(total, COUPONS[coupon])\n    return total'
HIDDEN = [('    if qty >= 10:\n', '    if qty > 10:\n'), ('(cents * pct + 50) // 100', '(cents * pct) // 100'), ('            raise KeyError(coupon)\n', '            return total\n'), ('        return 15\n', '        return 10\n'), ('        raise ValueError("qty must be >= 0")\n', '        return 0\n')]

import shutil
ok(text("pricing/discounts.py").rstrip() == ORIG.rstrip(), "pricing/discounts.py is the original code (restored)", "pricing/discounts.py was changed - prove.sh must restore it, and the task is tests only")
src = text("tests/test_discounts.py")
ok(src and "unittest" in src, "tests/test_discounts.py exists", "write tests/test_discounts.py")
n = len(re.findall(r"^\s+def test_", src, re.M))
ok(n >= 5, f"the suite has {n} test methods", f"write at least 5 test methods - found {n}")
ok("mutants" not in src and "skip" not in src, "the tests don't touch the mutants or skip anything", "tests must exercise pricing.discounts directly, without skips")
rc, out, err = sh("python3 -m unittest -q")
ok(rc == 0, "the suite passes on the real code", "the suite fails on the real code:\n" + err[-400:])
def run_against(code):
    with tempfile.TemporaryDirectory() as t:
        shutil.copytree("tests", os.path.join(t, "tests"))
        os.makedirs(os.path.join(t, "pricing"))
        Path(t, "pricing", "__init__.py").write_text("")
        Path(t, "pricing", "discounts.py").write_text(code)
        return sh("python3 -m unittest -q", cwd=t)[0]
alive = [f"{a.strip()} -> {b.strip()}" for a, b in HIDDEN if run_against(ORIG.replace(a, b)) == 0]
ok(not alive, f"the suite kills all {len(HIDDEN)} hidden mutants", f"these hidden mutants survived your suite: {alive}")
given = sorted(glob.glob("mutants/*.py"))
alive2 = [m for m in given if run_against(text(m)) == 0]
ok(given and not alive2, f"the suite kills the {len(given)} given mutants", f"given mutants that survive: {alive2}")
rc, out, err = sh("./prove.sh")
ok(rc == 0 and out.count("KILLED") == len(given) and "SURVIVED" not in out, "prove.sh reports every mutant KILLED and exits 0", f"prove.sh should print KILLED per mutant and exit 0 - rc {rc}, output {out.strip()[-300:]!r}")
ok(text("pricing/discounts.py").rstrip() == ORIG.rstrip(), "prove.sh restored the original afterwards", "prove.sh left a mutant in pricing/discounts.py - restore it on exit")
bad = Path(tempfile.mkdtemp())
for p in ("prove.sh", "pricing/__init__.py", "tests/__init__.py", "tests/test_discounts.py"):
    (bad / p).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(p, bad / p)
(bad / "mutants").mkdir()
(bad / "pricing/discounts.py").write_text(ORIG)
(bad / "mutants/noop.py").write_text(ORIG)
rc, out, err = sh("./prove.sh", cwd=str(bad))
ok(rc != 0 and "SURVIVED" in out, "prove.sh flags a mutant the suite can't kill (non-zero exit)", f"given an equivalent 'mutant', prove.sh should print SURVIVED and exit non-zero - rc {rc}")
rows = run_rows("testgen.json")
wr = [u for u in uses(rows) if u.get("name") in ("Write", "Edit") and (u.get("input") or {}).get("file_path", "").endswith("tests/test_discounts.py")]
ok(wr, "Claude wrote the test file in the headless run", "testgen.json should come from the claude -p run that wrote tests/test_discounts.py")
PYEOF
```

## What you learned

- A suite that passes proves little; a suite that kills mutants proves it can catch bugs.
- Generated tests should pin the documented contract with hand-computed values.
- A restore-always mutation loop is a few lines of bash.
