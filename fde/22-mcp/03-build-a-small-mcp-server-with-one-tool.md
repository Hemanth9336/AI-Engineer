---
type: task
title: "Build a small MCP server with one tool"
minutes: 9
---

## Set up

```bash
mkdir -p /root/fde-lab/22-mcp
cd /root/fde-lab/22-mcp
cat > parcels.json <<'EOF'
{
  "MER-55120": {
    "status": "out for delivery",
    "eta": "2026-03-15"
  },
  "MER-60311": {
    "status": "in transit to Leeds hub",
    "eta": "2026-03-17"
  }
}
EOF
python -c "import mcp.server.fastmcp" && echo 'mcp package OK' || echo 'mcp package missing - run the FDE install script from setup/README.md'
```

## What to build

Write `/root/fde-lab/22-mcp/server.py`, an MCP server named `meridian` with one tool:

- `track_parcel(order_id: str) -> dict` with a docstring that says what it does.
- Returns `{"order_id", "status", "eta"}` from `parcels.json` (next to the script), or `{"error": "unknown order"}`.
- Appends one line to `calls.log` (next to the script) for every call: `track_parcel <order_id>`. Don't print to stdout.
- Runs over stdio with `mcp.run()`.

A stdio server waits for a client, so running it by hand just hangs. Test it with the MCP client from the same package:

```bash
cd /root/fde-lab/22-mcp
python - <<'PY'
import asyncio, sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    async with stdio_client(StdioServerParameters(command=sys.executable, args=["server.py"])) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            print([t.name for t in (await s.list_tools()).tools])
            print((await s.call_tool("track_parcel", {"order_id": "MER-55120"})).content[0].text)

asyncio.run(main())
PY
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `HERE = Path(__file__).parent` - the client may start the server from any directory.
- FastMCP turns the dict you return into the tool result's JSON text.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/22-mcp
cat > server.py <<'EOF'
import json
from pathlib import Path

from mcp.server.fastmcp import FastMCP

HERE = Path(__file__).parent
PARCELS = json.loads((HERE / "parcels.json").read_text())
mcp = FastMCP("meridian")


@mcp.tool()
def track_parcel(order_id: str) -> dict:
    """Look up the delivery status of a Meridian order by its order id (like MER-12345)."""
    with open(HERE / "calls.log", "a") as f:
        f.write(f"track_parcel {order_id}\n")
    p = PARCELS.get(order_id.strip().upper())
    return {"order_id": order_id, **p} if p else {"error": "unknown order"}


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
            print((await s.call_tool("track_parcel", {"order_id": "MER-55120"})).content[0].text)

asyncio.run(main())
PY
```

</details>

## Check your work

```bash
D=/root/fde-lab/22-mcp; cd $D 2>/dev/null || echo "❌ create $D"
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
                a = (await s.call_tool("track_parcel", {"order_id": "MER-60311"})).content[0].text
                b = (await s.call_tool("track_parcel", {"order_id": "MER-99999"})).content[0].text
                return tools, a, b
    try:
        tools, a, b = asyncio.run(asyncio.wait_for(probe(), 60))
    except Exception as e:
        tools, a, b = [], str(e), ""
    t = tools[0] if len(tools) == 1 else None
    ok(t is not None and t.name == "track_parcel" and len(t.description or "") >= 20 and "order_id" in t.inputSchema.get("properties", {}) and t.inputSchema.get("required") == ["order_id"], "the server exposes exactly one tool, track_parcel(order_id), with a description", f"expected one tool track_parcel with a docstring and a required order_id - got {[x.name for x in tools]} {a[:200]}")
    try:
        ra, rb = json.loads(a), json.loads(b)
    except ValueError:
        ra, rb = {}, {}
    ok(ra.get("status") == "in transit to Leeds hub" and ra.get("eta") == "2026-03-17" and rb == {"error": "unknown order"}, "track_parcel returns data from parcels.json and an error for unknown orders, even when started from another folder", f"expected the MER-60311 record and {{'error': 'unknown order'}} - got {a[:200]!r} {b[:100]!r}")
    log = Path("calls.log").read_text().split("\n") if Path("calls.log").exists() else []
    ok(log[:2] == ["track_parcel MER-60311", "track_parcel MER-99999"], "every call is logged to calls.log next to the server", f"calls.log should list both calls - got {log[:3]}")
PYEOF
```

## What you learned

- FastMCP builds the tool schema from type hints and the docstring.
- A stdio server talks through stdout - never print to it.
- Test a server with a real MCP client before connecting an AI app to it.
