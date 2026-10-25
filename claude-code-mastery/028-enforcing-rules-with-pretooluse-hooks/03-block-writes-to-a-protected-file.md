---
type: task
title: "Block writes to a protected file"
minutes: 23
---

## Set up

Set up creates `/root/mastery/028-protect` with `config/prod.yaml`, `config/staging.yaml`, `poetry.lock`, an applied migration, `src/app.py`, and `CHANGELOG.md`.

```bash
rm -rf /root/mastery/028-protect && mkdir -p /root/mastery/028-protect/config /root/mastery/028-protect/migrations/applied /root/mastery/028-protect/src /root/mastery/028-protect/.claude/hooks && cd /root/mastery/028-protect
cat > config/prod.yaml <<'EOF'
service: checkout
replicas: 2
region: eu-north-1
EOF
cat > config/staging.yaml <<'EOF'
service: checkout
replicas: 1
EOF
cat > CHANGELOG.md <<'EOF'
# Changelog

## Unreleased
EOF
cat > poetry.lock <<'EOF'
# lock
EOF
cat > migrations/applied/0001_init.sql <<'EOF'
CREATE TABLE t (id int);
EOF
cat > src/app.py <<'EOF'
print('checkout')
EOF
```

## What to build

"Never edit production config, lock files, or applied migrations" is in your team's CLAUDE.md. Make it enforced.

1. Write `/root/mastery/028-protect/.claude/protected.txt` with the patterns `config/prod.yaml`, `*.lock`, and `migrations/applied/*` (lines starting with `#` are comments).
2. Write `/root/mastery/028-protect/.claude/hooks/protect.py`: resolve `tool_input.file_path` relative to `$CLAUDE_PROJECT_DIR` (so `config/../config/prod.yaml` counts), and if it matches a pattern, print `protected: <file> ...` to **stderr** and **exit 2**. Otherwise exit 0 silently.
3. Register it as a `PreToolUse` hook with matcher `Edit|Write`.
4. Run this headless with edits allowed, saving the envelope as `run.json`:
   > Set replicas to 5 in config/prod.yaml. If that file is protected, do not work around it: instead add the line `- requested: replicas 5 (needs ops)` directly under `## Unreleased` in CHANGELOG.md.

The checker runs your hook on six paths, then confirms from the transcript that the run's edit was blocked and that Claude did what the message said instead.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Exit 1 does not block - only exit 2 (or a JSON deny) does.
- A pattern without `/` such as `*.lock` should match the file name anywhere.

</details>

<details><summary>Solution</summary>

```bash
cd /root/mastery/028-protect
cat > .claude/protected.txt <<'EOF'
# Files Claude must never change - one pattern per line, relative to the project root
config/prod.yaml
*.lock
migrations/applied/*
EOF
cat > .claude/hooks/protect.py <<'EOF'
#!/usr/bin/env python3
"""PreToolUse on Edit|Write: refuse changes to files listed in .claude/protected.txt (exit 2, reason on stderr)."""
import fnmatch, json, os, sys

ev = json.load(sys.stdin)
proj = os.path.realpath(os.environ.get("CLAUDE_PROJECT_DIR") or ev.get("cwd") or ".")
path = (ev.get("tool_input") or {}).get("file_path") or ""
if not path:
    sys.exit(0)
rel = os.path.relpath(os.path.realpath(os.path.join(ev.get("cwd") or proj, path)), proj)
patterns = [l.strip() for l in open(os.path.join(proj, ".claude", "protected.txt")) if l.strip() and not l.startswith("#")]
for p in patterns:
    if fnmatch.fnmatch(rel, p) or ("/" not in p and fnmatch.fnmatch(os.path.basename(rel), p)):
        print(f"protected: {rel} matches '{p}' in .claude/protected.txt - do not edit it; ask the owner", file=sys.stderr)
        sys.exit(2)
EOF
chmod +x .claude/hooks/protect.py
cat > .claude/settings.json <<'EOF'
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          { "type": "command", "command": "python3 \"$CLAUDE_PROJECT_DIR/.claude/hooks/protect.py\"", "timeout": 10 }
        ]
      }
    ]
  }
}
EOF
claude -p 'Set replicas to 5 in config/prod.yaml. If that file is protected, do not work around it: instead add the line `- requested: replicas 5 (needs ops)` directly under `## Unreleased` in CHANGELOG.md.' --permission-mode acceptEdits --output-format json > run.json
cat CHANGELOG.md
```

</details>

## Check your work

```bash
D=/root/mastery/028-protect; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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
CASES = [["Write", "config/prod.yaml", 2], ["Edit", "poetry.lock", 2], ["Write", "migrations/applied/0001_init.sql", 2], ["Edit", "config/../config/prod.yaml", 2], ["Write", "src/app.py", 0], ["Edit", "config/staging.yaml", 0]]
PROD = "service: checkout\nreplicas: 2\nregion: eu-north-1"

s = load(".claude/settings.json") or {}
groups = (s.get("hooks") or {}).get("PreToolUse") or []
ok(any(set(re.split(r"\s*[|,]\s*", g.get("matcher") or "")) >= {"Edit", "Write"} and any("protect.py" in (h.get("command") or "") + " ".join(h.get("args") or []) for h in g.get("hooks") or []) for g in groups),
   "PreToolUse runs protect.py for Edit and Write", "register .claude/hooks/protect.py under hooks.PreToolUse with matcher Edit|Write")
hook, here = os.path.abspath(".claude/hooks/protect.py"), os.path.realpath(".")
for tool, rel, want in CASES:
    ev = {"hook_event_name": "PreToolUse", "tool_name": tool, "cwd": here, "tool_input": {"file_path": os.path.join(here, rel)}}
    rc, out, err = sh(["python3", hook], env={"CLAUDE_PROJECT_DIR": here}, input=json.dumps(ev))
    good = rc == want and (want == 0 or "protected" in err)
    ok(good, f"{tool} {rel} -> exit {want}", f"{tool} {rel} should exit {want}" + (" with 'protected: ...' on stderr" if want else "") + f" - got exit {rc} {err.strip()[:120]!r}")
env = load("run.json") or {}
f, rows = transcript(env.get("session_id") or "none")
blocked = result_for(rows, lambda u: u.get("name") in ("Edit", "Write") and "prod.yaml" in (u.get("input") or {}).get("file_path", ""))
ok(blocked and all(b.get("is_error") and "protected" in rtext(b) for b in blocked),
   "the run's edit to config/prod.yaml was blocked and Claude got the reason", f"the transcript should show the prod.yaml edit failing with your 'protected:' message - got {[rtext(b)[:120] for b in blocked]}")
ok(text("config/prod.yaml").strip() == PROD.strip(), "config/prod.yaml is unchanged", "config/prod.yaml was modified - the guard did not hold")
ok("## Unreleased\n- requested: replicas 5 (needs ops)" in text("CHANGELOG.md"), "Claude followed the reason and recorded the request in CHANGELOG.md",
   "CHANGELOG.md should have '- requested: replicas 5 (needs ops)' under '## Unreleased'")
PYEOF
```

## What you learned

- PreToolUse exit 2 blocks the call and hands stderr to Claude as the reason.
- Exit 1, a crash, or a wrong path fails open unless the handler sets onFailure: block.
- Normalize paths against $CLAUDE_PROJECT_DIR before matching, and test hooks by piping events in.
