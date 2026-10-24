---
type: task
title: "A Python script that answers a question"
minutes: 7
---

## Set up

```bash
ailab status
mkdir -p /root/fde-lab/06-api
```

## What to build

Write `/root/fde-lab/06-api/ask.py`, used as `python ask.py QUESTION`:

1. Create the client with `OpenAI()` - no key in the code.
2. Send QUESTION as a single user message to `lab-mini` with `max_tokens=300` and `temperature=0`.
3. Print **only** the reply text.
4. If no question is given, print `usage: python ask.py QUESTION` and exit with status 1.

```bash
cd /root/fde-lab/06-api
python ask.py "What is a context window?"
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `if len(sys.argv) < 2: print(...); sys.exit(1)`.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/06-api
cat > ask.py <<'EOF'
import sys

from openai import OpenAI

if len(sys.argv) < 2:
    print("usage: python ask.py QUESTION")
    sys.exit(1)
client = OpenAI()
resp = client.chat.completions.create(
    model="lab-mini",
    max_tokens=300,
    temperature=0,
    messages=[{"role": "user", "content": sys.argv[1]}],
)
print(resp.choices[0].message.content)
EOF
python ask.py "What is a context window?"
```

</details>

## Check your work

```bash
D=/root/fde-lab/06-api; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/ask.py 2>/dev/null && [ -s $D/ask.py ] && echo "✅ ask.py reads the key from the environment" || echo "❌ ask.py must not contain a key - let the SDK read it from the environment"
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
rc, out, err = run("ask.py")
ok(rc == 1 and "usage" in out.lower(), "no question prints usage and exits 1", f"with no question, print the usage line and exit 1 (got exit {rc}, {out[:100]!r})")
before = sum(1 for _ in open("/var/log/ailab/requests.jsonl"))
rc, out, err = run("ask.py", "How do customs delays affect parcel delivery times?")
rows = [json.loads(l) for l in open("/var/log/ailab/requests.jsonl")][before:]
ok(rc == 0 and out.strip() != "", "a new question gets a reply", f"python ask.py QUESTION should print the reply - got exit {rc} {err[-200:]}")
call = [r for r in rows if r.get("api") == "chat.completions"]
ok(len(call) == 1 and call[0].get("model") == "lab-mini" and call[0].get("max_tokens") == 300 and call[0].get("temperature") == 0 and call[0].get("roles") == ["user"], "one lab-mini call with max_tokens 300, temperature 0 and a single user message", f"expected one lab-mini call with max_tokens=300, temperature=0 and one user message - saw {[(r.get('model'), r.get('max_tokens'), r.get('temperature'), r.get('roles')) for r in call]}")
PYEOF
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- `OpenAI()` reads the key and base URL from the environment - the same code runs anywhere.
- The reply is `resp.choices[0].message.content`.
- Handle missing input with a clear usage message and a non-zero exit code.
