---
type: task
title: "Turn a repeated task into a command"
minutes: 23
---

## Set up

Set up creates `/root/mastery/015-commands/CHANGELOG.md` with sections for 2.4.0 and 2.3.0.

```bash
mkdir -p /root/mastery/015-commands && cd /root/mastery/015-commands
cat > CHANGELOG.md <<'EOF'
# Changelog

## 2.4.0
- Added CSV export for invoices
- Fixed VAT rounding on credit notes

## 2.3.0
- Added dark mode
- Dropped Python 3.8
EOF
```

## What to build

Every release someone retypes "write release notes for version X from the changelog". Make it a project command.

1. Create `/root/mastery/015-commands/.claude/commands/release-notes.md`:
   - frontmatter with a `description` and an `argument-hint`;
   - a body containing the sentence `Write release notes for version $ARGUMENTS` (use only that version's section), with output starting `Release <version>` followed by one bullet per change.
2. Run it headlessly for 2.4.0 and save the envelope as `notes.json`.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Arguments are 0-based: the first one is `$0`, not `$1` - or use `$ARGUMENTS`.

</details>

<details><summary>Solution</summary>

```bash
cd /root/mastery/015-commands
mkdir -p .claude/commands
cat > .claude/commands/release-notes.md <<'EOF'
---
description: Write release notes for one version from CHANGELOG.md
argument-hint: <version>
allowed-tools: Read
---

Write release notes for version $ARGUMENTS using only that version's section of CHANGELOG.md.
Format: a first line `Release $ARGUMENTS`, then one bullet per change in user-facing language.
EOF
claude -p "/release-notes 2.4.0" --output-format json > notes.json
jq -r .result notes.json
```

</details>

## Check your work

```bash
D=/root/mastery/015-commands; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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

c = text(".claude/commands/release-notes.md")
fm = re.match(r"---\n(.*?)\n---\n", c, re.S)
ok(fm and "description:" in fm.group(1) and "argument-hint:" in fm.group(1),
   "the command file has a description and an argument hint", "start .claude/commands/release-notes.md with frontmatter holding description: and argument-hint:")
ok("Write release notes for version $ARGUMENTS" in c or "Write release notes for version $0" in c,
   "the body takes the version as an argument", "the body should say 'Write release notes for version $ARGUMENTS' (or $0 - arguments are 0-based)")
env = load("notes.json") or {}
f, rows = transcript(env.get("session_id") or "none")
body = "\n".join(b.get("text", "") for r in rows if r.get("type") == "user" for b in content(r) if b.get("type") == "text")
ok("<command-name>/release-notes</command-name>" in body and "Write release notes for version 2.4.0" in body,
   "the run invoked /release-notes and the argument was substituted", "run claude -p \"/release-notes 2.4.0\" and save notes.json")
r = env.get("result") or ""
ok(r.splitlines()[:1] == ["Release 2.4.0"] and "CSV" in r and "dark mode" not in r.lower(),
   "the notes cover 2.4.0 only", f"notes should start 'Release 2.4.0' and cover only that section - got {r!r}")
PYEOF
```

## What you learned

- A markdown file in .claude/commands/ becomes a /command; ~/.claude/commands/ makes it personal.
- $ARGUMENTS and 0-based $0, $1 carry input; frontmatter adds description, hint, tools, and model.
- claude -p "/command args" turns a team ritual into a scriptable tool.
