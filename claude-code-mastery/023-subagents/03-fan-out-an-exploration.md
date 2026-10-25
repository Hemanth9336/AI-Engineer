---
type: task
title: "Fan out an exploration"
minutes: 23
---

## Set up

Set up creates `/root/mastery/023-fanout/services/` with three services (billing, auth, search); each has a `config.toml` with its port, an `OWNERS` file, and an entrypoint script.

```bash
rm -rf /root/mastery/023-fanout && mkdir -p /root/mastery/023-fanout/services/billing /root/mastery/023-fanout/services/auth /root/mastery/023-fanout/services/search && cd /root/mastery/023-fanout
cat > services/billing/config.toml <<'EOF'
[server]
port = 8101
EOF
cat > services/billing/OWNERS <<'EOF'
team-payments
EOF
cat > services/billing/main.py <<'EOF'
"""Entrypoint for billing."""


def main():
    pass
EOF
cat > services/auth/config.toml <<'EOF'
[server]
port = 8102
EOF
cat > services/auth/OWNERS <<'EOF'
team-identity
EOF
cat > services/auth/server.py <<'EOF'
"""Entrypoint for auth."""


def main():
    pass
EOF
cat > services/search/config.toml <<'EOF'
[server]
port = 8103
EOF
cat > services/search/OWNERS <<'EOF'
team-discovery
EOF
cat > services/search/app.py <<'EOF'
"""Entrypoint for search."""


def main():
    pass
EOF
```

## What to build

Map the services with parallel, read-only scouts, keeping the file reads out of the main conversation.

1. Write `/root/mastery/023-fanout/agents.json` defining one subagent, `service-scout`: a description that says to use one per service, a prompt that asks for one line `name | port | owner | entrypoint`, read-only tools, and `model: haiku`.
2. Run this headless with the agents file and edits allowed (so the main agent can write MAP.md), saving the envelope as `run.json`:
   > Map every service under services/ using one service-scout subagent per service. Write MAP.md with a header line `service | port | owner | entrypoint` and one line per service, sorted by name.

The checker opens the session's `subagents/` folder to count the scouts and confirms the main conversation read no service files itself.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `--agents ./agents.json` works in `-p` mode.
- Each subagent's `.meta.json` names its `agentType`.

</details>

<details><summary>Solution</summary>

```bash
cd /root/mastery/023-fanout
cat > agents.json <<'EOF'
{
  "service-scout": {
    "description": "Reads one service folder and reports its port, owner, and entrypoint. Use one per service.",
    "prompt": "You inspect exactly one service folder. Reply with one line: name | port | owner | entrypoint.",
    "tools": ["Read", "Grep", "Glob"],
    "model": "haiku"
  }
}
EOF
claude -p "Map every service under services/ using one service-scout subagent per service. Write MAP.md with a header line `service | port | owner | entrypoint` and one line per service, sorted by name." --agents ./agents.json --permission-mode acceptEdits --output-format json > run.json
cat MAP.md
```

</details>

## Check your work

```bash
D=/root/mastery/023-fanout; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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

a = (load("agents.json") or {}).get("service-scout") or {}
tools = a.get("tools") or []
tools = tools.replace(",", " ").split() if isinstance(tools, str) else tools
ok(a.get("description") and a.get("prompt") and tools and not set(tools) & {"Edit", "Write", "Bash", "NotebookEdit"} and a.get("model") == "haiku",
   "agents.json defines a read-only service-scout on haiku", "agents.json needs service-scout with description, prompt, read-only tools (no Edit/Write/Bash), and model haiku")
env = load("run.json") or {}
f, rows = transcript(env.get("session_id") or "none")
subs = sorted(glob.glob(os.path.join(f[:-6], "subagents", "*.meta.json"))) if f else []
types = [(load(m) or {}).get("agentType") for m in subs]
ok(env.get("subtype") == "success" and types.count("service-scout") >= 3, f"the run fanned out to {types.count('service-scout')} service-scout subagents",
   f"run the prompt with --agents ./agents.json so the main agent starts one service-scout per service - subagents seen: {types}")
main_reads = [u["input"].get("file_path", "") for u in uses(rows) if u.get("name") == "Read" and "/services/" in u["input"].get("file_path", "")]
ok(not main_reads, "the main conversation never read the service files itself - the scouts did", f"the main agent read {main_reads} - delegate that to the scouts")
want = "service | port | owner | entrypoint\nauth | 8102 | team-identity | services/auth/server.py\nbilling | 8101 | team-payments | services/billing/main.py\nsearch | 8103 | team-discovery | services/search/app.py"
ok(text("MAP.md").strip() == want, "MAP.md has the header and the right port, owner, and entrypoint for each service", f"MAP.md should be:\n{want}")
PYEOF
```

## What you learned

- A subagent has its own context window and returns only its final answer.
- --agents defines session-only subagents; in -p it also takes a JSON file.
- Read-only tools and a cheap model make scouts safe and inexpensive; the subagents/ folder proves the fan-out.
