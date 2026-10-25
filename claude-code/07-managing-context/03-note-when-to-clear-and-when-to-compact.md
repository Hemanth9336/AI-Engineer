---
type: task
title: "Note when to clear and when to compact"
minutes: 7
---

## Set up

Set up writes six situations to `/root/cc-lab/07-context/situations.md`.

```bash
mkdir -p /root/cc-lab/07-context && cd /root/cc-lab/07-context
cat > situations.md <<'EOF'
# Context situations

S1. You just finished and committed a fix for the login bug. Next you'll write documentation for the unrelated billing module.

S2. Ninety minutes into building a feature, Claude warns that the context is nearly full. You're mid-task and it still needs the decisions you made along the way.

S3. You've switched from chasing a flaky CI test to reviewing a teammate's change in a different part of the codebase.

S4. Halfway through a long database migration, you want to free up space but keep going. Claude must still remember which tables are already migrated and the naming rule you agreed on.

S5. You started a session two minutes ago and have asked one short question.

S6. Earlier you pasted a 4,000-line log to investigate an outage. That's solved; now you want to start a new feature in the same session.
EOF
```

## What to build

1. Read `/root/cc-lab/07-context/situations.md`. For each situation decide: **clear**, **compact** or **neither**.
2. Write `/root/cc-lab/07-context/decisions.txt` with one line per situation, in order, exactly like `S1: clear`.
3. Write `/root/cc-lab/07-context/compact.txt` with the single `/compact` command - including focus instructions - that you'd type in situation S4.
4. Optional: open `claude` anywhere, run `/context`, and look at what fills a fresh window.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Different task next? clear. Same task, window heavy? compact. Fresh and fine? neither.
- S4's focus instructions should mention the migrated tables.

</details>

<details><summary>Solution</summary>

```bash
cd /root/cc-lab/07-context
cat > decisions.txt <<'EOF'
S1: clear
S2: compact
S3: clear
S4: compact
S5: neither
S6: clear
EOF
cat > compact.txt <<'EOF'
/compact keep the list of tables already migrated and the naming rule we agreed; drop the debugging output
EOF
cat decisions.txt compact.txt
```

</details>

## Check your work

```bash
D=/root/cc-lab/07-context; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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
key = {"S1": "clear", "S2": "compact", "S3": "clear", "S4": "compact", "S5": "neither", "S6": "clear"}
why = {"S1": "a finished task followed by unrelated work", "S2": "the same task with a full window", "S3": "a switch to different work",
       "S4": "the same task where history must survive", "S5": "a fresh session", "S6": "a polluted conversation before new work"}
got = {}
for line in text("decisions.txt").splitlines():
    m = re.match(r"^\s*(S\d)\s*:\s*(\w+)\s*$", line, re.I)
    if m:
        got[m.group(1).upper()] = m.group(2).lower()
ok(len(got) == 6, "decisions.txt has a decision for all six situations", f"decisions.txt needs six lines like 'S1: clear' - found {len(got)}")
for s, want in key.items():
    ok(got.get(s) == want, f"{s}: {want} - right for {why[s]}", f"{s} is not '{got.get(s)}' - think about {why[s]}")
c = text("compact.txt").strip()
ok(c.startswith("/compact ") and len(c.split()) >= 5 and "table" in c.lower(), "compact.txt is a /compact with focus instructions that keep the migrated tables", f"compact.txt should be one '/compact ...' line with instructions that mention the migrated tables - got {c[:120]!r}")
PYEOF
```

## What you learned

- `/clear` is for a different task; `/compact` is for the same task with less weight.
- Focus instructions decide what survives a compaction.
- Sometimes the right move is neither.
