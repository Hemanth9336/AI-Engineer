---
type: task
title: "Route easy questions to the small model"
minutes: 7
---

## Set up

```bash
mkdir -p /root/fde-lab/33-cost
cd /root/fde-lab/33-cost
cat > questions.txt <<'EOF'
Where is my parcel?
where is my parcel?
When is support open?
Where  is my   PARCEL?
When is support open?
How do I report damage?
EOF
```

## What to build

Write `/root/fde-lab/33-cost/route.py`:

- `pick_model(question)` returns `lab-mini` when the question is **easy**, else `lab-fast`. Easy means: at most **12 words** (words = `re.findall(r"[a-z0-9']+", question.lower())`), at most **one** `?`, and none of these words: `why, compare, explain, dispute, claim, contract, complaint, refund`.
- `answer(question)` calls the chosen model and returns `(model, reply)`.
- `python route.py QUESTION` prints `model: <name>` then the reply. `python route.py --file FILE` answers every line and prints `lab-mini: N/M (P%)`.

```bash
cd /root/fde-lab/33-cost
python route.py "When is support open?"
python route.py "Why was my claim rejected when I sent photos within 7 days?"
python route.py --file questions.txt
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Turn the word list into a set and intersect it with the question's words.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/33-cost
cat > route.py <<'EOF'
import re
import sys

from openai import OpenAI

client = OpenAI()
HARD_WORDS = {'why', 'compare', 'explain', 'dispute', 'claim', 'contract', 'complaint', 'refund'}


def pick_model(question):
    words = re.findall(r"[a-z0-9']+", question.lower())
    easy = len(words) <= 12 and question.count("?") <= 1 and not HARD_WORDS & set(words)
    return "lab-mini" if easy else "lab-fast"


def answer(question):
    model = pick_model(question)
    reply = client.chat.completions.create(
        model=model, temperature=0,
        messages=[{"role": "system", "content": "You are Meridian Logistics' support assistant."}, {"role": "user", "content": question}],
    ).choices[0].message.content
    return model, reply


if __name__ == "__main__":
    if sys.argv[1] == "--file":
        models = [answer(l.strip())[0] for l in open(sys.argv[2]) if l.strip()]
        mini = models.count("lab-mini")
        print(f"lab-mini: {mini}/{len(models)} ({round(100 * mini / len(models))}%)")
    else:
        model, reply = answer(sys.argv[1])
        print(f"model: {model}")
        print(reply)

EOF
python route.py "When is support open?"
python route.py "Why was my claim rejected when I sent photos within 7 days?"
python route.py --file questions.txt
```

</details>

## Check your work

```bash
D=/root/fde-lab/33-cost; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/route.py 2>/dev/null && [ -s $D/route.py ] && echo "✅ route.py reads the key from the environment" || echo "❌ route.py must not contain a key - let the SDK read it from the environment"
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
sys.path.insert(0, ".")
try:
    from route import pick_model
    cases = {"Where is my parcel?": "lab-mini",
             "Can you explain the fuel surcharge?": "lab-fast",
             "Is the depot open? And until when?": "lab-fast",
             "I want to dispute an invoice": "lab-fast",
             "Do you deliver on Saturdays to rural addresses in the north of the country please": "lab-fast",
             "Do you deliver on Saturdays to rural addresses in the north?": "lab-mini",
             "What's the refund window": "lab-fast"}
    wrong = {q: pick_model(q) for q, m in cases.items() if pick_model(q) != m}
    ok(not wrong, "pick_model routes seven unseen questions correctly", f"wrong routes: {wrong}")
except Exception as e:
    print(f"❌ import route failed: {e}")
b = sum(1 for _ in open("/var/log/ailab/requests.jsonl"))
rc, out, err = run("route.py", "Please compare standard and express delivery for pallets")
rows = [json.loads(l) for l in open("/var/log/ailab/requests.jsonl")][b:]
ok(rc == 0 and out.startswith("model: lab-fast") and [r.get("model") for r in rows] == ["lab-fast"], "a hard question went to lab-fast", f"expected one lab-fast call and 'model: lab-fast' - got {[r.get('model') for r in rows]}, {out[:100]!r} {err[-200:]}")
Path("/tmp/q33r.txt").write_text("Where is my parcel?\nWhy is my parcel late?\nWhen is support open?\nHow heavy can a pallet be?\n")
b = sum(1 for _ in open("/var/log/ailab/requests.jsonl"))
rc, out, err = run("route.py", "--file", "/tmp/q33r.txt")
rows = [json.loads(l) for l in open("/var/log/ailab/requests.jsonl")][b:]
ok(rc == 0 and out.strip().endswith("lab-mini: 3/4 (75%)") and [r.get("model") for r in rows].count("lab-mini") == 3, "--file sends 3 of 4 FAQ questions to lab-mini and reports the share", f"expected 'lab-mini: 3/4 (75%)' and three lab-mini calls - got {out[-100:]!r}, {[r.get('model') for r in rows]}")
PYEOF
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Route each request to the cheapest model that can handle it.
- Start with simple, testable rules; move to a classifier or cascade if needed.
- Prove routing on the golden set per slice before claiming the saving.
