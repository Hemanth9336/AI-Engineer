---
type: task
title: "Build a write-audit hook"
minutes: 23
---

## Set up

Set up creates an empty project at `/root/mastery/027-audit` with `notes/` and `.claude/hooks/`.

```bash
rm -rf /root/mastery/027-audit && mkdir -p /root/mastery/027-audit/notes /root/mastery/027-audit/.claude/hooks && cd /root/mastery/027-audit
cat > README.md <<'EOF'
# Team notes
EOF
```

## What to build

Every file Claude writes or edits in this project must leave an audit line - and Claude should be told it was recorded.

1. Write `/root/mastery/027-audit/.claude/hooks/audit.py`. It reads the hook JSON from stdin and appends one JSON line to `$CLAUDE_PROJECT_DIR/.claude/audit.jsonl` with `session` (the session id), `tool`, `file` (the path **relative to the project root**, with symlinks resolved), and `tool_use_id`. It then prints only this to stdout: `{"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": "audit: recorded <file>"}}`.
2. Register it in `/root/mastery/027-audit/.claude/settings.json` as a `PostToolUse` hook with matcher `Write|Edit` and a 10-second timeout.
3. Run this headless with edits allowed, saving the envelope as `run.json`:
   > Create notes/standup.md containing the line `# Standup` and the line `- shipped the audit hook`, then change `shipped` to `finished` in that file, then list the notes folder.

The checker feeds your script sample events, then matches every audit line from the run to its tool call in the transcript. The `ls` in the run must **not** be audited.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `os.path.realpath` on both the file and `$CLAUDE_PROJECT_DIR` before `relpath`.
- Print nothing else on stdout - a debug `print` turns the JSON into plain text.

</details>

<details><summary>Solution</summary>

```bash
cd /root/mastery/027-audit
cat > .claude/hooks/audit.py <<'EOF'
#!/usr/bin/env python3
"""PostToolUse on Write|Edit: append one JSON line per file change to .claude/audit.jsonl and tell Claude."""
import json, os, sys

ev = json.load(sys.stdin)
proj = os.path.realpath(os.environ.get("CLAUDE_PROJECT_DIR") or ev.get("cwd") or ".")
path = (ev.get("tool_input") or {}).get("file_path") or ""
rel = os.path.relpath(os.path.realpath(path), proj) if path else ""
entry = {"session": ev.get("session_id"), "tool": ev.get("tool_name"), "file": rel, "tool_use_id": ev.get("tool_use_id")}
with open(os.path.join(proj, ".claude", "audit.jsonl"), "a") as f:
    f.write(json.dumps(entry) + "\n")
print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": f"audit: recorded {rel}"}}))
EOF
chmod +x .claude/hooks/audit.py
cat > .claude/settings.json <<'EOF'
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          { "type": "command", "command": "python3 \"$CLAUDE_PROJECT_DIR/.claude/hooks/audit.py\"", "timeout": 10 }
        ]
      }
    ]
  }
}
EOF
claude -p 'Create notes/standup.md containing the line `# Standup` and the line `- shipped the audit hook`, then change `shipped` to `finished` in that file, then list the notes folder.' --permission-mode acceptEdits --output-format json > run.json
cat .claude/audit.jsonl
```

</details>

## Check your work

```bash
D=/root/mastery/027-audit; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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

def matches(m, tool):
    m = m or ""
    if m in ("", "*"):
        return True
    if re.fullmatch(r"[A-Za-z0-9_\- ,|]+", m):
        return tool in [x.strip() for x in re.split(r"[|,]", m)]
    return re.search(m, tool) is not None
s = load(".claude/settings.json") or {}
groups = (s.get("hooks") or {}).get("PostToolUse") or []
good = [g for g in groups if matches(g.get("matcher"), "Write") and matches(g.get("matcher"), "Edit") and not matches(g.get("matcher"), "Bash")
        and any("audit.py" in (h.get("command") or "") + " ".join(h.get("args") or []) for h in g.get("hooks") or [])]
ok(good, "PostToolUse runs audit.py for Write and Edit, and not for Bash", f"register .claude/hooks/audit.py under hooks.PostToolUse with matcher Write|Edit - got {json.dumps(groups)[:200]}")
hook = os.path.abspath(".claude/hooks/audit.py")
t = tempfile.mkdtemp()
os.makedirs(t + "/.claude"); os.makedirs(t + "/sub")
ev = {"session_id": "chk-1", "hook_event_name": "PostToolUse", "tool_name": "Write", "cwd": t + "/sub",
      "tool_input": {"file_path": t + "/sub/x.md", "content": "x"}, "tool_response": {}, "tool_use_id": "toolu_chk1"}
Path(t + "/sub/x.md").write_text("x")
rc, out, err = sh(["python3", hook], cwd=t + "/sub", env={"CLAUDE_PROJECT_DIR": t}, input=json.dumps(ev))
line = (events(t + "/.claude/audit.jsonl") or [{}])[-1]
ok(rc == 0 and {k: line.get(k) for k in ("session", "tool", "file", "tool_use_id")} == {"session": "chk-1", "tool": "Write", "file": "sub/x.md", "tool_use_id": "toolu_chk1"},
   "the hook logs session, tool, project-relative file, and tool_use_id", f"for a Write of <project>/sub/x.md run from sub/, audit.jsonl should get session, tool, file 'sub/x.md', tool_use_id - got rc={rc} {line} {err.strip()[:150]}")
try:
    ctx = json.loads(out)["hookSpecificOutput"]
except Exception:
    ctx = {}
ok(ctx.get("hookEventName") == "PostToolUse" and "audit: recorded sub/x.md" in (ctx.get("additionalContext") or ""),
   "stdout is one JSON object whose additionalContext tells Claude what was recorded", f"print only {{\"hookSpecificOutput\": {{\"hookEventName\": \"PostToolUse\", \"additionalContext\": \"audit: recorded sub/x.md\"}}}} - got {out.strip()[:150]!r}")
env = load("run.json") or {}
sid = env.get("session_id")
mine = [x for x in events(".claude/audit.jsonl") if x.get("session") == sid]
ok(env.get("subtype") == "success" and [(x.get("tool"), x.get("file")) for x in mine] == [("Write", "notes/standup.md"), ("Edit", "notes/standup.md")],
   "the headless run fired the hook for the Write and the Edit only", f"run the prompt with --output-format json > run.json; audit.jsonl for that session should be Write then Edit of notes/standup.md - got {[(x.get('tool'), x.get('file')) for x in mine]}")
f, rows = transcript(sid or "none")
ids = [u["id"] for u in uses(rows) if u.get("name") in ("Write", "Edit")]
ok(ids and [x.get("tool_use_id") for x in mine] == ids, "each audit line's tool_use_id matches the tool call in the transcript", "log tool_use_id from the hook input so each line points at its tool call")
ok(f and "audit: recorded notes/standup.md" in text(f), "Claude received the hook's additionalContext", "the transcript has no 'audit: recorded notes/standup.md' - print the additionalContext JSON on stdout")
ok(text("notes/standup.md").strip() == "# Standup\n- finished the audit hook", "notes/standup.md has the edited content", "notes/standup.md should end as '# Standup' / '- finished the audit hook'")
PYEOF
```

## What you learned

- Hooks are event, matcher groups, then handlers; matching handlers run in parallel.
- Command hooks read one JSON object on stdin and answer with an exit code and optional JSON on stdout.
- PostToolUse additionalContext reaches Claude; tool_use_id ties a hook event to the transcript.
