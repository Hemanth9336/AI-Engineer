---
type: task
title: "Let Claude write a script"
minutes: 7
---

## Scenario

Headless mode can do real work, not just answer. `--permission-mode acceptEdits` lets Claude create and edit files in the folder for this one run - and nothing else: it still can't run commands you haven't allowed.

## Set up

Same folder as the previous task: `/root/cc-lab/04-headless`.

```bash
mkdir -p /root/cc-lab/04-headless && cd /root/cc-lab/04-headless
cat > server.log <<'EOF'
2026-10-20T09:00:01 INFO  api started on :8080
2026-10-20T09:00:07 INFO  GET /health 200
2026-10-20T09:01:13 ERROR E101 payment gateway timeout
2026-10-20T09:01:15 WARN  retrying payment request
2026-10-20T09:02:40 ERROR E204 invalid card number
2026-10-20T09:03:02 INFO  GET /orders 200
2026-10-20T09:04:55 ERROR E101 payment gateway timeout
2026-10-20T09:05:10 WARN  slow query on orders (2300 ms)
2026-10-20T09:06:31 ERROR E330 inventory service unreachable
2026-10-20T09:07:00 INFO  GET /health 200
EOF
claude --version
```

## What to build

1. In `/root/cc-lab/04-headless`, have Claude write a log-statistics script from a precise spec:

```bash
claude -p "Write a bash script named logstats.sh. Usage: bash logstats.sh FILE. It prints one line, 'lines=N errors=M warnings=K', where N is the number of lines in FILE, M the lines containing ERROR and K the lines containing WARN. With no argument it prints 'usage: logstats.sh FILE' to stderr and exits 2; if FILE does not exist it prints 'no such file: FILE' to stderr and exits 1." --permission-mode acceptEdits
```

2. Try it yourself - including the error cases:

```bash
bash logstats.sh server.log
bash logstats.sh; echo "exit $?"
bash logstats.sh nope.log; echo "exit $?"
```

If something is off, run `claude -p` again with a specific correction ("the warnings count includes...").

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- A precise spec - exact output format, exit codes - gets you a checkable script.
- Expected for server.log: lines=10 errors=4 warnings=2.

</details>

<details><summary>Solution</summary>

```bash
cd /root/cc-lab/04-headless
claude -p "Write a bash script named logstats.sh. Usage: bash logstats.sh FILE. It prints one line, 'lines=N errors=M warnings=K', where N is the number of lines in FILE, M the lines containing ERROR and K the lines containing WARN. With no argument it prints 'usage: logstats.sh FILE' to stderr and exits 2; if FILE does not exist it prints 'no such file: FILE' to stderr and exits 1." --permission-mode acceptEdits --max-turns 6
bash logstats.sh server.log
```

</details>

## Check your work

```bash
D=/root/cc-lab/04-headless; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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
ok(Path("logstats.sh").exists(), "logstats.sh exists", "no logstats.sh in /root/cc-lab/04-headless - run the claude -p command")
with tempfile.TemporaryDirectory() as t:
    f = os.path.join(t, "app.log")
    Path(f).write_text("ERROR a\nWARN b\nINFO c\nERROR d\nERROR e\nINFO f\nWARN g\n")
    rc, out, err = sh(["bash", "logstats.sh", f])
    ok(rc == 0 and out.strip() == "lines=7 errors=3 warnings=2", "a 7-line log with 3 ERROR and 2 WARN lines gives lines=7 errors=3 warnings=2", f"expected 'lines=7 errors=3 warnings=2' - got {(out + err).strip()[:200]!r}")
    Path(f).write_text("all quiet\n")
    rc, out, err = sh(["bash", "logstats.sh", f])
    ok(rc == 0 and out.strip() == "lines=1 errors=0 warnings=0", "a log with no errors gives errors=0 warnings=0", f"expected 'lines=1 errors=0 warnings=0' - got {(out + err).strip()[:200]!r}")
rc, out, err = sh(["bash", "logstats.sh"])
ok(rc == 2 and "usage: logstats.sh FILE" in err, "no argument: usage on stderr, exit 2", f"no argument should print usage to stderr and exit 2 - got exit {rc}, stderr {err.strip()[:100]!r}")
rc, out, err = sh(["bash", "logstats.sh", "missing-file.log"])
ok(rc == 1 and "no such file: missing-file.log" in err, "missing file: message on stderr, exit 1", f"a missing file should print 'no such file: missing-file.log' to stderr and exit 1 - got exit {rc}")
hits = [rows for rows in sessions(os.getcwd()) if any(u.get("name") in ("Write", "Edit") and "logstats.sh" in json.dumps(u.get("input")) for u in uses(rows))]
ok(hits, "Claude Code wrote logstats.sh in a session here", "no session in this folder where Claude wrote logstats.sh - let claude -p write it")
PYEOF
```

## What you learned

- `--permission-mode acceptEdits` lets a headless run write files and nothing more.
- A spec with exact output and exit codes is one you (and a checker) can verify.
- Always run what the agent wrote, including the failure paths.
