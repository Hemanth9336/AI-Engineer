---
type: task
title: "Trigger and observe a hallucination"
minutes: 8
---

## Set up

```bash
ailab status
mkdir -p /root/fde-lab/03-llms
```

## What to build

The Meridian X200 pallet scanner doesn't exist. Ask about it anyway.

Write `/root/fde-lab/03-llms/hallucinate.py` that:

1. Asks `lab-mini` **three times**, at `temperature=1.0`, with no system message: `What is the warranty period for the Meridian X200 pallet scanner?` Save the three replies as a JSON list of strings in `runs.json`.
2. Asks once more at `temperature=0` with this system message, and saves the reply in `abstain.txt`:
   `Answer only if you are certain the product exists and you know the fact. Otherwise reply exactly: I don't know.`

Run it, read `runs.json`, and write one word to `verdict.txt`: `hallucinated` if any run invented a warranty, or `abstained` if every run said it didn't know.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Use a loop for the three runs: `[ask(q, temperature=1.0) for _ in range(3)]`.
- Compare the three runs: invented details tend to change between runs.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/03-llms
cat > hallucinate.py <<'EOF'
import json

from openai import OpenAI

client = OpenAI()
QUESTION = "What is the warranty period for the Meridian X200 pallet scanner?"
ABSTAIN = "Answer only if you are certain the product exists and you know the fact. Otherwise reply exactly: I don't know."


def ask(messages, temperature):
    resp = client.chat.completions.create(model="lab-mini", temperature=temperature, messages=messages)
    return resp.choices[0].message.content.strip()


runs = [ask([{"role": "user", "content": QUESTION}], 1.0) for _ in range(3)]
json.dump(runs, open("runs.json", "w"), indent=2)
abstain = ask([{"role": "system", "content": ABSTAIN}, {"role": "user", "content": QUESTION}], 0)
open("abstain.txt", "w").write(abstain + "\n")
for r in runs:
    print("-", r)
print("with permission to abstain:", abstain)
EOF
python hallucinate.py
python - > verdict.txt <<'EOF'
import json
runs = json.load(open("runs.json"))
print("abstained" if all("don't know" in r.lower() for r in runs) else "hallucinated")
EOF
cat verdict.txt
```

</details>

## Check your work

```bash
D=/root/fde-lab/03-llms; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/hallucinate.py 2>/dev/null && [ -s $D/hallucinate.py ] && echo "✅ hallucinate.py reads the key from the environment" || echo "❌ hallucinate.py must not contain a key - let the SDK read it from the environment"
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
runs = load("runs.json")
ok(isinstance(runs, list) and len(runs) == 3 and all(isinstance(r, str) and r.strip() for r in runs), "runs.json holds three replies", "runs.json should be a JSON list of the three replies")
v = Path("verdict.txt").read_text().strip() if Path("verdict.txt").exists() else ""
want = "abstained" if runs and all("don't know" in r.lower() for r in runs) else "hallucinated"
ok(v == want, f"verdict.txt correctly says {want}", f"verdict.txt should say {want} for the replies in runs.json (got {v!r})")
ok(Path("abstain.txt").exists() and Path("abstain.txt").read_text().strip() != "", "abstain.txt holds the reply with permission to abstain", "save the temperature-0 reply with the abstain system message to abstain.txt")
rows = [json.loads(l) for l in open("/var/log/ailab/requests.jsonl")]
mine = [r for r in rows if r.get("api") == "chat.completions" and r.get("model") == "lab-mini" and r.get("client", "").startswith("OpenAI/Python")]
ok(sum(1 for r in mine if r.get("temperature") == 1.0 and not r.get("system")) >= 3, "three temperature-1.0 calls without a system message", "make three lab-mini calls at temperature=1.0 with no system message")
ok(any(r.get("temperature") == 0 and r.get("system") for r in mine), "one temperature-0 call with the abstain system message", "make one lab-mini call at temperature=0 with the abstain system message")
PYEOF
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Ask about something that doesn't exist and a model may still produce a fluent answer.
- Details that change between runs at higher temperature are a hallucination warning sign.
- An explicit, allowed 'I don't know' gives the model a better continuation than guessing.
