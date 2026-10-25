---
type: task
title: "Store a project fact and recall it"
minutes: 23
---

## Set up

Set up creates `/root/mastery/012-memory` with a small `app.py` that does not mention any port.

```bash
mkdir -p /root/mastery/012-memory && cd /root/mastery/012-memory
cat > app.py <<'EOF'
import os

DB_HOST = os.environ.get("DB_HOST", "localhost")
EOF
```

## What to build

Save a fact in one session and prove a **different** session recalls it from memory.

1. From `/root/mastery/012-memory`, run this headless and save the envelope as `save.json`:
   > Remember for future sessions in this project: the staging database listens on port 6543.
2. Look in `~/.claude/projects/` for this project's `memory/` folder and read `MEMORY.md` and the topic file.
3. In a **new** session (no resume), run this and save the envelope as `recall.json`:
   > Which port does the staging database listen on? Reply with only the port number.

Do not write the port into any project file - the checker makes sure the answer could only have come from memory.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- The memory folder's name is the project path with `/` turned into `-`, e.g. `-root-mastery-012-memory`.
- If nothing was saved, check auto memory is on (`/memory`) and `CLAUDE_CODE_DISABLE_AUTO_MEMORY` is not set.

</details>

<details><summary>Solution</summary>

```bash
cd /root/mastery/012-memory
claude -p "Remember for future sessions in this project: the staging database listens on port 6543." --output-format json > save.json
claude -p "Which port does the staging database listen on? Reply with only the port number." --output-format json > recall.json
jq -r .result recall.json
```

</details>

## Check your work

```bash
D=/root/mastery/012-memory; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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

sv, rc_ = load("save.json") or {}, load("recall.json") or {}
f, rows = transcript(sv.get("session_id") or "none")
mem = os.path.join(os.path.dirname(f), "memory") if f else ""
idx = text(os.path.join(mem, "MEMORY.md"))
topics = [p for p in glob.glob(os.path.join(mem, "*.md")) if not p.endswith("MEMORY.md")]
ok(sv.get("subtype") == "success" and idx.strip() and any("6543" in text(p) for p in topics),
   "the save run wrote a memory file and indexed it in MEMORY.md",
   f"save.json's session should leave a topic file containing 6543 and a MEMORY.md index in {mem or '~/.claude/projects/<project>/memory'}")
ok(rc_.get("session_id") and rc_.get("session_id") != sv.get("session_id"), "recall.json is a different session",
   "ask in a new session - no --resume or --continue")
ok((rc_.get("result") or "").strip() == "6543", "the fresh session recalled the port", f"recall.json should answer exactly 6543 - got {rc_.get('result')!r}")
here = [p for p in glob.glob("**/*", recursive=True) if os.path.isfile(p) and not p.endswith(".json") and "6543" in text(p)]
ok(not here, "the port is not written in any project file, so it came from memory",
   f"remove 6543 from {here} - the answer must come from memory, not from the project")
PYEOF
```

## What you learned

- Only files survive a session: CLAUDE.md, auto memory, the transcript, and the project itself.
- Auto memory keeps a MEMORY.md index plus one topic file per fact, per project, on this machine only.
- A real recall test uses a fresh session and a fact that exists nowhere else.
