---
type: task
title: "Write a session handoff file"
minutes: 23
---

## Set up

Set up creates `/root/mastery/009-handoff` with `TASKS.md` (two tasks) and `text.py`, where `slugify` is a stub.

```bash
mkdir -p /root/mastery/009-handoff && cd /root/mastery/009-handoff
cat > text.py <<'EOF'
"""Text helpers."""


def slugify(value):
    raise NotImplementedError
EOF
cat > TASKS.md <<'EOF'
# Tasks
1. Implement slugify(value) in text.py: lowercase; spaces and underscores become hyphens; drop every other character that is not a letter, digit, or hyphen.
2. Add unit tests for slugify.
EOF
```

## What to build

Split one job across two sessions and make a file - not memory of the conversation - carry the work between them. Run everything headless from `/root/mastery/009-handoff`.

1. **Session 1** - do task 1, saving the envelope as `s1.json`:
   > Implement task 1 from TASKS.md in text.py. Do only task 1.
2. **Handoff** - *resume session 1* and have it write the handoff, saving the envelope as `handoff.json`:
   > Write HANDOFF.md for a fresh session that has none of this conversation: sections ## Goal, ## Done, ## Next, ## Files. Next is task 2 from TASKS.md.
3. **Session 2** - a brand-new session (no resume) whose prompt does not mention slugify, saving `s2.json`:
   > Read HANDOFF.md and complete its Next section.

   Session 2 will need to run the tests, so pre-approve only that command.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `--resume "$(jq -r .session_id s1.json)"` continues session 1 with all its context.
- Both editing runs need `--permission-mode acceptEdits`.

</details>

<details><summary>Solution</summary>

```bash
cd /root/mastery/009-handoff
claude -p "Implement task 1 from TASKS.md in text.py. Do only task 1." --permission-mode acceptEdits --output-format json > s1.json
claude -p "Write HANDOFF.md for a fresh session that has none of this conversation: sections ## Goal, ## Done, ## Next, ## Files. Next is task 2 from TASKS.md." --resume "$(jq -r .session_id s1.json)" --permission-mode acceptEdits --output-format json > handoff.json
claude -p "Read HANDOFF.md and complete its Next section." --permission-mode acceptEdits --allowedTools "Bash(python3 -m unittest *)" --output-format json > s2.json
jq -r '.session_id' s1.json handoff.json s2.json
```

</details>

## Check your work

```bash
D=/root/mastery/009-handoff; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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

s1, ho, s2 = load("s1.json") or {}, load("handoff.json") or {}, load("s2.json") or {}
probe = sh("python3 -c 'from text import slugify as s; print(s(\"Q3 Report_final v2!\"))'")[1].strip()
ok(probe == "q3-report-final-v2", "slugify works on input the tests never used", f"slugify('Q3 Report_final v2!') should be q3-report-final-v2 - got {probe!r}")
ok(s1.get("subtype") == "success" and ho.get("session_id") == s1.get("session_id"),
   "handoff.json was written by resuming the session that did the work",
   "run the handoff prompt with --resume <session_id from s1.json> so it has the context")
h = text("HANDOFF.md")
heads = [x for x in ("## Goal", "## Done", "## Next", "## Files") if x in h]
ok(len(heads) == 4 and "text.py" in h and len(h.splitlines()) <= 40,
   "HANDOFF.md has Goal, Done, Next, and Files and stays short",
   f"HANDOFF.md needs ## Goal, ## Done, ## Next, ## Files, name text.py, and stay under 40 lines - found {heads}")
sid2 = s2.get("session_id")
f, rows = transcript(sid2 or "none")
seq = [(u.get("name"), u["input"]) for u in uses(rows)]
ok(sid2 and sid2 != s1.get("session_id") and seq and seq[0][0] == "Read" and str(seq[0][1].get("file_path", "")).endswith("HANDOFF.md"),
   "s2.json is a fresh session whose first move was reading the handoff",
   "s2.json should come from a new session (no --resume/--continue) that starts by reading HANDOFF.md")
ok(not any("slugify" in p for p in prompts(rows)), "the fresh session was never told about slugify in its prompt",
   "the fresh session's prompt must not mention slugify - the handoff has to carry it")
rc, out, err = sh("python3 -m unittest -q")
ok(os.path.exists("test_text.py") and "slugify" in text("test_text.py") and rc == 0 and "Ran 0 tests" not in err,
   "the fresh session added passing tests for slugify", "test_text.py should exist, test slugify, and pass")
PYEOF
```

## What you learned

- Tool results fill the context window fastest; /context shows what is using it.
- Compaction keeps CLAUDE.md, memory, plans, and a few files - conversation detail only survives if the summary kept it.
- A handoff file written by the session with the context lets a fresh session continue cleanly.
