---
type: task
title: "Find the nearest sentence among ten"
minutes: 8
---

## Set up

`sentences.txt` holds ten one-line summaries of Meridian help articles.

```bash
mkdir -p /root/fde-lab/13-embeddings
cd /root/fde-lab/13-embeddings
cat > sentences.txt <<'EOF'
Reporting a damaged parcel. Report damage within 7 days of delivery through the claims page.
Changing a delivery address. You can change the delivery address until the parcel leaves the depot.
International shipping and customs. International parcels outside the EU need a commercial invoice.
Support hours. Customer support is open 8:00 to 18:00 CET, Monday to Friday.
Tracking a parcel. Enter the order id, for example MER-55120, on the tracking page.
Pallet weight limits. Standard pallets can weigh up to 800 kg and be up to 1.8 m high.
Dangerous goods. Lithium batteries, aerosols and flammable liquids are dangerous goods.
Invoices and payment terms. Business invoices are issued on the 1st of each month.
Missed delivery. If nobody is home, the driver leaves a card and tries again the next working day.
Scanner error codes. Error E-4417 on a handheld scanner means the label barcode is unreadable.
EOF
```

## What to build

Write `/root/fde-lab/13-embeddings/nearest.py`, used as `python nearest.py QUERY`:

1. Read the non-empty lines of `sentences.txt` (next to the script).
2. Embed all of them **and** the query in one call.
3. Print the most similar line, then on a second line its score rounded to 3 decimals.

```bash
cd /root/fde-lab/13-embeddings
python nearest.py "my box came smashed"
python nearest.py "can I fly a phone battery to Spain"
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `vecs = E(lines + [query])`, then the query vector is `vecs[-1]`.
- `best = max(range(len(lines)), key=lambda i: cosine(vecs[i], q))`.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/13-embeddings
cat > nearest.py <<'EOF'
import math
import sys
from pathlib import Path

from openai import OpenAI


def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    return dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))


lines = [l.strip() for l in Path(__file__).with_name("sentences.txt").read_text().splitlines() if l.strip()]
vecs = [d.embedding for d in OpenAI().embeddings.create(model="lab-embed", input=lines + [sys.argv[1]]).data]
q = vecs[-1]
best = max(range(len(lines)), key=lambda i: cosine(vecs[i], q))
print(lines[best])
print(round(cosine(vecs[best], q), 3))
EOF
python nearest.py "my box came smashed"
python nearest.py "can I fly a phone battery to Spain"
```

</details>

## Check your work

```bash
D=/root/fde-lab/13-embeddings; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/nearest.py 2>/dev/null && [ -s $D/nearest.py ] && echo "✅ nearest.py reads the key from the environment" || echo "❌ nearest.py must not contain a key - let the SDK read it from the environment"
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
lines = [l.strip() for l in Path("sentences.txt").read_text().splitlines() if l.strip()]
vecs = E(lines)
for q in ("who pays the import tax on my parcel", "the driver came when I was out"):
    qv = E([q])[0]
    best = max(range(len(lines)), key=lambda i: cos(vecs[i], qv))
    rc, out, err = run("nearest.py", q)
    got = out.splitlines()
    ok(rc == 0 and len(got) == 2 and got[0] == lines[best] and abs(float(got[1]) - round(cos(vecs[best], qv), 3)) < 0.0015, f"'{q}' -> {lines[best][:45]}...", f"for '{q}' expected the line '{lines[best]}' and its score - got {out[:200]!r} {err[-150:]}")
PYEOF
jq -se 'any(.[]; .ok and .api == "embeddings" and .model == "lab-embed" and (.client | startswith("OpenAI/Python")))' /var/log/ailab/requests.jsonl >/dev/null 2>&1 && echo "✅ the gateway logged your lab-embed calls" || echo "❌ the gateway has no lab-embed call from your script yet"
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Semantic search: embed documents once, embed the query, rank by cosine similarity.
- It matches meaning across different words.
- Most similar is not always most relevant - keep that in mind for later.
