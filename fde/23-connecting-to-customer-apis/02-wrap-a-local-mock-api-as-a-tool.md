---
type: task
title: "Wrap a local mock API as a tool"
minutes: 9
---

## Set up

Set up starts a mock of Meridian's orders API on `127.0.0.1:4560`. `GET /v1/orders/<id>` needs no authentication.

```bash
mkdir -p /root/fde-lab/23-apis
cd /root/fde-lab/23-apis
cat > orders.json <<'EOF'
{
  "MER-55120": {
    "order_id": "MER-55120",
    "status": "out for delivery",
    "eta": "2026-03-15",
    "customer": "Harbor Foods"
  },
  "MER-60311": {
    "order_id": "MER-60311",
    "status": "in transit to Leeds hub",
    "eta": "2026-03-17",
    "customer": "Dockside Retail"
  },
  "MER-70413": {
    "order_id": "MER-70413",
    "status": "lost - investigation open",
    "eta": null,
    "customer": "Kestrel Foods"
  }
}
EOF
echo mrd_demo_7f3a9c2e41b8 > api-token && chmod 600 api-token
cat > mock_api.py <<'EOF'
import json
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).parent
ORDERS = json.loads((HERE / "orders.json").read_text())
TOKEN = (HERE / "api-token").read_text().strip()


class H(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        auth = "yes" if self.headers.get("Authorization") == f"Bearer {TOKEN}" else "no"
        with open(HERE / "api.log", "a") as f:
            f.write(f"{self.command} {self.path} auth={auth}\n")

    def reply(self, code, obj):
        data = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/health":
            return self.reply(200, {"ok": True})
        m = re.fullmatch(r"/(v1|v2)/orders/([A-Za-z0-9-]+)", self.path)
        if not m:
            return self.reply(404, {"error": "not found"})
        if m[1] == "v2" and self.headers.get("Authorization") != f"Bearer {TOKEN}":
            return self.reply(401, {"error": "unauthorized"})
        order = ORDERS.get(m[2].upper())
        return self.reply(200, order) if order else self.reply(404, {"error": "order not found"})


ThreadingHTTPServer(("127.0.0.1", 4560), H).serve_forever()
EOF
curl -fsS -o /dev/null http://127.0.0.1:4560/health 2>/dev/null || (nohup python mock_api.py > mock_api.out 2>&1 &)
for i in $(seq 1 20); do curl -fsS -o /dev/null http://127.0.0.1:4560/health 2>/dev/null && break; sleep 0.5; done
curl -fsS http://127.0.0.1:4560/health && echo "  <- mock orders API is up on 127.0.0.1:4560"
```

## What to build

1. Explore the API first:
   ```bash
   curl -s http://127.0.0.1:4560/v1/orders/MER-55120; echo
   curl -s -w ' HTTP %{http_code}' http://127.0.0.1:4560/v1/orders/MER-00000; echo
   ```
2. Write `/root/fde-lab/23-apis/orders_client.py` with `get_order(order_id)` as in the lesson: base URL from `MERIDIAN_API_URL` (default `http://127.0.0.1:4560`), 5-second timeout, `{"error": "order not found"}` on 404, `{"error": "orders API error <code>"}` on other failures, `{"error": "orders API unreachable"}` when the connection fails.
3. Write `api_tool.py`, used as `python api_tool.py QUESTION`: a tool loop on `lab-fast` with one tool, `get_order`, that calls your client.

```bash
cd /root/fde-lab/23-apis
python api_tool.py "What's the status of order MER-55120?"
tail -3 api.log
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `httpx.HTTPError` covers connection errors and timeouts.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/23-apis
curl -s http://127.0.0.1:4560/v1/orders/MER-55120; echo
cat > orders_client.py <<'EOF'
import os

import httpx

BASE = os.environ.get("MERIDIAN_API_URL", "http://127.0.0.1:4560")


def get_order(order_id):
    try:
        r = httpx.get(f"{BASE}/v1/orders/{order_id}", timeout=5)
    except httpx.HTTPError:
        return {"error": "orders API unreachable"}
    if r.status_code == 404:
        return {"error": "order not found"}
    if r.status_code != 200:
        return {"error": f"orders API error {r.status_code}"}
    return r.json()

EOF
cat > api_tool.py <<'EOF'
import json
import sys

from openai import OpenAI

from orders_client import get_order

TOOL = {"type": "function", "function": {
    "name": "get_order",
    "description": "Get a Meridian order's status, ETA and customer from the orders API, by order id like MER-12345.",
    "parameters": {"type": "object", "properties": {"order_id": {"type": "string"}}, "required": ["order_id"]}}}

client = OpenAI()
messages = [{"role": "user", "content": sys.argv[1]}]
while True:
    msg = client.chat.completions.create(model="lab-fast", tools=[TOOL], messages=messages).choices[0].message
    if not msg.tool_calls:
        print(msg.content)
        break
    messages.append(msg)
    for call in msg.tool_calls:
        args = json.loads(call.function.arguments)
        result = get_order(**args) if call.function.name == "get_order" else {"error": "unknown tool"}
        messages.append({"role": "tool", "tool_call_id": call.id, "content": json.dumps(result)})

EOF
python api_tool.py "What's the status of order MER-55120?"
tail -3 api.log
```

</details>

## Check your work

```bash
D=/root/fde-lab/23-apis; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/api_tool.py 2>/dev/null && [ -s $D/api_tool.py ] && echo "✅ api_tool.py reads the key from the environment" || echo "❌ api_tool.py must not contain a key - let the SDK read it from the environment"
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
sys.path.insert(0, ".")
try:
    import orders_client as oc
except Exception as e:
    oc = None
    print(f"❌ import orders_client failed: {e}")
if oc:
    ok(oc.get_order("MER-60311") == load("orders.json")["MER-60311"], "get_order returns the API's JSON for a known order", f"get_order('MER-60311') should return the API response - got {oc.get_order('MER-60311')}")
    ok(oc.get_order("MER-00000") == {"error": "order not found"}, "a 404 becomes {'error': 'order not found'}", f"get_order('MER-00000') should return {{'error': 'order not found'}} - got {oc.get_order('MER-00000')}")
    env = dict(os.environ, MERIDIAN_API_URL="http://127.0.0.1:4599")
    r = subprocess.run([sys.executable, "-c", "from orders_client import get_order; print(get_order('MER-55120'))"], capture_output=True, text=True, env=env)
    ok(r.stdout.strip() == "{'error': 'orders API unreachable'}", "MERIDIAN_API_URL is honoured and a dead API returns an error result", f"with MERIDIAN_API_URL pointing at a closed port, expected {{'error': 'orders API unreachable'}} - got {r.stdout[-150:]!r} {r.stderr[-150:]}")
before = Path("api.log").read_text().count("/v1/orders/MER-70413") if Path("api.log").exists() else 0
rc, out, err = run("api_tool.py", "Can you check on order MER-70413 for Kestrel Foods?")
after = Path("api.log").read_text().count("/v1/orders/MER-70413") if Path("api.log").exists() else 0
ok(rc == 0 and after > before and "lost" in out.lower(), "the assistant called the API for MER-70413 and answered from it", f"api_tool.py should call /v1/orders/MER-70413 and answer from the result - api calls {before}->{after}, answer {out[:200]!r} {err[-200:]}")
PYEOF
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- A REST tool wrapper needs timeouts, status-code handling and errors returned as results.
- Keep the HTTP client separate from the AI code - testable and reusable.
- Call the real endpoint yourself before trusting the docs.
