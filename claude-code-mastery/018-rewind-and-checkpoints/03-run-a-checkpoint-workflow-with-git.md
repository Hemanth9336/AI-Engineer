---
type: task
title: "Run a checkpoint workflow with git"
minutes: 20
---

## Set up

Set up creates a git repo at `/root/mastery/018-checkpoint` with `util.py`, `app.py`, and a `legacy/` folder that a cron job still needs. The tree is clean.

```bash
rm -rf /root/mastery/018-checkpoint && mkdir -p /root/mastery/018-checkpoint/legacy && cd /root/mastery/018-checkpoint
git init -q && git symbolic-ref HEAD refs/heads/main && git config user.email dev@example.com && git config user.name 'Dev Lab'
cat > util.py <<'EOF'
def money(cents):
    return f"${cents / 100:.2f}"
EOF
cat > legacy/report.py <<'EOF'
# still imported by the finance cron job
from util import money
EOF
cat > app.py <<'EOF'
from util import money

print(money(1234))
EOF
git add -A && git commit -q -m 'chore: initial import'
```

## What to build

Let the agent make a change you will reject, and get back with git - the way you must when the change happened through Bash.

1. Confirm the tree is clean and tag the checkpoint `cp-before-cleanup`.
2. Run this headless with `--permission-mode acceptEdits`, saving the envelope **outside the repo** for now:
   > Clean up this repo: remove the legacy/ folder and rename util.py to helpers.py.
3. Save `git status --short` as `damage.txt` - it shows the deletions a plain `git diff` would not.
4. You remember the cron job needs `legacy/`. Restore everything to the checkpoint, removing what the agent created but keeping `damage.txt`.
5. Move the run's envelope into the repo as `.runs/cleanup.json`.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `git clean -fd -e damage.txt` removes untracked files except the one you want to keep.
- acceptEdits auto-approves rm and mv inside the working folder - one reason to checkpoint first.

</details>

<details><summary>Solution</summary>

```bash
cd /root/mastery/018-checkpoint
git status --short
git tag cp-before-cleanup
claude -p "Clean up this repo: remove the legacy/ folder and rename util.py to helpers.py." --permission-mode acceptEdits --output-format json > /tmp/cleanup-018.json
git status --short > damage.txt
cat damage.txt
git reset --hard cp-before-cleanup
git clean -fd -e damage.txt
mkdir -p .runs && mv /tmp/cleanup-018.json .runs/cleanup.json
git status --short
```

</details>

## Check your work

```bash
D=/root/mastery/018-checkpoint; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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

rc, tag, _ = sh("git rev-parse -q --verify refs/tags/cp-before-cleanup^{commit}")
first = sh("git rev-list --max-parents=0 HEAD")[1].strip()
ok(rc == 0 and tag.strip() == first, "cp-before-cleanup tags the starting commit", "tag the starting commit: git tag cp-before-cleanup (before the agent runs)")
env = load(".runs/cleanup.json") or {}
f, rows = transcript(env.get("session_id") or "none")
cmds = [u["input"].get("command", "") for u in uses(rows) if u.get("name") == "Bash"]
ok(any(re.search(r"\brm\b.*legacy", c) for c in cmds) and any(re.search(r"\bmv\b.*util\.py", c) for c in cmds),
   "the agent's cleanup ran through Bash (rm and mv) - changes /rewind would not track",
   "save the cleanup run's envelope as .runs/cleanup.json; its transcript should show the rm and mv")
d = text("damage.txt")
ok(re.search(r"(?m)^ ?D +legacy/report\.py", d) and re.search(r"(?m)^ ?D +util\.py", d) and re.search(r"(?m)^\?\? +helpers\.py", d),
   "damage.txt captured the deletions and the new file from git status", f"damage.txt should be git status --short after the run - got {d!r}")
st = sh("git status --porcelain --untracked-files=all")[1].splitlines()
left = [l for l in st if not l.endswith(("damage.txt", ".runs/cleanup.json")) and ".runs/" not in l]
ok(not left and os.path.isfile("legacy/report.py") and os.path.isfile("util.py") and not os.path.exists("helpers.py")
   and sh("git rev-parse HEAD")[1].strip() == tag.strip(),
   "the repo is back at the checkpoint: legacy/ and util.py restored, helpers.py gone",
   f"restore with git reset --hard cp-before-cleanup and git clean -fd - still different: {left}")
PYEOF
```

## What you learned

- /rewind restores edits made by Claude's file tools, not files changed only by Bash, subagents, or you.
- Tag a clean tree before a risky run; git sees every change, whatever made it.
- git status shows deletions and new files; reset --hard plus clean -fd returns to the checkpoint.
