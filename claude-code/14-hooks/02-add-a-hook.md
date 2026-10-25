---
type: task
title: "Add a hook"
minutes: 12
---

## Set up

Set up creates a tiny Python app in `/root/cc-lab/14-hooks`.

```bash
mkdir -p /root/cc-lab/14-hooks/app && cd /root/cc-lab/14-hooks
cat > app/hello.py <<'EOF'
def greet(name):
    return f"Hello, {name}!"
EOF
cat > app/util.py <<'EOF'
def shout(text):
    return text.upper()
EOF
claude --version
```

## What to build

Add a **PostToolUse** hook that logs every file Claude edits and pushes back when a Python file doesn't compile.

1. Write `/root/cc-lab/14-hooks/.claude/hooks/log_edit.py`. It reads the hook's JSON from stdin and:
   - appends `<tool_name> <path relative to the project>` to `.claude/edits.log` (project = `$CLAUDE_PROJECT_DIR`), for example `Edit app/hello.py`;
   - if the file ends in `.py` and `python3 -m py_compile` fails on it, prints the error to **stderr** and exits **2**; otherwise exits 0.
2. Register it in `/root/cc-lab/14-hooks/.claude/settings.json` under `hooks.PostToolUse` with matcher `Edit|Write` and the command `python3 "$CLAUDE_PROJECT_DIR/.claude/hooks/log_edit.py"`.
3. Let Claude make an edit and look at the log:

```bash
cd /root/cc-lab/14-hooks
claude -p "Add a one-line docstring to the greet function in app/hello.py" --permission-mode acceptEdits --max-turns 6
cat .claude/edits.log
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `json.load(sys.stdin)` gives you the event; the path is `event["tool_input"]["file_path"]`.
- Use `os.path.relpath(os.path.realpath(path), os.path.realpath(project))` so symlinked folders don't break the relative path.

</details>

<details><summary>Solution</summary>

```bash
mkdir -p /root/cc-lab/14-hooks/.claude/hooks && cd /root/cc-lab/14-hooks
cat > .claude/hooks/log_edit.py <<'EOF'
#!/usr/bin/env python3
"""PostToolUse hook: log every file edit, and make Claude fix Python files that don't compile."""
import json
import os
import subprocess
import sys

event = json.load(sys.stdin)
project = os.environ.get("CLAUDE_PROJECT_DIR") or event.get("cwd", ".")
path = event.get("tool_input", {}).get("file_path", "")
rel = os.path.relpath(os.path.realpath(path), os.path.realpath(project))

with open(os.path.join(project, ".claude", "edits.log"), "a") as log:
    log.write(f"{event.get('tool_name')} {rel}\n")

if path.endswith(".py"):
    r = subprocess.run([sys.executable, "-m", "py_compile", path], capture_output=True, text=True)
    if r.returncode != 0:
        print(f"{rel} does not compile - fix it:\n{r.stderr}", file=sys.stderr)
        sys.exit(2)
EOF
chmod +x .claude/hooks/log_edit.py
cat > .claude/settings.json <<'EOF'
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {"type": "command", "command": "python3 \"$CLAUDE_PROJECT_DIR/.claude/hooks/log_edit.py\""}
        ]
      }
    ]
  }
}
EOF
cd /root/cc-lab/14-hooks
claude -p "Add a one-line docstring to the greet function in app/hello.py" --permission-mode acceptEdits --max-turns 6
cat .claude/edits.log
```

</details>

## Check your work

```bash
D=/root/cc-lab/14-hooks; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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
s = load(".claude/settings.json") or {}
entries = (s.get("hooks") or {}).get("PostToolUse") or []
def matches(e, tool):
    try:
        return re.fullmatch(e.get("matcher") or ".*", tool) is not None or e.get("matcher") == "*"
    except re.error:
        return False
good = [e for e in entries if matches(e, "Edit") and matches(e, "Write") and any("log_edit.py" in h.get("command", "") for h in e.get("hooks", []))]
ok(good, "settings.json registers log_edit.py as a PostToolUse hook for Edit and Write", f"add a hooks.PostToolUse entry with matcher Edit|Write running log_edit.py - got {json.dumps(entries)[:200]}")
hook = os.path.abspath(".claude/hooks/log_edit.py")
with tempfile.TemporaryDirectory() as t:
    os.makedirs(os.path.join(t, ".claude"))
    os.makedirs(os.path.join(t, "pkg"))
    Path(t, "pkg", "fine.py").write_text("x = 1\n")
    Path(t, "pkg", "broken.py").write_text("def oops(:\n")
    Path(t, "notes.md").write_text("hi\n")
    def fire(tool, rel):
        ev = {"hook_event_name": "PostToolUse", "tool_name": tool, "tool_input": {"file_path": os.path.join(t, rel)}, "cwd": t, "session_id": "x"}
        return sh([sys.executable, hook], input=json.dumps(ev), env={"CLAUDE_PROJECT_DIR": t})
    rc1, _, e1 = fire("Write", "pkg/fine.py")
    rc2, _, e2 = fire("Edit", "pkg/broken.py")
    rc3, _, e3 = fire("Write", "notes.md")
    log = Path(t, ".claude", "edits.log").read_text() if Path(t, ".claude", "edits.log").exists() else ""
    ok(log.splitlines() == ["Write pkg/fine.py", "Edit pkg/broken.py", "Write notes.md"], "the hook logs '<tool> <relative path>' for every edit", f"for three edits the log should be ['Write pkg/fine.py', 'Edit pkg/broken.py', 'Write notes.md'] - got {log.splitlines()} {(e1 + e3)[-200:]}")
    ok(rc1 == 0 and rc3 == 0, "valid Python and non-Python files pass (exit 0)", f"fine.py and notes.md should exit 0 - got {rc1}, {rc3}")
    ok(rc2 == 2 and "broken.py" in e2, "a Python file that doesn't compile is pushed back to Claude (exit 2, error on stderr)", f"broken.py should exit 2 with an error on stderr - got exit {rc2}, stderr {e2[-150:]!r}")
real = text(".claude/edits.log").splitlines()
ok(any(re.fullmatch(r"(Edit|Write|MultiEdit) app/hello\.py", l) for l in real), "the real run logged Claude's edit to app/hello.py", f".claude/edits.log should contain 'Edit app/hello.py' from the claude -p run - got {real[-3:]}")
import ast
try:
    fn = next(n for n in ast.parse(text("app/hello.py")).body if isinstance(n, ast.FunctionDef) and n.name == "greet")
    doc = ast.get_docstring(fn)
except Exception:
    doc = None
ok(doc, "greet now has a docstring", "app/hello.py's greet should have a docstring")
PYEOF
```

## What you learned

- Hooks run your commands at fixed points in the loop - the model can't skip them.
- A hook gets the event as JSON on stdin; exit 2 sends stderr back to Claude.
- PostToolUse with matcher `Edit|Write` is the place for format, lint and log steps.
