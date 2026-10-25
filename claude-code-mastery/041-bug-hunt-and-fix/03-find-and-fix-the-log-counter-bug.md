---
type: task
title: "Find and fix the log counter bug"
minutes: 23
---

## Set up

Set up creates a git repo at `/root/mastery/041-bughunt`: `logcount.py` (counts log lines per level), a sample `app.log`, and one passing test. The counts it prints for `app.log` are wrong.

```bash
rm -rf /root/mastery/041-bughunt && mkdir -p /root/mastery/041-bughunt/tests && cd /root/mastery/041-bughunt
git init -q -b main && git config user.name 'Lab Learner' && git config user.email learner@lab.invalid
cat > logcount.py <<'EOF'
"""logcount.py <file> - count log lines per level, most frequent first.

Lines look like '<timestamp> <LEVEL> <message>'. Lines that don't match that shape are ignored.
"""
import sys
from collections import Counter

LEVELS = ("ERROR", "WARN", "INFO", "DEBUG")


def count_levels(lines):
    counts = Counter()
    for line in lines:
        for level in LEVELS:
            if level in line:
                counts[level] += 1
    return counts


def main(path):
    with open(path) as f:
        counts = count_levels(f)
    for level, n in counts.most_common():
        print(f"{level} {n}")


if __name__ == "__main__":
    main(sys.argv[1])
EOF
cat > app.log <<'EOF'
2026-10-25T10:00:01Z INFO service started
2026-10-25T10:00:02Z WARN retrying payment after ERROR from gateway
2026-10-25T10:00:03Z ERROR payment failed: gateway timeout
2026-10-25T10:00:04Z INFO user DEBUGGER attached
2026-10-25T10:00:05Z DEBUG cache miss for key 42
2026-10-25T10:00:06Z INFO healthcheck ok
2026-10-25T10:00:07Z WARN slow query: 812 ms
2026-10-25T10:00:08Z ERROR payment failed: card declined
2026-10-25T10:00:09Z INFO request finished after WARN threshold
EOF
cat > tests/__init__.py <<'EOF'

EOF
cat > tests/test_logcount.py <<'EOF'
import unittest

from logcount import count_levels


class CountTest(unittest.TestCase):
    def test_simple_lines(self):
        lines = ["2026-10-25T10:00:01Z INFO up", "2026-10-25T10:00:02Z ERROR down"]
        self.assertEqual(dict(count_levels(lines)), {"INFO": 1, "ERROR": 1})
EOF
python3 -m unittest -q && git add -A && git commit -qm 'logcount' && python3 logcount.py app.log
```

## What to build

1. **Reproduce.** Run `python3 logcount.py app.log` and count the levels independently (for example `awk '{print $2}' app.log | sort | uniq -c`). Write `BUG.md` with `## Reproduce`, `## Expected`, `## Actual`, and `## Root cause` (fill in the root cause after step 3).
2. **Safety net.** Check the tree is clean, then `git switch -c fix/level-count`.
3. **Locate and test first.** Run Claude headless with `Read`, `Write`, and `Bash(python3 -m unittest *)`, saving `locate.json`:
   > logcount.py miscounts levels: python3 logcount.py app.log prints WARN 3, ERROR 3, DEBUG 2, but the level field says WARN 2, ERROR 2, DEBUG 1. Find the cause, then write tests/test_level_field.py with a regression test that fails because of it, and run the tests to show the failure. Do not change logcount.py yet.

   Confirm the suite fails, then commit `BUG.md` and the test as `test: reproduce level miscount`.
4. **Fix.** Run Claude headless with `Read`, `Edit`, and the test command, **disallowing `Edit(tests/**)`**, saving `fix.json`:
   > Fix logcount.py so that every test passes. Make the smallest change, and do not modify the tests.

   Re-run the reproduction, then commit `logcount.py` alone as `fix: count the level field only`.

The checker checks out your first commit and expects red, expects green at HEAD, and tries edge cases from the docstring.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- The docstring says malformed lines are ignored - a fix that crashes on a blank line is not done.
- `git archive <commit>` lets you test an old commit without switching branches.
- Use `Edit(tests/**)`, not `Write(...)`: Write rules never match.

</details>

<details><summary>Solution</summary>

```bash
cd /root/mastery/041-bughunt
git status --short            # clean tree before the agent starts
git switch -c fix/level-count
python3 logcount.py app.log
awk '{print $2}' app.log | sort | uniq -c
cat > BUG.md <<'EOF'
# Bug: logcount.py miscounts levels

## Reproduce

`python3 logcount.py app.log`

## Expected

INFO 4, WARN 2, ERROR 2, DEBUG 1 (counted from the level field: `awk '{print $2}' app.log | sort | uniq -c`).

## Actual

INFO 4, WARN 3, ERROR 3, DEBUG 2.

## Root cause

`count_levels` checks `if level in line`, so a level word anywhere in the message ("after ERROR from gateway", "DEBUGGER") is counted too. Only the second field is the level.
EOF
claude -p 'logcount.py miscounts levels: python3 logcount.py app.log prints WARN 3, ERROR 3, DEBUG 2, but the level field says WARN 2, ERROR 2, DEBUG 1. Find the cause, then write tests/test_level_field.py with a regression test that fails because of it, and run the tests to show the failure. Do not change logcount.py yet.' --allowedTools Read Write "Bash(python3 -m unittest *)" --output-format json < /dev/null > locate.json
jq -r .result locate.json
python3 -m unittest -q || echo "the suite fails, as it should before the fix"
git add BUG.md tests/test_level_field.py && git commit -qm 'test: reproduce level miscount'
claude -p 'Fix logcount.py so that every test passes. Make the smallest change, and do not modify the tests.' --allowedTools Read Edit "Bash(python3 -m unittest *)" --disallowedTools "Edit(tests/**)" --output-format json < /dev/null > fix.json
jq -r .result fix.json
python3 -m unittest -q && python3 logcount.py app.log
git add logcount.py && git commit -qm 'fix: count the level field only'
git log --oneline main..HEAD
```

</details>

## Check your work

```bash
D=/root/mastery/041-bughunt; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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
BUGGY = '"""logcount.py <file> - count log lines per level, most frequent first.\n\nLines look like \'<timestamp> <LEVEL> <message>\'. Lines that don\'t match that shape are ignored.\n"""\nimport sys\nfrom collections import Counter\n\nLEVELS = ("ERROR", "WARN", "INFO", "DEBUG")\n\n\ndef count_levels(lines):\n    counts = Counter()\n    for line in lines:\n        for level in LEVELS:\n            if level in line:\n                counts[level] += 1\n    return counts\n\n\ndef main(path):\n    with open(path) as f:\n        counts = count_levels(f)\n    for level, n in counts.most_common():\n        print(f"{level} {n}")\n\n\nif __name__ == "__main__":\n    main(sys.argv[1])'

import io, shutil, tarfile
rc, br, _ = sh("git rev-parse --abbrev-ref HEAD")
ok(br.strip() == "fix/level-count", "you are on the fix/level-count branch", f"work on a branch named fix/level-count - HEAD is {br.strip()!r}")
rc, mfile, _ = sh("git show main:logcount.py")
ok(mfile.rstrip() == BUGGY.rstrip(), "main is untouched", "main should still hold the original logcount.py - the fix belongs on the branch")
rc, revs, _ = sh("git rev-list --reverse main..HEAD")
revs = revs.split()
ok(len(revs) >= 2, f"the branch has {len(revs)} commits on top of main", "make two commits: the failing test, then the fix")
def files(rev):
    return set(sh(f"git show --name-only --format= {rev}")[1].split())
def tests_at(rev):
    with tempfile.TemporaryDirectory() as t:
        data = subprocess.run(["git", "archive", rev], capture_output=True).stdout
        tarfile.open(fileobj=io.BytesIO(data)).extractall(t)
        return sh("python3 -m unittest -q", cwd=t)[0]
if len(revs) >= 2:
    f1, fl = files(revs[0]), files(revs[-1])
    ok(f1 and all(f.startswith("tests/") or f == "BUG.md" for f in f1), "the first commit adds only tests (and BUG.md)", f"the first commit should touch only tests/ and BUG.md - it touched {sorted(f1)}")
    ok(tests_at(revs[0]) != 0, "at the first commit the suite fails - the regression test reproduces the bug", "the regression test should fail before the fix: check out the first commit and it must be red")
    ok("logcount.py" in fl and not any(f.startswith("tests/") for f in fl), "the last commit changes logcount.py and no tests", f"the fix commit should change logcount.py only - it touched {sorted(fl)}")
rc, out, err = sh("python3 -m unittest -q")
ok(rc == 0, "the whole suite passes at HEAD", "tests fail at HEAD:\n" + err[-300:])
reg = text("tests/test_level_field.py")
ok("count_levels" in reg and re.search(r"def test_", reg), "tests/test_level_field.py holds the regression test", "write the regression test in tests/test_level_field.py")
rc, out, err = sh("python3 logcount.py app.log")
got = dict((l.split()[0], int(l.split()[1])) for l in out.splitlines() if len(l.split()) == 2)
ok(got == {"INFO": 4, "WARN": 2, "ERROR": 2, "DEBUG": 1}, "the reproduction now prints the expected counts", f"python3 logcount.py app.log should give INFO 4, WARN 2, ERROR 2, DEBUG 1 - got {got or err[-200:]}")
probe = ["2026-10-25T10:00:01Z TRACE something ERROR", "", "garbage", "2026-10-25T10:00:02Z ERROR a", "2026-10-25T10:00:03Z info lower", "x WARN y WARN"]
rc, out, err = sh([sys.executable, "-c", "import json, sys; from logcount import count_levels; print(json.dumps(dict(count_levels(json.loads(sys.argv[1])))))", json.dumps(probe)])
ok(rc == 0 and out.strip() and json.loads(out) == {"ERROR": 1, "WARN": 1}, "edge cases: unknown levels, blank and malformed lines are ignored", f"count_levels on edge cases should give {{'ERROR': 1, 'WARN': 1}} - got {out.strip() or err.strip()[-200:]}")
bug = text("BUG.md")
heads = [h for h in ("## Reproduce", "## Expected", "## Actual", "## Root cause") if h not in bug]
ok(bug and not heads, "BUG.md has Reproduce, Expected, Actual, and Root cause", f"BUG.md is missing {heads}")
fx = run_rows("fix.json")
te = result_for(fx, lambda u: u.get("name") in ("Edit", "Write", "MultiEdit") and "/tests/" in (u.get("input") or {}).get("file_path", ""))
ed = result_for(fx, lambda u: u.get("name") in ("Edit", "MultiEdit") and (u.get("input") or {}).get("file_path", "").endswith("logcount.py"))
ok(fx and ed and all(b.get("is_error") for b in te), "the fix run edited logcount.py and never changed a test", "fix.json should come from a claude -p run that edits logcount.py with tests/ disallowed")
lc = run_rows("locate.json")
ok(any(u.get("name") == "Write" and (u.get("input") or {}).get("file_path", "").endswith("tests/test_level_field.py") for u in uses(lc)),
   "the locate run wrote the regression test", "locate.json should come from the run that wrote tests/test_level_field.py")
PYEOF
```

## What you learned

- Reproduce with an independent expected value before touching code.
- Commit the failing regression test first, then the smallest fix.
- Take the 'edit the test' shortcut away from the fix run with a disallowed Edit rule.
