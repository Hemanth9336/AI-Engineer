---
type: task
title: "Register your server and call the tool through claude"
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
[ -f server.py ] && echo 'server.py found' || echo 'write server.py first (previous task)'
```

## What to build

1. Register your server with Claude Code at **user** scope, as `meridian`, using absolute paths for both Python and `server.py`.
2. Check that `claude mcp list` shows it as connected.
3. Ask Claude Code, allowing only that one tool, and save the answer:

```bash
cd /root/fde-lab/22-mcp
claude -p "Where is order MER-55120? Use the meridian tool." --allowedTools mcp__meridian__track_parcel > answer.txt
cat answer.txt
tail -3 calls.log
```

`calls.log` proves the answer came through your server, not from the model's imagination.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `claude mcp add --scope user meridian -- "$(command -v python)" /root/fde-lab/22-mcp/server.py`.
- If it shows as failed, run the same command yourself - an import error in `server.py` is the usual cause.
- Re-registering? Run `claude mcp remove --scope user meridian` first.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/22-mcp
[ -f server.py ] || cat > server.py <<'EOF'
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
claude mcp remove --scope user meridian >/dev/null 2>&1 || true
claude mcp add --scope user meridian -- "$(command -v python)" /root/fde-lab/22-mcp/server.py
claude mcp list
claude -p "Where is order MER-55120? Use the meridian tool." --allowedTools mcp__meridian__track_parcel > answer.txt
cat answer.txt
tail -3 calls.log
```

</details>

## Check your work

```bash
D=/root/fde-lab/22-mcp; cd $D 2>/dev/null || echo "❌ create $D"
claude mcp list 2>/dev/null | grep -q "^meridian:.*Connected" && echo "✅ claude mcp list shows meridian connected" || echo "❌ register the server as meridian (claude mcp add --scope user ...) and make sure it connects"
grep -qi "MER-55120" answer.txt 2>/dev/null && grep -qi "delivery" answer.txt && echo "✅ answer.txt holds the answer about MER-55120" || echo "❌ save claude's answer about MER-55120 to answer.txt"
grep -q "track_parcel MER-55120" calls.log 2>/dev/null && echo "✅ calls.log shows the server handled MER-55120" || echo "❌ calls.log has no call for MER-55120 - the tool was not called through your server"
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
before = Path("calls.log").read_text().count("MER-60311") if Path("calls.log").exists() else 0
r = subprocess.run(["claude", "-p", "What's the status of order MER-60311? Use the meridian tool.", "--allowedTools", "mcp__meridian__track_parcel"], capture_output=True, text=True, timeout=240)
after = Path("calls.log").read_text().count("MER-60311") if Path("calls.log").exists() else 0
ok(r.returncode == 0 and after > before and "leeds" in r.stdout.lower(), "a new question about MER-60311 went through your server and the answer uses its data", f"claude should call your server for MER-60311 and answer from it - calls {before}->{after}, answer {r.stdout[-200:]!r} {r.stderr[-200:]}")
rows = [json.loads(l) for l in open("/var/log/ailab/requests.jsonl")]
ok(any(x.get("client", "").startswith("claude-cli") and "mcp__meridian__track_parcel" in (x.get("tool_calls") or []) for x in rows), "the gateway logged claude calling mcp__meridian__track_parcel", "no claude request that called mcp__meridian__track_parcel")
PYEOF
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Register stdio servers with absolute paths for the interpreter and the script.
- Claude Code names MCP tools `mcp__<server>__<tool>`.
- Allow only the tools a task needs; check the server's own log to prove the path.
