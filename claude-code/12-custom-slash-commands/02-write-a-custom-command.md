---
type: task
title: "Write a custom command"
minutes: 10
---

## Set up

Set up creates `/root/cc-lab/12-commands` with raw change lists for two releases in `changes/v1.4.txt` and `changes/v1.5.txt`.

```bash
mkdir -p /root/cc-lab/12-commands/changes && cd /root/cc-lab/12-commands
cat > changes/v1.4.txt <<'EOF'
fix: csv export used the wrong date format
feat: add dark mode toggle to settings
perf: dashboard loads 40% faster
fix: password reset emails were sent twice
EOF
cat > changes/v1.5.txt <<'EOF'
feat: export invoices as PDF
fix: search ignored accented characters
chore: upgrade to Python 3.12
EOF
claude --version
```

## What to build

1. Create the project command `/changelog` in `/root/cc-lab/12-commands/.claude/commands/changelog.md`:
   - front matter with a `description` (and an `argument-hint`);
   - a body that uses `$ARGUMENTS` as the version: read `changes/$ARGUMENTS.txt`, and output only the entry - first line exactly `## $ARGUMENTS`, then one `- ` bullet per line of the file, in order, rewritten for users.
2. Run it for both versions:

```bash
cd /root/cc-lab/12-commands
claude -p "/changelog v1.4" > v1.4.md
claude -p "/changelog v1.5" > v1.5.md
cat v1.4.md v1.5.md
```

`v1.4.md` should start with `## v1.4` and have exactly 4 bullets; `v1.5.md` starts with `## v1.5` and has 3.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- The file name is the command name.
- Front matter goes between two `---` lines at the very top.

</details>

<details><summary>Solution</summary>

```bash
mkdir -p /root/cc-lab/12-commands/.claude/commands && cd /root/cc-lab/12-commands
cat > .claude/commands/changelog.md <<'EOF'
---
description: Turn changes/<version>.txt into a changelog entry
argument-hint: <version>
allowed-tools: Read
---
Read changes/$ARGUMENTS.txt and write the changelog entry for version $ARGUMENTS.

Output only the entry, nothing before or after it:
- the first line is exactly: ## $ARGUMENTS
- then one "- " bullet per line of the file, in the same order
- rewrite each line as a short sentence a user would understand (no "feat:"/"fix:" prefixes)
EOF
cd /root/cc-lab/12-commands
claude -p "/changelog v1.4" > v1.4.md
claude -p "/changelog v1.5" > v1.5.md
cat v1.4.md v1.5.md
```

</details>

## Check your work

```bash
D=/root/cc-lab/12-commands; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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
cmd = text(".claude/commands/changelog.md")
fm = re.match(r"^---\n(.*?)\n---\n(.*)$", cmd, re.S)
ok(fm, ".claude/commands/changelog.md exists with front matter", "create .claude/commands/changelog.md starting with a --- front matter block")
ok(fm and re.search(r"^description:\s*\S", fm.group(1), re.M), "the command has a description", "add a description: line to the front matter")
ok(fm and "$ARGUMENTS" in fm.group(2), "the body uses $ARGUMENTS", "use $ARGUMENTS in the body for the version")
for v, n in (("v1.4", 4), ("v1.5", 3)):
    lines = [l.rstrip() for l in text(f"{v}.md").splitlines() if l.strip()]
    bullets = [l for l in lines if l.startswith("- ")]
    ok(lines and lines[0] == f"## {v}" and len(bullets) == n and len(lines) == n + 1, f"{v}.md is '## {v}' plus exactly {n} bullets", f"{v}.md should be '## {v}' then {n} '- ' bullets and nothing else - got {lines[:6]}")
    ok(ran(r"<command-name>/changelog</command-name>.*" + re.escape(v)), f"Claude Code ran /changelog {v} in this folder", f"run claude -p \"/changelog {v}\" in this folder")
PYEOF
```

## What you learned

- A custom command is a Markdown prompt in `.claude/commands/`; the file name is the command.
- `$ARGUMENTS` fills in whatever follows the command name.
- Commands work headless too: `claude -p "/changelog v1.4"`.
