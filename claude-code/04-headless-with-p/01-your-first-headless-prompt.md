---
type: task
title: "Your first headless prompt"
minutes: 7
---

## Scenario

`claude -p "prompt"` (print mode) runs one task and prints the answer to standard output, then exits. No console, no back-and-forth - which makes Claude Code a Unix tool: redirect it, pipe it, check its exit code.

## Set up

Set up creates `/root/cc-lab/04-headless` with a small `server.log` you'll use in the next tasks.

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

In `/root/cc-lab/04-headless`:

1. Ask a one-word question and save the answer:

```bash
claude -p "Which planet is known as the Red Planet? Answer with one word." > answer.txt
echo "exit code: $?"
```

2. Ask for an exact reply - useful when a script needs to compare the output:

```bash
claude -p "Reply with exactly the word READY and nothing else." > ready.txt
```

3. `cat` both files. Notice there's no extra chatter: only the answer goes to stdout.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Quote the whole prompt.
- `$?` is the exit code of the last command: 0 means success.

</details>

<details><summary>Solution</summary>

```bash
cd /root/cc-lab/04-headless
claude -p "Which planet is known as the Red Planet? Answer with one word." > answer.txt
echo "exit code: $?"
claude -p "Reply with exactly the word READY and nothing else." > ready.txt
cat answer.txt ready.txt
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
a, r = text("answer.txt"), text("ready.txt")
ok("mars" in a.lower(), "answer.txt holds the answer (Mars)", "answer.txt should hold Claude's one-word answer - run the first claude -p command")
ok(re.sub(r"[^A-Za-z]", "", r).upper() == "READY", "ready.txt is exactly READY", f"ready.txt should be just READY - got {r.strip()[:80]!r}")
ok(ran(r"Red Planet"), "Claude Code answered the Red Planet prompt in this folder", "no claude session in this folder asked about the Red Planet")
ok(ran(r"exactly the word READY"), "Claude Code answered the READY prompt in this folder", "no claude session in this folder asked for READY")
PYEOF
```

## What you learned

- `claude -p` runs once and prints only the answer, so `>` saves it like any command.
- Asking for an exact format makes the output usable by scripts.
- Every `-p` run is still a saved session you can inspect later.
