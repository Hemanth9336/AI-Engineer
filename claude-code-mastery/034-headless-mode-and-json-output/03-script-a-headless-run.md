---
type: task
title: "Script a headless run"
minutes: 23
---

## Set up

Set up creates `/root/mastery/034-headless/src/` with `clean.py`, `buggy.py` (divides by zero on an empty list), and `huge.py` (40 functions - too much for a 4-turn review).

```bash
rm -rf /root/mastery/034-headless && mkdir -p /root/mastery/034-headless/src && cd /root/mastery/034-headless
cat > src/clean.py <<'EOF'
def add(a, b):
    return a + b
EOF
cat > src/buggy.py <<'EOF'
def average(items):
    total = sum(items)
    return total / len(items)
EOF
cat > src/huge.py <<'EOF'
def f0(x):
    return x + 0
def f1(x):
    return x + 1
def f2(x):
    return x + 2
def f3(x):
    return x + 3
def f4(x):
    return x + 4
def f5(x):
    return x + 5
def f6(x):
    return x + 6
def f7(x):
    return x + 7
def f8(x):
    return x + 8
def f9(x):
    return x + 9
def f10(x):
    return x + 10
def f11(x):
    return x + 11
def f12(x):
    return x + 12
def f13(x):
    return x + 13
def f14(x):
    return x + 14
def f15(x):
    return x + 15
def f16(x):
    return x + 16
def f17(x):
    return x + 17
def f18(x):
    return x + 18
def f19(x):
    return x + 19
def f20(x):
    return x + 20
def f21(x):
    return x + 21
def f22(x):
    return x + 22
def f23(x):
    return x + 23
def f24(x):
    return x + 24
def f25(x):
    return x + 25
def f26(x):
    return x + 26
def f27(x):
    return x + 27
def f28(x):
    return x + 28
def f29(x):
    return x + 29
def f30(x):
    return x + 30
def f31(x):
    return x + 31
def f32(x):
    return x + 32
def f33(x):
    return x + 33
def f34(x):
    return x + 34
def f35(x):
    return x + 35
def f36(x):
    return x + 36
def f37(x):
    return x + 37
def f38(x):
    return x + 38
def f39(x):
    return x + 39
EOF
```

## What to build

Write `/root/mastery/034-headless/review.sh <file>`, a review step a CI job can trust.

1. Exit `2` with a usage message if the argument is missing or the file does not exist.
2. Run, with only the Read tool, at most 4 turns, and JSON output:
   > Review <file> for bugs. Reply with one line per issue as 'line N: problem', or exactly NO ISSUES.
3. If claude produced no JSON, or `subtype` is not `success`, or `is_error` is true: print `review failed: <subtype>` to stderr, append `FAIL <file> <subtype> session=<id>` to `runs.log`, exit `1`.
4. Otherwise print the result. If it is exactly `NO ISSUES`, append `OK <file> turns=<n> cost=<usd> session=<id>` and exit `0`; else append the same with `ISSUES` and exit `3`.

The checker runs your script five times - no argument, a missing file, and the three source files - and checks every exit code and log line.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `claude ... > out.json || true` keeps `set -e` from stopping before you can read the subtype.
- `jq -r '.subtype // "no-json"'` handles a missing field.

</details>

<details><summary>Solution</summary>

```bash
cd /root/mastery/034-headless
cat > review.sh <<'EOF'
#!/usr/bin/env bash
# review.sh <file> - headless bug review. Exit: 0 no issues, 1 agent run failed, 2 bad usage, 3 issues found.
set -euo pipefail
cd "$(dirname "$0")"
if [ $# -ne 1 ] || [ ! -f "$1" ]; then
  echo "usage: review.sh <existing file>" >&2
  exit 2
fi
f=$1
out=$(mktemp)
claude -p "Review $f for bugs. Reply with one line per issue as 'line N: problem', or exactly NO ISSUES." \
  --allowedTools Read --max-turns 4 --output-format json < /dev/null > "$out" 2>/dev/null || true
subtype=$(jq -r '.subtype // "no-json"' "$out" 2>/dev/null || echo no-json)
sid=$(jq -r '.session_id // "-"' "$out" 2>/dev/null || echo -)
if [ "$subtype" != success ] || [ "$(jq -r .is_error "$out")" != false ]; then
  echo "FAIL $f $subtype session=$sid" >> runs.log
  echo "review failed: $subtype" >&2
  exit 1
fi
result=$(jq -r .result "$out")
turns=$(jq -r .num_turns "$out")
cost=$(jq -r .total_cost_usd "$out")
echo "$result"
if [ "$result" = "NO ISSUES" ]; then
  echo "OK $f turns=$turns cost=$cost session=$sid" >> runs.log
  exit 0
fi
echo "ISSUES $f turns=$turns cost=$cost session=$sid" >> runs.log
exit 3
EOF
chmod +x review.sh
./review.sh src/buggy.py || echo "exit $?"
cat runs.log
```

</details>

## Check your work

```bash
D=/root/mastery/034-headless; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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

ok(os.access("review.sh", os.X_OK), "review.sh is executable", "write an executable review.sh in the project folder")
def run(*args):
    return sh(["./review.sh", *args], timeout=240)
rc, out, err = run()
ok(rc == 2, "no argument -> exit 2", f"./review.sh with no argument should exit 2 - got {rc}")
rc, out, err = run("src/nope.py")
ok(rc == 2, "missing file -> exit 2", f"./review.sh src/nope.py should exit 2 - got {rc}")
before = len(text("runs.log").splitlines())
rc, out, err = run("src/clean.py")
ok(rc == 0 and out.strip() == "NO ISSUES", "clean file -> exit 0 and prints NO ISSUES", f"src/clean.py should exit 0 printing NO ISSUES - got exit {rc} {out.strip()[:80]!r} {err.strip()[:120]}")
rc, out, err = run("src/buggy.py")
ok(rc == 3 and "line 3" in out, "buggy file -> exit 3 and prints the issue", f"src/buggy.py should exit 3 printing the 'line 3: ...' issue - got exit {rc} {out.strip()[:80]!r}")
rc, out, err = run("src/huge.py")
ok(rc == 1 and "error_max_turns" in err, "a run that hits --max-turns -> exit 1 with the subtype on stderr", f"src/huge.py runs past --max-turns 4: expect exit 1 and 'error_max_turns' on stderr - got exit {rc} {err.strip()[:120]!r}")
new = text("runs.log").splitlines()[before:]
kinds = [l.split()[0] for l in new if l.split()]
ok(kinds == ["OK", "ISSUES", "FAIL"] and all("session=" in l for l in new), "runs.log got OK, ISSUES, and FAIL lines with session ids",
   f"each run should append one line (OK / ISSUES / FAIL, file, ..., session=<id>) to runs.log - new lines: {new}")
sids = [l.split("session=")[1].split()[0] for l in new if "session=" in l]
ok(sids and all(transcript(s)[0] for s in sids), "every logged session id has a transcript you can open", "log the real session_id from the run object")
PYEOF
```

## What you learned

- The json run object carries subtype, is_error, result, session_id, turns, cost, and permission_denials.
- claude exits 1 on max-turns or budget limits and may print no JSON at all on setup errors.
- Give scripts their own exit-code contract and log one line per run with its session id.
