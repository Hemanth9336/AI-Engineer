---
type: task
title: "Fix it: env vars and redacted logs"
minutes: 9
---

## Set up

```bash
mkdir -p /root/harness-lab/24-secrets
cd /root/harness-lab/24-secrets
[ -f leaky_agent.py ] || cat > leaky_agent.py <<'EOF'
"""Stackline's ops assistant - first version. Works, but leaks its key. Usage: python leaky_agent.py "question" """
import json
import os
import sys
import time
from pathlib import Path

from openai import OpenAI

API_KEY = os.environ["OPENAI_API_KEY"]
BASE_URL = os.environ.get("OPENAI_BASE_URL")
HERE = Path(__file__).parent
SYSTEM = f"You are Stackline's ops assistant. If a tool needs auth, use this token: {API_KEY}"
client = OpenAI(api_key=API_KEY, base_url=BASE_URL, max_retries=0)


def log(event, **data):
    with open(HERE / "debug.log", "a") as f:
        f.write(json.dumps({"ts": time.time(), "event": event, **data}) + "\n")


def ask(question):
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": question}]
    log("request", url=BASE_URL, headers={"Authorization": f"Bearer {API_KEY}"}, messages=messages)
    try:
        r = client.chat.completions.create(model="lab-fast", messages=messages)
    except Exception as e:
        (HERE / "crash.txt").write_text(f"{type(e).__name__}: {e}\nenvironment: {dict(os.environ)}\n")
        raise
    answer = r.choices[0].message.content
    log("response", answer=answer)
    return answer


if __name__ == "__main__":
    print(ask(sys.argv[1]))
EOF
```

## What to build

Write `/root/harness-lab/24-secrets/agent.py`, a fixed version of `leaky_agent.py` with the same behavior (`python agent.py "question"`, debug log, crash file):

1. The key is never in code or in the prompt: create the client with `OpenAI()` and let it read the environment. `SYSTEM` has no token.
2. `redact(text)` replaces (a) the value of every environment variable whose name contains `KEY`, `TOKEN`, `SECRET` or `PASSWORD` (values of 8+ characters), and (b) anything shaped like `sk-...` or `Bearer ...`, with `[REDACTED]`.
3. Every line written to `debug.log` and `crash.txt` goes through `redact()`. Don't log headers, and don't dump the environment.
4. The user's question is redacted before it's sent - if someone pastes a key, the model doesn't need it.

```bash
cd /root/harness-lab/24-secrets
rm -f debug.log crash.txt
python agent.py "My token is sk-live-pasted-12345678, why does billing return 502?"
OPENAI_BASE_URL=http://127.0.0.1:9/v1 python agent.py "Is billing healthy?" 2> /dev/null || echo "(crashed, as expected)"
cat debug.log crash.txt
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Redact the final serialized line, not individual fields - then nothing can slip past.
- `OpenAI(max_retries=0)` keeps the crash test fast.

</details>

<details><summary>Solution</summary>

```bash
cd /root/harness-lab/24-secrets
cat > agent.py <<'EOF'
"""Stackline's ops assistant, fixed: the key stays in the environment and logs are redacted."""
import json
import os
import re
import sys
import time
from pathlib import Path

from openai import OpenAI

HERE = Path(__file__).parent
SYSTEM = "You are Stackline's ops assistant. Answer briefly."
SECRET_NAME = re.compile(r"KEY|TOKEN|SECRET|PASSWORD", re.I)
PATTERNS = [re.compile(r"sk-[A-Za-z0-9_-]{8,}"), re.compile(r"(?i)bearer\s+[A-Za-z0-9._-]{8,}")]
client = OpenAI(max_retries=0)


def redact(text):
    for name, value in os.environ.items():
        if SECRET_NAME.search(name) and len(value) >= 8:
            text = text.replace(value, "[REDACTED]")
    for p in PATTERNS:
        text = p.sub("[REDACTED]", text)
    return text


def log(event, **data):
    with open(HERE / "debug.log", "a") as f:
        f.write(redact(json.dumps({"ts": time.time(), "event": event, **data})) + "\n")


def ask(question):
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": redact(question)}]
    log("request", model="lab-fast", messages=messages)
    try:
        r = client.chat.completions.create(model="lab-fast", messages=messages)
    except Exception as e:
        (HERE / "crash.txt").write_text(redact(f"{type(e).__name__}: {e}") + "\n")
        raise
    answer = r.choices[0].message.content
    log("response", answer=answer)
    return answer


if __name__ == "__main__":
    print(ask(sys.argv[1]))

EOF
rm -f debug.log crash.txt
python agent.py "My token is sk-live-pasted-12345678, why does billing return 502?"
OPENAI_BASE_URL=http://127.0.0.1:9/v1 python agent.py "Is billing healthy?" 2> /dev/null || echo "(crashed, as expected)"
cat debug.log crash.txt
```

</details>

## Check your work

```bash
D=/root/harness-lab/24-secrets; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/agent.py 2>/dev/null && [ -s $D/agent.py ] && echo "✅ agent.py reads the key from the environment" || echo "❌ agent.py must not contain a key - let the SDK read it from the environment"
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
import os, shutil, tempfile
sys.path.insert(0, ".")
try:
    os.environ["DEMO_API_KEY"] = "abcd1234efgh5678"
    import agent
    tests = {"token sk-live-abcdefgh123 here": "sk-live-abcdefgh123", "Authorization: Bearer abcdefghijklmnop": "abcdefghijklmnop", "value abcd1234efgh5678": "abcd1234efgh5678"}
    bad = [t for t, secret in tests.items() if secret in agent.redact(t) or "[REDACTED]" not in agent.redact(t)]
    ok(not bad and agent.redact("billing listens on port 8081") == "billing listens on port 8081", "redact() removes key-shaped strings, bearer tokens and secret env values - and leaves other text alone", f"not redacted: {bad}")
    ok("sk-" not in agent.SYSTEM and "API_KEY" not in agent.SYSTEM, "the system prompt has no key in it", "SYSTEM must not contain a key")
except Exception as e:
    ok(False, "", f"agent.py should define redact(text) and SYSTEM - {type(e).__name__}: {e}")
tmp = Path(tempfile.mkdtemp())
shutil.copy("agent.py", tmp)
key = "sk-fake-checker-7f3a9c1e"
with MockModel(["Check the upstream health."]) as m:
    rc, out, err = m.run(["python", str(tmp / "agent.py"), "My token is sk-user-pasted-9988776655, why 502?"], env={"OPENAI_API_KEY": key}, timeout=20)
m.run(["python", str(tmp / "agent.py"), "hi"], env={"OPENAI_API_KEY": key, "OPENAI_BASE_URL": "http://127.0.0.1:9/v1"}, timeout=20)
sent = json.dumps(m.requests[0].get("messages")) if m.requests else ""
ok(rc == 0 and m.requests and key not in sent and "sk-user-pasted" not in sent, "neither the API key nor a pasted key is sent to the model", f"rc {rc}; {err[-150:]}")
leaked = sorted(p.name for p in tmp.iterdir() if p.is_file() and p.suffix != ".py" and (key in p.read_text(errors="ignore") or "sk-user-pasted" in p.read_text(errors="ignore")))
dbg = (tmp / "debug.log").read_text() if (tmp / "debug.log").exists() else ""
ok(not leaked and "[REDACTED]" in dbg and "Check the upstream health." in dbg and (tmp / "crash.txt").exists(), "debug.log and crash.txt are written, redacted, and contain no key", f"files with a key: {leaked}; debug.log has [REDACTED]: {'[REDACTED]' in dbg}")
shutil.rmtree(tmp, ignore_errors=True)
PYEOF
jq -se 'any(.[]; .ok and .api == "chat.completions" and .model == "lab-fast" and (.client | startswith("OpenAI/Python")))' /var/log/ailab/requests.jsonl >/dev/null 2>&1 && echo "✅ your fixed agent called the real lab model" || echo "❌ run agent.py against the gateway"
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Let the SDK read the key from the environment; keep it out of code and prompts.
- Pass every log line through one redact() that knows your secret values and key shapes.
- Redact what users paste, too - the model never needs a key.
