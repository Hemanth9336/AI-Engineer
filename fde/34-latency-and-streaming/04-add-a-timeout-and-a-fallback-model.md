---
type: task
title: "Add a timeout and a fallback model"
minutes: 8
---

## Set up

Set up starts `slow_api.py`: a fake `lab-smart` endpoint on `127.0.0.1:4555` that takes **5 seconds** to answer - like a provider having a bad day.

```bash
mkdir -p /root/fde-lab/34-latency
cd /root/fde-lab/34-latency
cat > slow_api.py <<'EOF'
import json
import os
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

DELAY = float(os.environ.get("SLOW_SECONDS", "5"))


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Length", "2")
        self.end_headers()
        self.wfile.write(b"ok")

    def do_POST(self):
        self.rfile.read(int(self.headers.get("Content-Length", 0)))
        time.sleep(DELAY)
        body = json.dumps({"id": "slow-1", "object": "chat.completion", "created": int(time.time()), "model": "lab-smart",
                           "choices": [{"index": 0, "message": {"role": "assistant", "content": "A slow answer."}, "finish_reason": "stop"}],
                           "usage": {"prompt_tokens": 10, "completion_tokens": 3, "total_tokens": 13}}).encode()
        try:
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass


ThreadingHTTPServer(("127.0.0.1", 4555), H).serve_forever()
EOF
curl -fsS -o /dev/null http://127.0.0.1:4555/health 2>/dev/null || (nohup python slow_api.py > slow_api.out 2>&1 &)
for i in $(seq 1 20); do curl -fsS -o /dev/null http://127.0.0.1:4555/health 2>/dev/null && break; sleep 0.5; done
curl -fsS -o /dev/null http://127.0.0.1:4555/health && echo "  <- a deliberately slow 'lab-smart' endpoint is up on 127.0.0.1:4555"
```

## What to build

Write `/root/fde-lab/34-latency/fallback.py`, used as `python fallback.py QUESTION`:

- A **primary** client whose `base_url` comes from the environment variable `PRIMARY_URL` (default `http://127.0.0.1:4555/v1`), with `timeout=2.0` and `max_retries=0`. It asks `lab-smart`.
- On `APITimeoutError` or `APIConnectionError`, print `[fallback] ...` to stderr and ask `lab-mini` through the normal lab gateway instead.
- Print `model: <model that answered>`, then the answer.

```bash
cd /root/fde-lab/34-latency
time python fallback.py "When is support open?"
PRIMARY_URL="$OPENAI_BASE_URL" python fallback.py "When is support open?"
```

The first run should fall back after about 2 seconds; the second, pointed at the healthy gateway, should answer with `lab-smart`.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- A client created with only `base_url` still reads `OPENAI_API_KEY` from the environment.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/34-latency
cat > fallback.py <<'EOF'
import os
import sys

from openai import APIConnectionError, APITimeoutError, OpenAI

primary = OpenAI(base_url=os.environ.get("PRIMARY_URL", "http://127.0.0.1:4555/v1"), timeout=2.0, max_retries=0)
backup = OpenAI(timeout=20.0)
MESSAGES = [{"role": "system", "content": "You are Meridian Logistics' support assistant."}]


def ask(question):
    messages = MESSAGES + [{"role": "user", "content": question}]
    try:
        resp = primary.chat.completions.create(model="lab-smart", messages=messages)
        return "lab-smart", resp.choices[0].message.content
    except (APITimeoutError, APIConnectionError) as e:
        print(f"[fallback] lab-smart failed ({type(e).__name__}), using lab-mini", file=sys.stderr)
    resp = backup.chat.completions.create(model="lab-mini", messages=messages)
    return "lab-mini", resp.choices[0].message.content


if __name__ == "__main__":
    model, text = ask(sys.argv[1])
    print(f"model: {model}")
    print(text)

EOF
time python fallback.py "When is support open?"
PRIMARY_URL="$OPENAI_BASE_URL" python fallback.py "When is support open?"
```

</details>

## Check your work

```bash
D=/root/fde-lab/34-latency; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/fallback.py 2>/dev/null && [ -s $D/fallback.py ] && echo "✅ fallback.py reads the key from the environment" || echo "❌ fallback.py must not contain a key - let the SDK read it from the environment"
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
import time
b = sum(1 for _ in open("/var/log/ailab/requests.jsonl"))
t = time.time()
r = subprocess.run([sys.executable, "fallback.py", "Where is my parcel?"], capture_output=True, text=True, env={k: v for k, v in os.environ.items() if k != "PRIMARY_URL"})
took = time.time() - t
rows = [json.loads(l) for l in open("/var/log/ailab/requests.jsonl")][b:]
ok(r.returncode == 0 and r.stdout.startswith("model: lab-mini") and "[fallback]" in r.stderr, "the slow primary timed out and lab-mini answered", f"expected 'model: lab-mini' and a [fallback] line - got {r.stdout[:150]!r} {r.stderr[-200:]!r}")
ok(1.5 <= took < 4.5, f"the fallback answer arrived in {took:.1f} s - the 5 s primary was cut off at the timeout", f"took {took:.1f} s - set timeout=2.0 and max_retries=0 on the primary client")
ok([x.get("model") for x in rows] == ["lab-mini"], "the gateway logged exactly one lab-mini call", f"expected one lab-mini call through the gateway - got {[x.get('model') for x in rows]}")
b = sum(1 for _ in open("/var/log/ailab/requests.jsonl"))
r = subprocess.run([sys.executable, "fallback.py", "Where is my parcel?"], capture_output=True, text=True, env=dict(os.environ, PRIMARY_URL=os.environ["OPENAI_BASE_URL"]))
rows = [json.loads(l) for l in open("/var/log/ailab/requests.jsonl")][b:]
ok(r.returncode == 0 and r.stdout.startswith("model: lab-smart") and "[fallback]" not in r.stderr and [x.get("model") for x in rows] == ["lab-smart"], "with a healthy primary, lab-smart answers and no fallback fires", f"with PRIMARY_URL set to the gateway expected 'model: lab-smart' and no fallback - got {r.stdout[:150]!r} {r.stderr[-200:]!r}")
PYEOF
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Always set an explicit timeout - the SDK default is far too long for users.
- Fall back on timeouts and connection errors, not on bad requests.
- Log, evaluate and test the fallback path like the main one.
