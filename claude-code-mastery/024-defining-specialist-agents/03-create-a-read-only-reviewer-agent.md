---
type: task
title: "Create a read-only reviewer agent"
minutes: 23
---

## Set up

Set up creates `/root/mastery/024-reviewer/src/auth.py` with an MD5 password hash and a SQL query built by string concatenation.

```bash
rm -rf /root/mastery/024-reviewer && mkdir -p /root/mastery/024-reviewer/src && cd /root/mastery/024-reviewer
cat > src/auth.py <<'EOF'
import hashlib
import sqlite3


def hash_password(pw):
    return hashlib.md5(pw.encode()).hexdigest()


def find_user(db, name):
    return db.execute("SELECT * FROM users WHERE name = '" + name + "'").fetchone()
EOF
```

## What to build

Create a project specialist that reviews security and **cannot** change code.

1. Write `/root/mastery/024-reviewer/.claude/agents/security-reviewer.md`:
   - `name: security-reviewer` and a description that says when to use it;
   - read-only tools only;
   - a system prompt with a checklist and the output format `FINDING: <file>:<line> - <issue>`, or exactly `NO FINDINGS`.
2. Get it invoked: run this headless and save the envelope as `review.json`:
   > Use the security-reviewer agent to review src/auth.py and reply with its findings unchanged.

The checker then runs your agent as the main agent with edits allowed and asks it to fix the file - the file must not change.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `tools: Read, Grep, Glob` is an allowlist enforced by Claude Code.

</details>

<details><summary>Solution</summary>

```bash
cd /root/mastery/024-reviewer
mkdir -p .claude/agents
cat > .claude/agents/security-reviewer.md <<'EOF'
---
name: security-reviewer
description: Reviews code for security issues. Use proactively after changes to authentication, payments, or SQL.
tools: Read, Grep, Glob
model: sonnet
---

You are a security reviewer. You never modify files.

Check for: hard-coded secrets, SQL built by string concatenation, weak password hashing, missing authorization checks.
Report each issue on its own line as:
FINDING: <file>:<line> - <issue>
If there are none, reply exactly: NO FINDINGS
EOF
claude -p "Use the security-reviewer agent to review src/auth.py and reply with its findings unchanged." --output-format json > review.json
jq -r .result review.json
```

</details>

## Check your work

```bash
D=/root/mastery/024-reviewer; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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

a = text(".claude/agents/security-reviewer.md")
fm = re.match(r"---\n(.*?)\n---\n", a, re.S)
meta = dict(l.split(":", 1) for l in (fm.group(1).splitlines() if fm else []) if ":" in l)
tools = {t.strip() for t in meta.get("tools", "").split(",") if t.strip()}
ok(meta.get("name", "").strip() == "security-reviewer" and len(meta.get("description", "")) > 20 and tools and not tools & {"Edit", "Write", "Bash", "NotebookEdit"},
   "security-reviewer.md has name, a real description, and read-only tools", f"frontmatter needs name: security-reviewer, a description, and tools without Edit/Write/Bash - got tools {sorted(tools)}")
ok("FINDING:" in a and "NO FINDINGS" in a, "the agent's prompt fixes the output format", "the body should define the FINDING: <file>:<line> - <issue> format and NO FINDINGS")
env = load("review.json") or {}
f, rows = transcript(env.get("session_id") or "none")
types = [(load(m) or {}).get("agentType") for m in glob.glob(os.path.join(f[:-6], "subagents", "*.meta.json"))] if f else []
res = env.get("result") or ""
ok("security-reviewer" in types, "the main agent delegated to security-reviewer", f"run the review prompt so the main agent invokes the security-reviewer subagent - saw {types}")
ok(re.search(r"FINDING: src/auth\.py:\d+ - .*(md5|hash)", res, re.I) and re.search(r"FINDING: src/auth\.py:\d+ - .*(sql|inject)", res, re.I),
   "the review flags the weak hash and the SQL injection", f"review.json should report both issues as FINDING lines - got {res!r}")
before = sha("src/auth.py")
rc, out, err = sh(["claude", "-p", "Apply fixes for every finding directly in src/auth.py.", "--agent", "security-reviewer", "--permission-mode", "acceptEdits", "--output-format", "json"], timeout=240)
ok(sha("src/auth.py") == before, "run as the main agent with edits allowed, the reviewer still could not change the file",
   "the reviewer edited src/auth.py - its tools must not include Edit or Write")
PYEOF
```

## What you learned

- .claude/agents/<name>.md holds a reusable specialist: frontmatter plus a self-contained system prompt.
- Tool restrictions are enforced, so a read-only reviewer cannot edit even when asked to.
- Specialists get used through good descriptions, by name in the prompt, or with --agent.
