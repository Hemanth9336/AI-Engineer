---
type: task
title: "Add token auth to the tool wrapper"
minutes: 9
---

## Set up

The mock API also serves `GET /v2/orders/<id>`, which requires `Authorization: Bearer <token>`. Set up saved the token in `api-token` (readable only by you) - treat it like a real secret.

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

Move the client to the authenticated v2 endpoint:

1. Update `get_order` in `/root/fde-lab/23-apis/orders_client.py` to call `/v2/orders/<id>` with `Authorization: Bearer <token>`, reading the token from the environment variable `MERIDIAN_API_TOKEN`.
2. If the variable isn't set, raise `RuntimeError("MERIDIAN_API_TOKEN is not set")`.
3. A 401 returns `{"error": "orders API rejected the credentials"}`. Keep the other error handling.
4. The token must not appear in any file you write.

```bash
cd /root/fde-lab/23-apis
export MERIDIAN_API_TOKEN="$(cat api-token)"
python api_tool.py "What's the status of order MER-55120?"
tail -3 api.log        # auth=yes on the v2 requests
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Test the 401 path: `MERIDIAN_API_TOKEN=wrong python -c "from orders_client import get_order; print(get_order('MER-55120'))"`.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/23-apis
cat > orders_client.py <<'EOF'
import os

import httpx

BASE = os.environ.get("MERIDIAN_API_URL", "http://127.0.0.1:4560")


def get_order(order_id):
    token = os.environ.get("MERIDIAN_API_TOKEN")
    if not token:
        raise RuntimeError("MERIDIAN_API_TOKEN is not set")
    try:
        r = httpx.get(f"{BASE}/v2/orders/{order_id}", headers={"Authorization": f"Bearer {token}"}, timeout=5)
    except httpx.HTTPError:
        return {"error": "orders API unreachable"}
    if r.status_code == 404:
        return {"error": "order not found"}
    if r.status_code == 401:
        return {"error": "orders API rejected the credentials"}
    if r.status_code != 200:
        return {"error": f"orders API error {r.status_code}"}
    return r.json()

EOF
[ -f api_tool.py ] || cat > api_tool.py <<'EOF'
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
export MERIDIAN_API_TOKEN="$(cat api-token)"
python api_tool.py "What's the status of order MER-55120?"
tail -3 api.log
```

</details>

## Check your work

```bash
D=/root/fde-lab/23-apis; cd $D 2>/dev/null || echo "❌ create $D"
! grep -rqF "$(cat api-token 2>/dev/null || echo no-token-file)" --include="*.py" --include="*.sh" --include="*.json" --include="*.txt" --include="*.env" . && echo "✅ the token appears in no file you wrote" || echo "❌ a file contains the API token - read it from MERIDIAN_API_TOKEN instead"
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
token = Path("api-token").read_text().strip()
def call(env_token, oid="MER-60311"):
    env = {k: v for k, v in os.environ.items() if k != "MERIDIAN_API_TOKEN"}
    if env_token is not None:
        env["MERIDIAN_API_TOKEN"] = env_token
    r = subprocess.run([sys.executable, "-c", f"from orders_client import get_order; import json; print(json.dumps(get_order({oid!r})))"], capture_output=True, text=True, env=env)
    return r.stdout.strip(), r.stderr
out, err = call(token)
ok(out and json.loads(out) == load("orders.json")["MER-60311"], "with the token set, get_order returns the order", f"with MERIDIAN_API_TOKEN set, get_order should return the order - got {out[:150]!r} {err[-200:]}")
out, err = call(None)
ok("RuntimeError" in err and "MERIDIAN_API_TOKEN is not set" in err, "without the token, get_order raises a clear RuntimeError", f"without MERIDIAN_API_TOKEN expected RuntimeError('MERIDIAN_API_TOKEN is not set') - got {out[:100]!r} {err[-200:]}")
out, err = call("wrong-token")
ok(out and json.loads(out) == {"error": "orders API rejected the credentials"}, "a wrong token returns the credentials error", f"with a wrong token expected {{'error': 'orders API rejected the credentials'}} - got {out[:150]!r} {err[-150:]}")
log = Path("api.log").read_text().splitlines() if Path("api.log").exists() else []
ok(any(l == "GET /v2/orders/MER-60311 auth=yes" for l in log), "the API log shows authenticated v2 requests", "api.log has no authenticated GET /v2/orders request")
env = dict(os.environ, MERIDIAN_API_TOKEN=token)
r = subprocess.run([sys.executable, "api_tool.py", "Can you check on order MER-70413 for Kestrel Foods?"], capture_output=True, text=True, env=env)
ok(r.returncode == 0 and "lost" in r.stdout.lower(), "the assistant still answers through the authenticated API", f"api_tool.py should answer about MER-70413 through v2 - got {r.stdout[-200:]!r} {r.stderr[-200:]}")
PYEOF
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Credentials go in a header added by your code - never in the prompt or the model's view.
- Read secrets from the environment and fail loudly when they're missing.
- Prefer a narrowly scoped service account or the user's own token - never an admin key.
