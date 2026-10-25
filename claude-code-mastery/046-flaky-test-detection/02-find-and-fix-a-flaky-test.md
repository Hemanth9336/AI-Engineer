---
type: task
title: "Find and fix a flaky test"
minutes: 30
---

## Set up

Set up creates `/root/mastery/046-flaky`: `tags.py` and a two-test suite. Set up runs the suite five times; usually you'll see both pass and fail.

```bash
rm -rf /root/mastery/046-flaky && mkdir -p /root/mastery/046-flaky/tests && cd /root/mastery/046-flaky
cat > tags.py <<'EOF'
def unique_tags(posts):
    """Every tag used across posts, once each, in first-seen order."""
    seen = set()
    for post in posts:
        seen.update(post["tags"])
    return list(seen)


def tag_counts(posts):
    """How many posts use each tag."""
    counts = {}
    for post in posts:
        for tag in set(post["tags"]):
            counts[tag] = counts.get(tag, 0) + 1
    return counts
EOF
cat > tests/__init__.py <<'EOF'

EOF
cat > tests/test_tags.py <<'EOF'
import unittest

from tags import tag_counts, unique_tags

POSTS = [{"tags": ["python", "testing"]}, {"tags": ["testing", "ci"]}, {"tags": ["python"]}]


class TagsTest(unittest.TestCase):
    def test_unique_tags_in_first_seen_order(self):
        self.assertEqual(unique_tags(POSTS), ["python", "testing", "ci"])

    def test_counts(self):
        self.assertEqual(tag_counts(POSTS), {"python": 2, "testing": 2, "ci": 1})
EOF
for i in 1 2 3 4 5; do python3 -m unittest -q 2>/dev/null && echo pass || echo fail; done | sort | uniq -c
```

## What to build

1. Write `hunt.sh [runs]` (default 30).
   - Run the suite once per `PYTHONHASHSEED` from 0 up to `runs - 1`, and write `seed=<n> pass` or `seed=<n> fail` per run to `hunt.log`.
   - Print `<failed>/<runs> runs failed`, and exit 1 if any run failed.
2. Run it on the original code and keep the evidence: `cp hunt.log hunt-before.log`.
3. Run Claude headless, allowing `Read`, `Edit`, `Bash(./hunt.sh)`, and the test command, and disallowing `Edit(tests/**)`. Save `fix.json`:
   > tests/test_tags.py is flaky: hunt-before.log shows it passing for some PYTHONHASHSEED values and failing for others. Find the nondeterminism in tags.py and fix the code so it honors its docstring - do not change the tests. Then run ./hunt.sh to confirm zero failures.
4. Write `FLAKY.md` with `## Symptom`, `## Detection`, `## Root cause`, and `## Fix`.
5. Run `./hunt.sh` again: `0/30 runs failed`.

The checker runs the suite under 50 seeds you never tried, checks first-seen order on a hidden input, and runs your `hunt.sh` against the original flaky code.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Python randomizes str hashing per process; set iteration order follows the hashes.
- `dict.fromkeys(items)` or `seen.setdefault(tag, None)` keeps insertion order and drops duplicates.

</details>

<details><summary>Solution</summary>

```bash
cd /root/mastery/046-flaky
cat > hunt.sh <<'EOF'
#!/usr/bin/env bash
# hunt.sh [runs] - run the suite once per PYTHONHASHSEED value, log pass/fail per seed. Exit 1 if any run failed.
set -u
cd "$(dirname "$0")"
runs=${1:-30}
: > hunt.log
failed=0
for seed in $(seq 0 $((runs - 1))); do
  if PYTHONHASHSEED=$seed python3 -m unittest -q > /dev/null 2>&1; then
    echo "seed=$seed pass" >> hunt.log
  else
    echo "seed=$seed fail" >> hunt.log
    failed=$((failed + 1))
  fi
done
echo "$failed/$runs runs failed"
[ "$failed" -eq 0 ]
EOF
chmod +x hunt.sh
./hunt.sh || true
cp hunt.log hunt-before.log
grep fail hunt-before.log | head -1
claude -p 'tests/test_tags.py is flaky: hunt-before.log shows it passing for some PYTHONHASHSEED values and failing for others. Find the nondeterminism in tags.py and fix the code so it honors its docstring - do not change the tests. Then run ./hunt.sh to confirm zero failures.' --allowedTools Read Edit "Bash(./hunt.sh)" "Bash(python3 -m unittest *)" --disallowedTools "Edit(tests/**)" --output-format json < /dev/null > fix.json
jq -r .result fix.json
cat > FLAKY.md <<'EOF'
# Flaky test: test_unique_tags_in_first_seen_order

## Symptom

`test_unique_tags_in_first_seen_order` passed on some runs and failed on others, with no code change.

## Detection

`./hunt.sh` ran the suite once per `PYTHONHASHSEED` value 0-29; `hunt-before.log` shows a mix of pass and fail, and `PYTHONHASHSEED=<failing seed> python3 -m unittest` reproduces it on demand.

## Root cause

`unique_tags` collected tags in a `set` and returned `list(seen)`. Python randomizes string hashing per process (`PYTHONHASHSEED`), so set iteration order changes from run to run, while the docstring promises first-seen order.

## Fix

Collect tags in a dict (insertion-ordered) instead of a set. The test was not changed: it states the contract. `./hunt.sh` now reports 0/30 failed.
EOF
./hunt.sh
```

</details>

## Check your work

```bash
D=/root/mastery/046-flaky; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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
TEST = 'import unittest\n\nfrom tags import tag_counts, unique_tags\n\nPOSTS = [{"tags": ["python", "testing"]}, {"tags": ["testing", "ci"]}, {"tags": ["python"]}]\n\n\nclass TagsTest(unittest.TestCase):\n    def test_unique_tags_in_first_seen_order(self):\n        self.assertEqual(unique_tags(POSTS), ["python", "testing", "ci"])\n\n    def test_counts(self):\n        self.assertEqual(tag_counts(POSTS), {"python": 2, "testing": 2, "ci": 1})'
BUGGY = 'def unique_tags(posts):\n    """Every tag used across posts, once each, in first-seen order."""\n    seen = set()\n    for post in posts:\n        seen.update(post["tags"])\n    return list(seen)\n\n\ndef tag_counts(posts):\n    """How many posts use each tag."""\n    counts = {}\n    for post in posts:\n        for tag in set(post["tags"]):\n            counts[tag] = counts.get(tag, 0) + 1\n    return counts'

import shutil
ok(text("tests/test_tags.py").rstrip() == TEST.rstrip(), "the test is unchanged - it states the contract", "don't edit tests/test_tags.py: fix the code it tests")
before = [l.split() for l in text("hunt-before.log").splitlines() if l.strip()]
st = [x[1] for x in before if len(x) == 2]
ok(len(before) == 30 and "fail" in st and "pass" in st, f"hunt-before.log proves the flake: {st.count('fail')} of 30 seeds failed, the rest passed",
   "save the hunt from before the fix as hunt-before.log: 30 lines, with both pass and fail")
seeds = [x[0] for x in before]
ok(seeds == [f"seed={i}" for i in range(30)], "each line names its seed, 0 through 29", "log one line per seed as 'seed=<n> pass|fail'")
bad = [s for s in range(100, 150) if sh("python3 -m unittest -q", env={"PYTHONHASHSEED": str(s)})[0] != 0]
ok(not bad, "the suite passes for 50 fresh seeds (100-149)", f"the suite still fails for PYTHONHASHSEED in {bad[:5]}")
probe = [{"tags": ["zeta", "alpha"]}, {"tags": ["mid", "zeta", "beta"]}, {"tags": []}, {"tags": ["alpha", "omega"]}]
code = "import json, sys; from tags import unique_tags, tag_counts; p = json.loads(sys.argv[1]); print(json.dumps([unique_tags(p), tag_counts(p)]))"
want = [["zeta", "alpha", "mid", "beta", "omega"], {"zeta": 2, "alpha": 2, "mid": 1, "beta": 1, "omega": 1}]
def probe_out(seed):
    try:
        return json.loads(sh([sys.executable, "-c", code, json.dumps(probe)], env={"PYTHONHASHSEED": str(seed)})[1])
    except ValueError:
        return None
outs = [probe_out(s) for s in range(8)]
ok(all(o == want for o in outs), "unique_tags returns first-seen order on a hidden input, under every seed", f"unique_tags should return {want[0]} for every PYTHONHASHSEED")
rc, out, err = sh("./hunt.sh 5")
lines = text("hunt.log").splitlines()
ok(rc == 0 and len(lines) == 5 and all(l.endswith(" pass") for l in lines) and "0/5" in out, "./hunt.sh 5 runs 5 seeds, all pass, exit 0", f"./hunt.sh 5 should log 5 passing seeds, print 0/5 runs failed, and exit 0 - rc {rc}, {out.strip()!r}")
with tempfile.TemporaryDirectory() as t:
    shutil.copytree("tests", os.path.join(t, "tests"))
    shutil.copy("hunt.sh", t)
    Path(t, "tags.py").write_text(BUGGY)
    rc, out, err = sh("./hunt.sh 12", cwd=t)
ok(rc == 1 and "/12 runs failed" in out and not out.startswith("0/"), "on the original code hunt.sh catches the flake and exits 1", f"hunt.sh should exit 1 on the flaky code - rc {rc}, {out.strip()!r}")
fl = text("FLAKY.md")
heads = [h for h in ("## Symptom", "## Detection", "## Root cause", "## Fix") if h not in fl]
ok(fl and not heads and "PYTHONHASHSEED" in fl and "set" in fl.lower(), "FLAKY.md documents symptom, detection, root cause (set order, PYTHONHASHSEED), and fix",
   f"FLAKY.md needs the four sections and must name the cause (set ordering under PYTHONHASHSEED) - missing {heads}")
rows = run_rows("fix.json")
ran = result_for(rows, lambda u: u.get("name") == "Bash" and "hunt.sh" in (u.get("input") or {}).get("command", ""))
ok(ran, "Claude ran ./hunt.sh itself to confirm the fix", "let Claude run ./hunt.sh in the fix run (allow Bash(./hunt.sh))")
PYEOF
```

## What you learned

- A flake is proven by rerunning while varying the suspected factor, and reproduced by pinning it.
- Fix the code to honor its contract; retries and loosened assertions hide the bug.
- Give the agent the evidence and the hunt script, and take away the 'edit the test' shortcut.
