---
type: task
title: "Find and fix the bug until the test passes"
minutes: 45
---

## Scenario

Support reports customers being charged the wrong shipping: some parcels are cheaper than they should be, and some orders that should ship free don't. The repository has tests that capture the rules - and they're failing. Your job: get them green with Claude Code, without touching the tests, and commit the fix so it's ready for review.

## Set up

Set up creates a git repository in `/root/cc-lab/19-fix` with a `shipping` package whose test suite fails.

```bash
mkdir -p /root/cc-lab/19-fix && cd /root/cc-lab/19-fix
if [ ! -d .git ]; then
git init -q && git symbolic-ref HEAD refs/heads/main
git config user.name "Lab Learner" && git config user.email "learner@example.com"
mkdir -p shipping tests
cat > shipping/__init__.py <<'EOF'

EOF
cat > shipping/rates.py <<'EOF'
RATES = {"domestic": 4.00, "eu": 9.00, "world": 15.00}  # per started kilogram
FREE_DOMESTIC_FROM = 50.00  # domestic orders of 50.00 or more ship free


def shipping_cost(weight_kg, zone, order_total=0.0):
    if weight_kg <= 0:
        raise ValueError("weight must be positive")
    if zone not in RATES:
        raise ValueError(f"unknown zone: {zone}")
    if zone == "domestic" and order_total > FREE_DOMESTIC_FROM:
        return 0.0
    kilos = int(weight_kg)
    return round(kilos * RATES[zone], 2)
EOF
cat > tests/__init__.py <<'EOF'

EOF
cat > tests/test_rates.py <<'EOF'
import unittest

from shipping.rates import shipping_cost


class RatesTest(unittest.TestCase):
    def test_whole_kilos(self):
        self.assertEqual(shipping_cost(2, "eu"), 18.0)

    def test_partial_kilo_rounds_up(self):
        self.assertEqual(shipping_cost(2.3, "eu"), 27.0)

    def test_free_domestic_at_threshold(self):
        self.assertEqual(shipping_cost(1, "domestic", order_total=50.0), 0.0)

    def test_unknown_zone(self):
        with self.assertRaises(ValueError):
            shipping_cost(1, "mars")


if __name__ == "__main__":
    unittest.main()
EOF
cat > .gitignore <<'EOF'
__pycache__/
EOF
cat > README.md <<'EOF'
# shipping

Shipping cost rules. Charged per started kilogram; domestic orders of 50.00 or more ship free.

Tests: `python3 -m unittest discover -s tests -q`
EOF
git add . && git commit -qm "initial: shipping rates"
fi
python3 -m unittest discover -s tests -q || echo 'the suite fails - that is your job'
claude --version
```

## What to build

In `/root/cc-lab/19-fix`:

1. Run the tests and read the failures yourself first.
2. Have Claude find and fix the bugs in `shipping/rates.py`, re-running the tests until they pass - **the tests must not change**.
3. Commit only the fix, with a message starting with `fix:`. Don't push.

```bash
cd /root/cc-lab/19-fix
claude -p "The test suite fails. Run python3 -m unittest discover -s tests -q, find the bugs in shipping/rates.py and fix them without changing the tests, re-running until everything passes. Then commit only the fix with a message starting with 'fix:'." --permission-mode acceptEdits \
  --allowedTools "Bash(python3 -m unittest:*)" "Bash(git status:*)" "Bash(git diff:*)" "Bash(git add:*)" "Bash(git commit:*)" \
  --max-turns 20
python3 -m unittest discover -s tests -q
git log --oneline -2 && git show --stat HEAD
```

Then read the diff: do you understand why each changed line was wrong? The checker also tries cases the tests don't cover.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- The rate is per **started** kilogram: 2.3 kg pays for 3.
- "50.00 or more" means `>=`, not `>`.
- `git diff HEAD~1 -- tests/` should be empty.

</details>

<details><summary>Solution</summary>

```bash
cd /root/cc-lab/19-fix
claude -p "The test suite fails. Run python3 -m unittest discover -s tests -q, find the bugs in shipping/rates.py and fix them without changing the tests, re-running until everything passes. Then commit only the fix with a message starting with 'fix:'." --permission-mode acceptEdits \
  --allowedTools "Bash(python3 -m unittest:*)" "Bash(git status:*)" "Bash(git diff:*)" "Bash(git add:*)" "Bash(git commit:*)" \
  --max-turns 20
python3 -m unittest discover -s tests -q
git log --oneline -2 && git show --stat HEAD
```

</details>

## Check your work

```bash
D=/root/cc-lab/19-fix; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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
rc, out, err = sh([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-q"])
ok(rc == 0, "the test suite passes", "the tests still fail: " + err[-300:])
rc, first, _ = sh("git rev-list --max-parents=0 HEAD")
rc2, diff, _ = sh(f"git diff {first.strip()} -- tests/")
ok(rc == 0 and rc2 == 0 and not diff.strip() and Path("tests/test_rates.py").exists(), "the tests are exactly as they were", "the tests changed since the initial commit - fix the code, not the tests")
cases = [((0.2, "world"), 15.0), ((3.0, "domestic", 49.99), 12.0), ((1, "domestic", 50), 0.0), ((2.0001, "eu"), 27.0), ((1, "eu", 100), 9.0), ((4.5, "domestic", 10), 20.0)]
code = "import json, sys; from shipping.rates import shipping_cost; print(json.dumps([shipping_cost(*a) for a in json.loads(sys.argv[1])]))"
rc, out, err = sh([sys.executable, "-c", code, json.dumps([list(a) for a, _ in cases])])
try:
    got = json.loads(out)
except ValueError:
    got = None
ok(got == [w for _, w in cases], "unseen cases are right too (0.2 kg, 2.0001 kg, 49.99 vs 50.00, free shipping only domestic)", f"for {[a for a, _ in cases]} expected {[w for _, w in cases]} - got {got or err[-200:]}")
rc, bad, err = sh([sys.executable, "-c", "from shipping.rates import shipping_cost\ntry:\n    shipping_cost(0, 'eu')\nexcept ValueError:\n    print('ok')"])
ok(bad.strip() == "ok", "zero weight is still rejected", "shipping_cost(0, 'eu') should still raise ValueError")
rc, subj, _ = sh("git log -1 --format=%s")
rc2, st, _ = sh("git status --porcelain")
ok(subj.strip().lower().startswith("fix") and not st.strip(), f"the fix is committed ({subj.strip()!r}) and the tree is clean", f"commit the fix with a 'fix:' message - last subject {subj.strip()!r}, uncommitted: {st.strip()[:100]}")
rc, files, _ = sh("git show --name-only --format= HEAD")
ok(files.split() == ["shipping/rates.py"], "the commit contains only shipping/rates.py", f"the fix commit should contain only shipping/rates.py - got {files.split()}")
def verified(rows):
    us = uses(rows)
    e = max((i for i, u in enumerate(us) if u.get("name") in ("Edit", "Write")), default=None)
    return e is not None and any(u.get("name") == "Bash" and "unittest" in u["input"].get("command", "") for u in us[e + 1:])
ok([r for r in sessions(os.getcwd()) if verified(r)], "Claude re-ran the tests after its fix", "no session here where Claude ran the tests after editing the code")
PYEOF
```

## What you learned

- Failing tests are the definition of "fixed" - change the code, never the tests.
- Check a fix on cases the tests don't cover before you trust it.
- Commit just the fix, with a message a reviewer understands.
