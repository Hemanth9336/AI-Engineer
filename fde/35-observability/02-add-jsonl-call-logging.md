---
type: task
title: "Add JSONL call logging"
minutes: 7
---

## Set up

```bash
mkdir -p /root/fde-lab/35-observability
cd /root/fde-lab/35-observability
rm -f calls.jsonl
```

## What to build

Write `/root/fde-lab/35-observability/logged.py`:

- `chat(messages, model="lab-fast", **kwargs)` calls the API and returns the response, and **always** appends one line to `calls.jsonl` next to the script with: `ts` (UTC, ISO format), `request_id` (a new UUID hex), `model`, `question` (the last user message, at most 200 characters), `ok`, `error` (`None`, or `"<ExceptionType>: <message>"`), `prompt_tokens`, `completion_tokens` (0 on failure) and `latency_ms`.
- On failure, log the line **and** re-raise the exception.
- `python logged.py QUESTION [MODEL]` prints the answer.

```bash
cd /root/fde-lab/35-observability
python logged.py "When is support open?"
python logged.py "When is support open?" lab-does-not-exist
tail -n 2 calls.jsonl
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Write the log line in a `finally:` block so it runs on success and on failure.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/35-observability
cat > logged.py <<'EOF'
import json
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from openai import OpenAI

client = OpenAI()
LOG = Path(__file__).with_name("calls.jsonl")


def chat(messages, model="lab-fast", **kwargs):
    entry = {"ts": datetime.now(timezone.utc).isoformat(timespec="seconds"), "request_id": uuid.uuid4().hex, "model": model,
             "question": next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")[:200]}
    start = time.perf_counter()
    try:
        resp = client.chat.completions.create(model=model, messages=messages, **kwargs)
        entry.update(ok=True, error=None, prompt_tokens=resp.usage.prompt_tokens, completion_tokens=resp.usage.completion_tokens)
        return resp
    except Exception as e:
        entry.update(ok=False, error=f"{type(e).__name__}: {e}"[:300], prompt_tokens=0, completion_tokens=0)
        raise
    finally:
        entry["latency_ms"] = round((time.perf_counter() - start) * 1000)
        with open(LOG, "a") as f:
            f.write(json.dumps(entry) + "\n")


if __name__ == "__main__":
    model = sys.argv[2] if len(sys.argv) > 2 else "lab-fast"
    resp = chat([{"role": "user", "content": sys.argv[1]}], model=model)
    print(resp.choices[0].message.content)

EOF
python logged.py "When is support open?"
python logged.py "When is support open?" lab-does-not-exist || echo "failed as expected"
tail -n 2 calls.jsonl
```

</details>

## Check your work

```bash
D=/root/fde-lab/35-observability; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/logged.py 2>/dev/null && [ -s $D/logged.py ] && echo "✅ logged.py reads the key from the environment" || echo "❌ logged.py must not contain a key - let the SDK read it from the environment"
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
Path("calls.jsonl").unlink(missing_ok=True)
b = sum(1 for _ in open("/var/log/ailab/requests.jsonl"))
rc, out, err = run("logged.py", "Is support open on Saturday?")
gw = [json.loads(l) for l in open("/var/log/ailab/requests.jsonl")][b:]
rows = [json.loads(l) for l in open("calls.jsonl")] if Path("calls.jsonl").exists() else []
r = rows[0] if rows else {}
keys = {"ts", "request_id", "model", "question", "ok", "error", "prompt_tokens", "completion_tokens", "latency_ms"}
ok(rc == 0 and len(rows) == 1 and keys <= set(r), "a successful call wrote one line with every field", f"expected one line with {sorted(keys)} - got {rows} {err[-200:]}")
ok(r.get("ok") is True and r.get("error") is None and r.get("model") == "lab-fast" and r.get("question") == "Is support open on Saturday?" and gw and r.get("prompt_tokens") == gw[-1].get("prompt_tokens") and r.get("completion_tokens") == gw[-1].get("completion_tokens"),
   "the line's model, question and token counts match what the gateway saw", f"token counts should come from the response usage - got {r}, gateway {[(x.get('prompt_tokens'), x.get('completion_tokens')) for x in gw]}")
ok(isinstance(r.get("latency_ms"), (int, float)) and r.get("latency_ms", -1) >= 0 and len(str(r.get("request_id", ""))) >= 16 and "T" in str(r.get("ts", "")), "latency, request id and timestamp look right", f"latency_ms should be a number, request_id a UUID hex and ts ISO format - got {r}")
rc, out, err = run("logged.py", "Hello", "lab-nope")
rows = [json.loads(l) for l in open("calls.jsonl")] if Path("calls.jsonl").exists() else []
f = rows[-1] if len(rows) == 2 else {}
ok(rc != 0 and f.get("ok") is False and f.get("model") == "lab-nope" and f.get("error") and f.get("prompt_tokens") == 0, "a failing call is logged with ok false and the error - and still raises", f"with an unknown model expected a non-zero exit and a second line with ok false and an error - got exit {rc}, {rows[-1:] if rows else rows}")
PYEOF
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Wrap every model call so it writes one structured line, success or failure.
- A request id links the call to retrieval, tools and the user's complaint.
- Agree with the customer what text is logged and for how long.
