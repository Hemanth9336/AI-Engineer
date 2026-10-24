---
type: task
title: "Teach a format with examples"
minutes: 7
---

## Set up

```bash
mkdir -p /root/fde-lab/08-prompting
```

## What to build

Write `/root/fde-lab/08-prompting/classify.py`, used as `python classify.py TICKET_TEXT`, that prints exactly one label: `damaged`, `late`, `address`, `billing` or `other`.

- Send a short system message listing the labels, then **at least five few-shot examples** as user/assistant message pairs (one per label), then the real ticket.
- Use `lab-mini` at `temperature=0`.
- Clean the reply (`strip()`, lowercase, drop a trailing full stop). If it still isn't one of the five labels, print `other`.

```bash
cd /root/fde-lab/08-prompting
python classify.py "My order is four days late and nobody answers the phone."
python classify.py "The pallet arrived with the shrink wrap torn and a crate smashed."
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Build the example pairs in a loop: `for text, label in EXAMPLES: messages += [user(text), assistant(label)]`.
- `label = reply.strip().lower().rstrip(".")`.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/08-prompting
cat > classify.py <<'EOF'
import sys

from openai import OpenAI

LABELS = {"damaged", "late", "address", "billing", "other"}
EXAMPLES = [
    ("The box was crushed and two jars broke.", "damaged"),
    ("Tracking has said out for delivery since Monday and it's Thursday now.", "late"),
    ("I was charged twice for the same shipment.", "billing"),
    ("We moved offices, please send it to 14 Dock Road instead.", "address"),
    ("Do you deliver on public holidays?", "other"),
]

messages = [{"role": "system", "content": "Classify the support ticket. Reply with one label only: damaged, late, address, billing, other."}]
for text, label in EXAMPLES:
    messages += [{"role": "user", "content": text}, {"role": "assistant", "content": label}]
messages.append({"role": "user", "content": sys.argv[1]})

resp = OpenAI().chat.completions.create(model="lab-mini", temperature=0, messages=messages)
label = resp.choices[0].message.content.strip().lower().rstrip(".")
print(label if label in LABELS else "other")
EOF
python classify.py "My order is four days late and nobody answers the phone."
python classify.py "The pallet arrived with the shrink wrap torn and a crate smashed."
```

</details>

## Check your work

```bash
D=/root/fde-lab/08-prompting; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/classify.py 2>/dev/null && [ -s $D/classify.py ] && echo "✅ classify.py reads the key from the environment" || echo "❌ classify.py must not contain a key - let the SDK read it from the environment"
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
cases = [("Our invoice shows a fuel surcharge we never agreed to.", "billing"),
         ("Three cartons were soaked and the labels have come off.", "damaged"),
         ("It was promised for Tuesday, today is Friday and still nothing.", "late")]
before = sum(1 for _ in open("/var/log/ailab/requests.jsonl"))
for text, want in cases:
    rc, out, err = run("classify.py", text)
    ok(rc == 0 and out == want, f"'{text[:40]}...' -> {want}", f"'{text[:40]}...' should print exactly {want} - got {out!r} {err[-150:]}")
rows = [json.loads(l) for l in open("/var/log/ailab/requests.jsonl")][before:]
calls = [r for r in rows if r.get("api") == "chat.completions"]
ok(calls and all(r.get("model") == "lab-mini" and r.get("temperature") == 0 and (r.get("roles") or []).count("assistant") >= 5 and (r.get("roles") or [None])[0] == "system" for r in calls), "every call is lab-mini at temperature 0 with a system message and at least five few-shot pairs", "each call should be lab-mini, temperature 0, system first, with at least 5 user/assistant example pairs")
PYEOF
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Few-shot examples teach format and judgement by demonstration.
- Cover every label and include a hard case; real inputs beat invented ones.
- Always clean and validate the label - never trust the raw reply.
