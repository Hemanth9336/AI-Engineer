---
type: task
title: "Change behavior with a system message"
minutes: 8
---

## Set up

```bash
ailab status
mkdir -p /root/fde-lab/06-api
```

## What to build

Write `/root/fde-lab/06-api/compare.py` that asks `lab-mini` the same question twice, at `temperature=0`:

- **without** a system message: `When can I call support?`
- **with** this system message, and the same user message:
  `You are Meridian Logistics' support assistant. Support hours are 8:00-18:00 CET, Monday to Friday. Answer in one sentence.`

Save `{"without": <reply>, "with": <reply>}` to `compare.json` and print both.

```bash
cd /root/fde-lab/06-api
python compare.py
```

Only the reply with the system message should mention the real hours (8:00-18:00).

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Write one function `ask(messages)` and call it twice with different message lists.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/06-api
cat > compare.py <<'EOF'
import json

from openai import OpenAI

client = OpenAI()
SYSTEM = "You are Meridian Logistics' support assistant. Support hours are 8:00-18:00 CET, Monday to Friday. Answer in one sentence."
QUESTION = "When can I call support?"


def ask(messages):
    resp = client.chat.completions.create(model="lab-mini", temperature=0, messages=messages)
    return resp.choices[0].message.content


result = {
    "without": ask([{"role": "user", "content": QUESTION}]),
    "with": ask([{"role": "system", "content": SYSTEM}, {"role": "user", "content": QUESTION}]),
}
json.dump(result, open("compare.json", "w"), indent=2)
print("without:", result["without"])
print("with:   ", result["with"])
EOF
python compare.py
```

</details>

## Check your work

```bash
D=/root/fde-lab/06-api; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/compare.py 2>/dev/null && [ -s $D/compare.py ] && echo "✅ compare.py reads the key from the environment" || echo "❌ compare.py must not contain a key - let the SDK read it from the environment"
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
r = load("compare.json") or {}
ok(isinstance(r.get("without"), str) and isinstance(r.get("with"), str) and r["with"].strip(), "compare.json holds both replies", "compare.json should hold {\"without\": ..., \"with\": ...}")
ok("18" in (r.get("with") or ""), "the reply with the system message gives the real hours", f"the 'with' reply should mention 8:00-18:00 - got {r.get('with')!r}")
rows = [json.loads(l) for l in open("/var/log/ailab/requests.jsonl")]
mine = [x for x in rows if x.get("api") == "chat.completions" and x.get("model") == "lab-mini" and x.get("temperature") == 0 and x.get("client", "").startswith("OpenAI/Python")]
ok(any(x.get("roles") == ["user"] for x in mine) and any(x.get("roles") == ["system", "user"] for x in mine), "the gateway logged one call without and one with a system message", "make one lab-mini call with only a user message and one with system + user, both at temperature 0")
PYEOF
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- The system message carries the developer's rules and facts; the user message carries the question.
- Without a system message, the model knows nothing about the customer.
- The system prompt is most of the product at a customer - treat it like code.
