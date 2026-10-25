---
type: task
title: "Find the leak: a harness that logs its own API key"
minutes: 9
---

## Set up

`leaky_agent.py` is the first version of Stackline's ops assistant. It works - and leaks its key in several ways.

```bash
mkdir -p /root/harness-lab/24-secrets
cd /root/harness-lab/24-secrets
cat > leaky_agent.py <<'EOF'
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

1. Run it with a **fake key** against labmock, then again against a closed port to trigger its error path, and search for the key:

```bash
cd /root/harness-lab/24-secrets
rm -f debug.log crash.txt
echo '["The billing service is healthy."]' > mock.json
python /opt/harness/labmock.py mock.json --port 4598 > /dev/null &
MOCK=$!
for i in $(seq 30); do curl -s http://127.0.0.1:4598/v1/models > /dev/null && break; sleep 0.2; done
OPENAI_BASE_URL=http://127.0.0.1:4598/v1 OPENAI_API_KEY=sk-fake-leakcheck-0000 python leaky_agent.py "Is billing healthy?"
kill $MOCK
OPENAI_BASE_URL=http://127.0.0.1:9/v1 OPENAI_API_KEY=sk-fake-leakcheck-0000 python leaky_agent.py "Is billing healthy?" 2> /dev/null || echo "(crashed, as expected)"
grep -rl sk-fake-leakcheck-0000 . 
```

2. Read `leaky_agent.py` and the files it wrote. Write `/root/harness-lab/24-secrets/leaks.json`:

```json
{"files": ["..."], "sent_to_model": true}
```

- `files`: every file the run wrote that contains the key, sorted by name.
- `sent_to_model`: whether the key was also sent **to the model** as part of the messages.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Look at `SYSTEM`, at what `log()` writes for a request, and at the `except` branch.
- `grep -rl KEY .` lists the files - leave out `leaks.json` itself.

</details>

<details><summary>Solution</summary>

```bash
cd /root/harness-lab/24-secrets
rm -f debug.log crash.txt
echo '["The billing service is healthy."]' > mock.json
python /opt/harness/labmock.py mock.json --port 4598 > /dev/null &
MOCK=$!
for i in $(seq 30); do curl -s http://127.0.0.1:4598/v1/models > /dev/null && break; sleep 0.2; done
OPENAI_BASE_URL=http://127.0.0.1:4598/v1 OPENAI_API_KEY=sk-fake-leakcheck-0000 python leaky_agent.py "Is billing healthy?"
kill $MOCK
OPENAI_BASE_URL=http://127.0.0.1:9/v1 OPENAI_API_KEY=sk-fake-leakcheck-0000 python leaky_agent.py "Is billing healthy?" 2> /dev/null || echo "(crashed, as expected)"
grep -rl sk-fake-leakcheck-0000 . 
cat > leaks.json <<'EOF'
{"files": ["crash.txt", "debug.log"], "sent_to_model": true}
EOF
```

</details>

## Check your work

```bash
D=/root/harness-lab/24-secrets; cd $D 2>/dev/null || echo "❌ create $D"
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
import shutil, tempfile
ok(Path("debug.log").exists() and Path("crash.txt").exists(), "you ran the leaky agent, including its error path", "run both commands - debug.log and crash.txt should exist")
tmp = Path(tempfile.mkdtemp())
shutil.copy("leaky_agent.py", tmp)
key = "sk-fake-checker-7f3a9c1e"
with MockModel(["fine"]) as m:
    m.run(["python", str(tmp / "leaky_agent.py"), "hi"], env={"OPENAI_API_KEY": key}, timeout=20)
m.run(["python", str(tmp / "leaky_agent.py"), "hi"], env={"OPENAI_API_KEY": key, "OPENAI_BASE_URL": "http://127.0.0.1:9/v1"}, timeout=20)
files = sorted(p.name for p in tmp.iterdir() if p.is_file() and key in p.read_text(errors="ignore") and p.suffix != ".py")
to_model = bool(m.requests) and key in json.dumps(m.requests[0].get("messages"))
shutil.rmtree(tmp, ignore_errors=True)
got = load("leaks.json") or {}
ok(got.get("files") == files, f"leaks.json lists every file that leaked the key: {files}", f"files should be {files} - got {got.get('files')}")
ok(got.get("sent_to_model") is to_model, "leaks.json says whether the key went to the model", f"sent_to_model should be {to_model}")
PYEOF
```

## What you learned

- Keys leak through prompts, tool results, debug logs, crash reports and code.
- Test with a fake key and grep for it - wherever it shows up, a real key would too.
- The model never needs your key; tools authenticate in code.
