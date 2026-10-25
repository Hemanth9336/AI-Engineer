---
type: task
title: "Build an MCP server and register it"
minutes: 12
---

## Set up

`/root/harness-lab/35-mcp/incidents.json` holds three incidents. Each has `internal_notes` that must never reach the model.

```bash
mkdir -p /root/harness-lab/35-mcp/runs
cd /root/harness-lab/35-mcp
cat > incidents.json <<'EOF'
{
  "INC-4502": {
    "title": "Payment webhooks delayed",
    "status": "investigating",
    "severity": "sev2",
    "team": "payments",
    "internal_notes": "Suspect the queue consumer; do not share with customers."
  },
  "INC-4471": {
    "title": "Ledger replica lag",
    "status": "mitigated",
    "severity": "sev1",
    "team": "platform",
    "internal_notes": "Failover done by hand at 02:10."
  },
  "INC-4390": {
    "title": "Notify emails bouncing",
    "status": "resolved",
    "severity": "sev3",
    "team": "messaging",
    "internal_notes": "DNS record fixed."
  }
}
EOF
python -c "import mcp.server.fastmcp" && echo 'mcp package OK' || echo 'mcp package missing - run the install script from setup/README.md'
```

## What to build

1. Write `/root/harness-lab/35-mcp/server.py`, an MCP server named `opsdesk` with two read-only tools:
   - `incident_status(incident_id: str) -> dict` - returns `{"incident_id", "status", "severity", "team"}` for a known id (case-insensitive, stored upper-case) or `{"error": "unknown incident <id>"}`.
   - `list_open_incidents() -> dict` - returns `{"incidents": [{"incident_id", "title", "status"}, ...]}` for every incident that isn't `resolved`, newest id first.
   - Neither returns `internal_notes`. Each call appends a line to `calls.log` next to the script: `incident_status <id>` or `list_open_incidents`. Never print to stdout.
2. Test it with a real MCP client:

```bash
cd /root/harness-lab/35-mcp
python - <<'PY'
import asyncio, sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    async with stdio_client(StdioServerParameters(command=sys.executable, args=["server.py"])) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            print([t.name for t in (await s.list_tools()).tools])
            print((await s.call_tool("incident_status", {"incident_id": "INC-4471"})).content[0].text)
            print((await s.call_tool("list_open_incidents", {})).content[0].text)

asyncio.run(main())
PY
```

3. Register it for the **project** so the whole team gets it, with absolute paths, and look at the file it writes:

```bash
cd /root/harness-lab/35-mcp
claude mcp remove --scope project opsdesk >/dev/null 2>&1 || true
claude mcp add --scope project opsdesk -- "$(command -v python)" /root/harness-lab/35-mcp/server.py
cat .mcp.json
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `HERE = Path(__file__).parent` - the harness may start the server from any folder.
- `sorted(INCIDENTS.items(), reverse=True)` gives newest id first.
- `.mcp.json` is the file you'd commit; `claude mcp list` may show a project server as pending approval until someone trusts it in an interactive session - `claude -p` still loads it.

</details>

<details><summary>Solution</summary>

```bash
cd /root/harness-lab/35-mcp
cat > server.py <<'EOF'
import json
from pathlib import Path

from mcp.server.fastmcp import FastMCP

HERE = Path(__file__).parent
INCIDENTS = json.loads((HERE / "incidents.json").read_text())
mcp = FastMCP("opsdesk")


def log(line):
    with open(HERE / "calls.log", "a") as f:
        f.write(line + "\n")


@mcp.tool()
def incident_status(incident_id: str) -> dict:
    """Get one ops incident's status, severity and owning team by its id (like INC-4471). Read-only."""
    log(f"incident_status {incident_id}")
    key = incident_id.strip().upper()
    inc = INCIDENTS.get(key)
    if not inc:
        return {"error": f"unknown incident {incident_id}"}
    return {"incident_id": key, "status": inc["status"], "severity": inc["severity"], "team": inc["team"]}


@mcp.tool()
def list_open_incidents() -> dict:
    """List the incidents that are not resolved yet, newest id first, with id, title and status. Read-only."""
    log("list_open_incidents")
    rows = [{"incident_id": k, "title": v["title"], "status": v["status"]}
            for k, v in sorted(INCIDENTS.items(), reverse=True) if v["status"] != "resolved"]
    return {"incidents": rows}


if __name__ == "__main__":
    mcp.run()

EOF
python - <<'PY'
import asyncio, sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    async with stdio_client(StdioServerParameters(command=sys.executable, args=["server.py"])) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            print([t.name for t in (await s.list_tools()).tools])
            print((await s.call_tool("incident_status", {"incident_id": "INC-4471"})).content[0].text)
            print((await s.call_tool("list_open_incidents", {})).content[0].text)

asyncio.run(main())
PY
cd /root/harness-lab/35-mcp
claude mcp remove --scope project opsdesk >/dev/null 2>&1 || true
claude mcp add --scope project opsdesk -- "$(command -v python)" /root/harness-lab/35-mcp/server.py
cat .mcp.json
```

</details>

## Check your work

```bash
D=/root/harness-lab/35-mcp; cd $D 2>/dev/null || echo "❌ create $D"
python - <<'PYEOF'
import json, math, os, subprocess, sys
from pathlib import Path
from openai import OpenAI
_C = OpenAI()
sys.excepthook = lambda t, e, tb: print(f"❌ check stopped: {t.__name__}: {e}")
def E(xs):
    return [d.embedding for d in _C.embeddings.create(model="lab-embed", input=xs).data]
def cos(a, b):
    return sum(x * y for x, y in zip(a, b)) / math.sqrt(sum(x * x for x in a) * sum(y * y for y in b))
def ok(cond, good, bad):
    print(("✅ " + good) if cond else ("❌ " + bad))
def load(p):
    try:
        return json.loads(Path(p).read_text())
    except Exception:
        return None
def run(*args, cwd=None):
    r = subprocess.run([sys.executable, *args], capture_output=True, text=True, cwd=cwd)
    return r.returncode, r.stdout.strip(), r.stderr.strip()
sys.path.insert(0, '/opt/harness')
from labmock import MockModel
import asyncio
if not Path("server.py").exists():
    print("❌ write server.py")
else:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    Path("calls.log").unlink(missing_ok=True)
    async def probe():
        async with stdio_client(StdioServerParameters(command=sys.executable, args=[str(Path("server.py").resolve())], cwd="/tmp")) as (r, w):
            async with ClientSession(r, w) as s:
                await s.initialize()
                tools = (await s.list_tools()).tools
                out = []
                for name, args in (("incident_status", {"incident_id": "inc-4502"}), ("incident_status", {"incident_id": "INC-9"}), ("list_open_incidents", {})):
                    out.append((await s.call_tool(name, args)).content[0].text)
                return tools, out
    try:
        tools, out = asyncio.run(asyncio.wait_for(probe(), 60))
    except Exception as e:
        tools, out = [], [str(e), "", ""]
    by = {t.name: t for t in tools}
    st = by.get("incident_status")
    ok(sorted(by) == ["incident_status", "list_open_incidents"] and all(len(t.description or "") >= 20 for t in tools) and st and st.inputSchema.get("required") == ["incident_id"], "the server exposes incident_status(incident_id) and list_open_incidents, both described", f"expected two described tools - got {sorted(by)} {out[0][:200]}")
    try:
        a, b, c = (json.loads(x) for x in out)
    except ValueError:
        a, b, c = {}, {}, {}
    ok(a == {"incident_id": "INC-4502", "status": "investigating", "severity": "sev2", "team": "payments"} and b == {"error": "unknown incident INC-9"}, "incident_status returns the trimmed record (case-insensitive) and an error for unknown ids", f"incident_status('inc-4502') / ('INC-9') - got {out[0][:200]!r} {out[1][:100]!r}")
    ok(c == {"incidents": [{"incident_id": "INC-4502", "title": "Payment webhooks delayed", "status": "investigating"}, {"incident_id": "INC-4471", "title": "Ledger replica lag", "status": "mitigated"}]}, "list_open_incidents returns the two unresolved incidents, newest first", f"list_open_incidents - got {out[2][:300]!r}")
    ok(not any("internal" in x or "Failover" in x or "queue consumer" in x for x in out), "no result leaks internal_notes", "a tool result contains internal_notes - return only the fields the model needs")
    log = Path("calls.log").read_text().splitlines() if Path("calls.log").exists() else []
    ok(log == ["incident_status inc-4502", "incident_status INC-9", "list_open_incidents"], "every call is logged to calls.log next to the server", f"calls.log should list the three calls - got {log}")
cfg = (load(".mcp.json") or {}).get("mcpServers", {}).get("opsdesk", {})
args = cfg.get("args") or []
ok(cfg.get("command", "").startswith("/") and Path(cfg.get("command", "")).exists() and args and args[-1].startswith("/") and Path(args[-1]).resolve() == Path("server.py").resolve(), ".mcp.json registers opsdesk for the project with an absolute python and server path", f"register with claude mcp add --scope project opsdesk -- \"$(command -v python)\" $PWD/server.py - .mcp.json has {cfg}")
PYEOF
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- An MCP server is written once and works in any MCP-capable harness.
- Tool design rules still apply: clear descriptions, trimmed results, errors as results, read-only by default.
- Project scope writes `.mcp.json` - the file you commit so the team shares the server.
