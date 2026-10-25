---
type: task
title: "Write a project settings file"
minutes: 23
---

## Set up

Set up creates `/root/mastery/030-settings` with `scripts/show_env.py` (prints `APP_ENV` and `LOG_LEVEL`), a `.env`, and `secrets/prod.json` (both lab-only fakes).

```bash
rm -rf /root/mastery/030-settings && mkdir -p /root/mastery/030-settings/scripts /root/mastery/030-settings/secrets /root/mastery/030-settings/.claude && cd /root/mastery/030-settings
cat > scripts/show_env.py <<'EOF'
import os
print(f"APP_ENV={os.environ.get('APP_ENV', '-')} LOG_LEVEL={os.environ.get('LOG_LEVEL', '-')}")
EOF
cat > .env <<'EOF'
API_TOKEN=lab-only-token-0000
EOF
cat > secrets/prod.json <<'EOF'
{"db": "lab-only"}
EOF
```

## What to build

Write the settings this project ships to the team, plus your personal override, and prove each layer works.

1. `/root/mastery/030-settings/.claude/settings.json` with the `$schema` line, and:
   - `allow`: `Bash(python3 scripts/show_env.py)`, `Bash(python3 -m unittest *)`
   - `ask`: `Bash(git push *)`
   - `deny`: `Read(./.env)`, `Read(./secrets/**)`
   - `env`: `APP_ENV=test`, `LOG_LEVEL=info`
   - a `statusLine` of type `command`
2. `/root/mastery/030-settings/.claude/settings.local.json` that sets only `env.LOG_LEVEL=debug`, and add it to `.gitignore`.
3. Trust the folder, then run this headless with **no** permission flags, saving `run.json`:
   > Run python3 scripts/show_env.py, then read .env, then run git push origin main, and report what each step returned.

The checker reads the transcript: the script must run without a prompt and print `APP_ENV=test LOG_LEVEL=debug`, the `.env` read must be denied, and `git push` must be refused.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Ask rules are refusals in -p.
- If show_env.py is refused, the folder is not trusted yet.

</details>

<details><summary>Solution</summary>

```bash
cd /root/mastery/030-settings
cat > .claude/settings.json <<'EOF'
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "allow": ["Bash(python3 scripts/show_env.py)", "Bash(python3 -m unittest *)"],
    "ask": ["Bash(git push *)"],
    "deny": ["Read(./.env)", "Read(./secrets/**)"]
  },
  "env": { "APP_ENV": "test", "LOG_LEVEL": "info" },
  "statusLine": { "type": "command", "command": "jq -r '\"[030] \" + .model.display_name'" }
}
EOF
cat > .claude/settings.local.json <<'EOF'
{
  "env": { "LOG_LEVEL": "debug" }
}
EOF
echo '.claude/settings.local.json' >> .gitignore
[ -f ~/.claude.json ] || echo '{}' > ~/.claude.json
tmp=$(mktemp) && jq --arg p "$(pwd -P)" '.projects[$p].hasTrustDialogAccepted = true' ~/.claude.json > "$tmp" && mv "$tmp" ~/.claude.json
claude -p 'Run python3 scripts/show_env.py, then read .env, then run git push origin main, and report what each step returned.' --output-format json > run.json
jq -r .result run.json
```

</details>

## Check your work

```bash
D=/root/mastery/030-settings; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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

s, loc = load(".claude/settings.json"), load(".claude/settings.local.json")
ok(isinstance(s, dict) and str(s.get("$schema", "")).endswith("claude-code-settings.json"), ".claude/settings.json is valid JSON with the $schema line",
   ".claude/settings.json must be valid JSON with \"$schema\": \"https://json.schemastore.org/claude-code-settings.json\"")
s = s or {}
p = s.get("permissions") or {}
need = {"allow": ["Bash(python3 scripts/show_env.py)", "Bash(python3 -m unittest *)"], "ask": ["Bash(git push *)"], "deny": ["Read(./.env)", "Read(./secrets/**)"]}
miss = {k: [r for r in v if r not in (p.get(k) or [])] for k, v in need.items()}
ok(not any(miss.values()), "permissions has the allow, ask, and deny rules", f"missing permission rules: {miss}")
ok((s.get("env") or {}) == {"APP_ENV": "test", "LOG_LEVEL": "info"} and (s.get("statusLine") or {}).get("type") == "command",
   "the project file sets env APP_ENV=test, LOG_LEVEL=info and a command status line", "the project file needs env {APP_ENV: test, LOG_LEVEL: info} and a statusLine of type command")
ok(isinstance(loc, dict) and loc.get("env") == {"LOG_LEVEL": "debug"}, "settings.local.json overrides only LOG_LEVEL", ".claude/settings.local.json should be {\"env\": {\"LOG_LEVEL\": \"debug\"}}")
ok(".claude/settings.local.json" in text(".gitignore").split(), "the local file is git-ignored", "add .claude/settings.local.json to .gitignore")
env = load("run.json") or {}
f, rows = transcript(env.get("session_id") or "none")
show = result_for(rows, lambda u: u.get("name") == "Bash" and "show_env.py" in (u.get("input") or {}).get("command", ""))
ok(show and "APP_ENV=test LOG_LEVEL=debug" in rtext(show[-1]), "the allowed script ran and saw APP_ENV from the project and LOG_LEVEL from local",
   f"show_env.py should run without a prompt and print APP_ENV=test LOG_LEVEL=debug - got {[rtext(b)[:100] for b in show]}")
rd = result_for(rows, lambda u: u.get("name") == "Read" and (u.get("input") or {}).get("file_path", "").endswith("/.env"))
ok(rd and all(b.get("is_error") for b in rd) and not any("lab-only-token" in rtext(b) for b in results(rows)), "reading .env was denied and its value never reached Claude",
   "the Read of .env should fail with a permission error")
push = result_for(rows, lambda u: u.get("name") == "Bash" and "git push" in (u.get("input") or {}).get("command", ""))
ok(push and all(b.get("is_error") for b in push), "git push hit the ask rule and was refused in the headless run", "git push should be refused (ask rules cannot be answered in -p)")
PYEOF
```

## What you learned

- Precedence: managed, command line, project local, project, user.
- Permission lists merge across layers and deny wins; env merges key by key.
- Project allow rules need a trusted folder; ask means refused in headless runs.
