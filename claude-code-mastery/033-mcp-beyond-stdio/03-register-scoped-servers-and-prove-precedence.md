---
type: task
title: "Register scoped servers and prove precedence"
minutes: 20
---

## Set up

Set up writes `/root/mastery/033-remote/status_server.py`: an MCP server with a `whoami` tool, a `status://summary` resource, and an `incident_brief` prompt. It serves HTTP or SSE on the port you give it and reports the `--label` it was started with.

```bash
[ -f /root/mastery/033-remote/servers.pid ] && kill $(cat /root/mastery/033-remote/servers.pid) 2>/dev/null || true
rm -rf /root/mastery/033-remote && mkdir -p /root/mastery/033-remote/logs && cd /root/mastery/033-remote
cat > status_server.py <<'EOF'
"""Status MCP server for the lab: a tool, a resource, and a prompt, over HTTP or SSE."""
import argparse

from mcp.server.fastmcp import FastMCP

ap = argparse.ArgumentParser()
ap.add_argument("--label", required=True)
ap.add_argument("--port", type=int, required=True)
ap.add_argument("--transport", choices=["streamable-http", "sse"], default="streamable-http")
a = ap.parse_args()

mcp = FastMCP("status", host="127.0.0.1", port=a.port)


@mcp.tool()
def whoami() -> str:
    """Name the configuration this server was started from."""
    return f"status server: {a.label}"


@mcp.resource("status://summary")
def summary() -> str:
    """One-line health summary."""
    return f"summary from {a.label}: checkout green, search green, billing degraded"


@mcp.prompt()
def incident_brief(service: str) -> str:
    """Start an incident brief for a service."""
    return f"Write an incident brief for {service}: impact, timeline, next update in 30 minutes."


mcp.run(transport=a.transport)
EOF
python3 -c 'import mcp.server.fastmcp' && echo 'mcp package OK' || echo 'mcp package missing - run setup/claude-code-mastery/install-tools.sh'
```

## What to build

Three people configured a `status` server three different ways. Prove which one Claude Code really talks to.

1. Start three copies in the background and record each PID in `servers.pid`: label `team` on port 8331 (HTTP), label `personal` on port 8332 with `--transport sse`, label `user` on port 8333 (HTTP).
2. Register all three under the **same name** `status`: the team one at **project** scope (`http://127.0.0.1:8331/mcp`), the personal one at **local** scope over **SSE** (`http://127.0.0.1:8332/sse`), the user one at **user** scope (`http://127.0.0.1:8333/mcp`). Approve the project server for yourself and trust the folder.
3. Save `claude mcp get status` as `get-local.txt`.
4. Run `claude -p 'Call the status whoami tool and reply with exactly what it returned.'` (allowing only `mcp__status__whoami`, JSON output) as `run-local.json`. Remove the local entry and run it again as `run-project.json`.
5. With the project server in force, save `resource.json` from `claude -p 'Read the status://summary resource from the status server and reply with its text.'` and `brief.json` from `claude -p '/mcp__status__incident_brief checkout'`.
6. Remove the project entry and run the whoami prompt a third time as `run-user.json`. Then remove the user entry and stop the three servers.

The checker reads which label each run's `whoami` returned.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Same name, different scopes: local, then project, then user.
- Quote prompts with single quotes so the shell leaves them alone.

</details>

<details><summary>Solution</summary>

```bash
cd /root/mastery/033-remote
python3 status_server.py --label team --port 8331 > logs/team.log 2>&1 & echo $! >> servers.pid
python3 status_server.py --label personal --port 8332 --transport sse > logs/personal.log 2>&1 & echo $! >> servers.pid
python3 status_server.py --label user --port 8333 > logs/user.log 2>&1 & echo $! >> servers.pid
sleep 3
for s in local project user; do claude mcp remove --scope $s status >/dev/null 2>&1 || true; done
claude mcp add --scope project --transport http status http://127.0.0.1:8331/mcp
claude mcp add --scope local --transport sse status http://127.0.0.1:8332/sse
claude mcp add --scope user --transport http status http://127.0.0.1:8333/mcp
mkdir -p .claude && echo '{"enabledMcpjsonServers": ["status"]}' > .claude/settings.local.json
[ -f ~/.claude.json ] || echo '{}' > ~/.claude.json
tmp=$(mktemp) && jq --arg p "$(pwd -P)" '.projects[$p].hasTrustDialogAccepted = true' ~/.claude.json > "$tmp" && mv "$tmp" ~/.claude.json
claude mcp get status > get-local.txt
claude -p 'Call the status whoami tool and reply with exactly what it returned.' --allowedTools mcp__status__whoami --output-format json > run-local.json
claude mcp remove --scope local status
claude -p 'Call the status whoami tool and reply with exactly what it returned.' --allowedTools mcp__status__whoami --output-format json > run-project.json
claude -p 'Read the status://summary resource from the status server and reply with its text.' --output-format json > resource.json
claude -p '/mcp__status__incident_brief checkout' --output-format json > brief.json
claude mcp remove --scope project status
claude -p 'Call the status whoami tool and reply with exactly what it returned.' --allowedTools mcp__status__whoami --output-format json > run-user.json
claude mcp remove --scope user status
kill $(cat servers.pid)
wait 2>/dev/null
cat get-local.txt
```

</details>

## Check your work

```bash
D=/root/mastery/033-remote; cd $D 2>/dev/null || echo "❌ create $D (run Set up)"
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
def run_rows(p):
    f, rows = transcript((load(p) or {}).get("session_id") or "none")
    return rows

def label(p):
    rows = run_rows(p)
    got = [rtext(b) for b in result_for(rows, lambda u: u.get("name") == "mcp__status__whoami")]
    return (got or ["(no whoami call)"])[-1]
g = text("get-local.txt")
ok("Local config" in g and re.search(r"Type:\s*sse", g), "claude mcp get showed the local SSE definition in force while all three existed",
   "save claude mcp get status as get-local.txt while the local, project, and user servers are all registered")
srv = ((load(".mcp.json") or {}).get("mcpServers") or {})
ok("status" not in srv, ".mcp.json no longer has status - you removed the project entry at the end", "remove the project-scope server after the project run")
for f_, want, why in [("run-local.json", "personal", "local beats project and user"), ("run-project.json", "team", "with local removed, project wins"),
                      ("run-user.json", "user", "with local and project removed, user is left")]:
    got = label(f_)
    ok(f"status server: {want}" in got, f"{f_}: the call reached the {want} server ({why})", f"{f_} should show whoami returning 'status server: {want}' - got {got[:80]!r}")
rr = [rtext(b) for b in result_for(run_rows("resource.json"), lambda u: u.get("name") == "ReadMcpResourceTool")]
ok(rr and "summary from team" in rr[-1], "Claude read the status://summary resource (from the project server)",
   f"resource.json should show ReadMcpResourceTool returning the team server's summary - got {[x[:80] for x in rr]}")
f, rows = transcript((load("brief.json") or {}).get("session_id") or "none")
ok(f and "incident brief for checkout" in text(f), "the MCP prompt ran as /mcp__status__incident_brief checkout", "brief.json should come from claude -p '/mcp__status__incident_brief checkout'")
cfg = load(os.path.expanduser("~/.claude.json")) or {}
ok("status" not in (cfg.get("mcpServers") or {}) and "status" not in (((cfg.get("projects") or {}).get(os.path.realpath(".")) or {}).get("mcpServers") or {}),
   "the user and local entries are cleaned up", "remove the user-scope status server too - a stale user entry follows you into every project")
pids = [int(x) for x in text("servers.pid").split() if x.isdigit()]
def alive(pid):
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False
import time
for _ in range(20):
    if not any(alive(p) for p in pids):
        break
    time.sleep(0.5)
ok(len(pids) == 3 and not any(alive(p) for p in pids), "the three servers you started are stopped", "start three servers, record their PIDs in servers.pid, and kill them at the end")
PYEOF
```

## What you learned

- Remote servers use http (preferred), sse (legacy), or ws; always set type in JSON.
- For one name, the whole entry from the highest scope wins: local, project, user.
- Resources are read with ReadMcpResourceTool in headless runs; MCP prompts run as /mcp__<server>__<prompt>.
