---
type: task
title: "Watch a model complete text step by step"
minutes: 8
---

## Set up

```bash
ailab status
mkdir -p /root/fde-lab/03-llms
```

## What to build

Write `/root/fde-lab/03-llms/complete.py`, used as `python complete.py TEXT STEPS`:

1. Start from TEXT. For each step, call `lab-mini` with:
   - a system message: `Continue the user's text. Output only the continuation.`
   - the text so far as the user message
   - `max_tokens=1` and `temperature=0`
2. Append the reply **exactly as returned** (don't strip it - a leading space is part of the token) and print `step N: <text so far>`.
3. Repeat STEPS times.

Then run:

```bash
cd /root/fde-lab/03-llms
python complete.py "The capital of France is" 5 > steps.txt
cat steps.txt
```

Every line should start with the line before it, plus one more token.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `text += resp.choices[0].message.content or ""`.
- `STEPS = int(sys.argv[2])`.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/03-llms
cat > complete.py <<'EOF'
import sys

from openai import OpenAI

client = OpenAI()
text, steps = sys.argv[1], int(sys.argv[2])
for n in range(1, steps + 1):
    resp = client.chat.completions.create(
        model="lab-mini",
        max_tokens=1,
        temperature=0,
        messages=[
            {"role": "system", "content": "Continue the user's text. Output only the continuation."},
            {"role": "user", "content": text},
        ],
    )
    text += resp.choices[0].message.content or ""
    print(f"step {n}: {text}")
EOF
python complete.py "The capital of France is" 5 > steps.txt
cat steps.txt
```

</details>

## Check your work

```bash
D=/root/fde-lab/03-llms; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/complete.py 2>/dev/null && [ -s $D/complete.py ] && echo "✅ complete.py reads the key from the environment" || echo "❌ complete.py must not contain a key - let the SDK read it from the environment"
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
def lines(out):
    return [l.split(": ", 1)[1] if ": " in l else "" for l in out.splitlines() if l.startswith("step ")]
def grows(seq, start):
    prev = start
    for s in seq:
        if not (s.startswith(prev) and len(s) > len(prev)):
            return False
        prev = s
    return True
saved = lines(Path("steps.txt").read_text()) if Path("steps.txt").exists() else []
ok(len(saved) == 5 and grows(saved, "The capital of France is"), "steps.txt shows 5 steps, each one token longer", "steps.txt should hold 5 'step N: ...' lines, each extending the previous one")
before = sum(1 for _ in open("/var/log/ailab/requests.jsonl"))
rc, out, err = run("complete.py", "Once upon a time", "3")
rows = [json.loads(l) for l in open("/var/log/ailab/requests.jsonl")][before:]
got = lines(out)
ok(rc == 0 and len(got) == 3 and grows(got, "Once upon a time"), "a new text and step count work", f"python complete.py 'Once upon a time' 3 should print 3 growing steps - got {out[-200:]!r} {err[-150:]}")
calls = [r for r in rows if r.get("api") == "chat.completions"]
ok(len(calls) == 3 and all(r.get("model") == "lab-mini" and r.get("max_tokens") == 1 and r.get("temperature") == 0 and r.get("system") for r in calls), "one lab-mini call per step, max_tokens 1, temperature 0, with a system message", f"each step should be one lab-mini call with max_tokens=1, temperature=0 and the system message (saw {len(calls)} calls)")
PYEOF
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- A model generates one token at a time; an answer is that loop repeated.
- `max_tokens` caps the loop; a leading space is often part of a token.
- Every token is one more pass through the model - that's why output tokens cost time and money.
