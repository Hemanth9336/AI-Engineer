---
type: task
title: "Create CLAUDE.md and prove it loads"
minutes: 23
---

## Set up

Set up creates `/root/mastery/010-house`, a tiny payments helper package with a README and one module that already carries an owner header.

```bash
mkdir -p /root/mastery/010-house && cd /root/mastery/010-house
cat > README.md <<'EOF'
# payments-utils

Small helpers used by the payments service.
EOF
cat > rounding.py <<'EOF'
# owner: payments-team


def to_cents(amount):
    return round(amount * 100)
EOF
```

## What to build

Give the project a `CLAUDE.md` and prove both that it loads and that it changes what the agent does.

1. Write `/root/mastery/010-house/CLAUDE.md` with a short **Conventions** section. It must include the rule that every new Python file starts with the line `# owner: payments-team`, plus at least one other checkable rule. (In the console, `/init` can draft the file for you to edit.)
2. **Prove it loads** - a fresh headless run, saved as `loaded.json`:
   > What exact first line must every new Python file in this project start with? Reply with only that line.
3. **Prove it works** - a headless run with edits allowed, saved as `run.json`. The prompt says nothing about owners:
   > Create a module fees.py with a function card_fee(cents) that returns 2.9 percent of cents plus 30, rounded to an int.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- The file name is exactly `CLAUDE.md`, in the folder you run `claude` from (or a parent).

</details>

<details><summary>Solution</summary>

```bash
cd /root/mastery/010-house
cat > CLAUDE.md <<'EOF'
# payments-utils

## Conventions
- Every new Python file starts with the line `# owner: payments-team`
- Money is always integer cents; never use floats for stored amounts
- Run `python3 -m unittest` before finishing
EOF
claude -p "What exact first line must every new Python file in this project start with? Reply with only that line." --output-format json > loaded.json
claude -p "Create a module fees.py with a function card_fee(cents) that returns 2.9 percent of cents plus 30, rounded to an int." --permission-mode acceptEdits --output-format json > run.json
head -1 fees.py
```

</details>

## Check your work

```bash
D=/root/mastery/010-house; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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
c = text("CLAUDE.md")
ok(c and "owner: payments-team" in c and len(c.splitlines()) <= 200, "CLAUDE.md exists with the owner-header rule",
   "create CLAUDE.md in the project root with a rule that new Python files start with '# owner: payments-team'")
ld = load("loaded.json") or {}
ok((ld.get("result") or "").strip().strip("`") == "# owner: payments-team", "a fresh session answered the convention from CLAUDE.md",
   f"loaded.json should answer exactly '# owner: payments-team' - got {ld.get('result')!r}")
run = load("run.json") or {}
ok(run.get("subtype") == "success" and not run.get("permission_denials"), "run.json is a successful edit run", "save the fees.py run as run.json (allow edits)")
lines = text("fees.py").splitlines()
ok(lines[:1] == ["# owner: payments-team"], "fees.py follows the rule without the prompt mentioning it",
   f"fees.py should start with '# owner: payments-team' - first line is {lines[:1]}")
probe = sh("python3 -c 'from fees import card_fee; print(card_fee(1000), card_fee(0))'")[1].split()
ok(probe == ["59", "30"], "card_fee is correct", f"card_fee(1000) should be 59 and card_fee(0) 30 - got {probe}")
PYEOF
```

## What you learned

- CLAUDE.md loads into every session started in the project or below it.
- Write rules a reviewer could check; keep the file short and free of contradictions.
- Prove a rule twice: ask about it, then give a task that should trigger it without mentioning it.
