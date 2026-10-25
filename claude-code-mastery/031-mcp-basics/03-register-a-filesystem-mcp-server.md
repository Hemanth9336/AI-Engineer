---
type: task
title: "Register a filesystem MCP server"
minutes: 23
---

## Set up

Set up creates `/root/mastery/031-mcp/handbook/` with `oncall.md` and `holidays.md`, and checks that `mcp-server-filesystem` (the official filesystem MCP server) is installed.

```bash
rm -rf /root/mastery/031-mcp && mkdir -p /root/mastery/031-mcp/handbook && cd /root/mastery/031-mcp
cat > handbook/oncall.md <<'EOF'
# On-call

Primary: Ingrid Berg, +47 555 0199
Secondary: Tomas Lind, +47 555 0142
Escalation channel: #ops-oncall
EOF
cat > handbook/holidays.md <<'EOF'
# Holidays

Office closed 24-26 December.
EOF
command -v mcp-server-filesystem >/dev/null && echo 'mcp-server-filesystem OK' || echo 'mcp-server-filesystem missing - run setup/claude-code-mastery/install-tools.sh'
```

## What to build

Give the team's agent a handbook server everyone gets from the repo.

1. In `/root/mastery/031-mcp`, register the filesystem server as `handbook` at **project** scope, serving `/root/mastery/031-mcp/handbook`, and look at `.mcp.json`. `claude mcp list` shows it as **pending approval** - a server that arrives with a repository is not trusted automatically. Approve it for yourself with `"enabledMcpjsonServers": ["handbook"]` in `.claude/settings.local.json` (or by answering the prompt in `claude`), trust the folder (approvals are ignored until you do), and confirm it is connected.
2. Ask this headless, allowing only the two handbook tools it needs, and save the envelope as `answer.json`:
   > Using the handbook MCP server, find the primary on-call engineer and their phone number. Reply with `name, phone` only.

The checker reads `.mcp.json`, health-checks the server, and confirms from the transcript that Claude used `mcp__handbook__*` tools rather than its built-in Read.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `claude mcp add --scope project <name> -- <command> <args>`.
- `--allowedTools "mcp__handbook__list_directory,mcp__handbook__read_text_file"`.

</details>

<details><summary>Solution</summary>

```bash
cd /root/mastery/031-mcp
claude mcp add --scope project handbook -- mcp-server-filesystem /root/mastery/031-mcp/handbook
mkdir -p .claude && echo '{"enabledMcpjsonServers": ["handbook"]}' > .claude/settings.local.json
[ -f ~/.claude.json ] || echo '{}' > ~/.claude.json
tmp=$(mktemp) && jq --arg p "$(pwd -P)" '.projects[$p].hasTrustDialogAccepted = true' ~/.claude.json > "$tmp" && mv "$tmp" ~/.claude.json
claude mcp list
claude -p 'Using the handbook MCP server, find the primary on-call engineer and their phone number. Reply with `name, phone` only.' --allowedTools "mcp__handbook__list_directory,mcp__handbook__read_text_file" --output-format json > answer.json
jq -r .result answer.json
```

</details>

## Check your work

```bash
D=/root/mastery/031-mcp; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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

srv = ((load(".mcp.json") or {}).get("mcpServers") or {}).get("handbook") or {}
args = srv.get("args") or []
ok(os.path.basename(srv.get("command", "")) == "mcp-server-filesystem" or "@modelcontextprotocol/server-filesystem" in " ".join(args),
   ".mcp.json registers handbook as the filesystem server (project scope)", "run claude mcp add --scope project handbook -- mcp-server-filesystem <handbook dir>")
ok(any(os.path.realpath(os.path.join(".", a)) == os.path.realpath("handbook") for a in args), "the server is pointed at the handbook folder",
   f"pass the handbook folder as the server's argument - args are {args}")
rc, out, err = sh("claude mcp list", timeout=90)
ok(re.search(r"^handbook:.*Connected", out, re.M), "claude mcp list shows handbook approved and connected",
   f"approve the project server (enabledMcpjsonServers in .claude/settings.local.json) so claude mcp list shows it connected - got {(out + err).strip()[-200:]}")
env = load("answer.json") or {}
res = (env.get("result") or "")
ok(env.get("subtype") == "success" and "Ingrid Berg" in res and "+47 555 0199" in res, "the answer names Ingrid Berg, +47 555 0199",
   f"answer.json should be a successful run whose result is 'Ingrid Berg, +47 555 0199' - got {res[:120]!r}")
f, rows = transcript(env.get("session_id") or "none")
names = [u.get("name") for u in uses(rows)]
ok("mcp__handbook__read_text_file" in names and not set(names) & {"Read", "Grep", "Glob", "Bash"},
   "Claude read the file through mcp__handbook__ tools only", f"the run should use mcp__handbook__* tools, not built-ins - tools used: {names}")
PYEOF
```

## What you learned

- MCP servers add tools named mcp__<server>__<tool> that use normal permissions.
- Scopes: local (default), project (.mcp.json, shared), user.
- Allow only the MCP tools a headless run needs; --strict-mcp-config makes CI reproducible.
