---
type: task
title: "Compare small vs large chunks on one question"
minutes: 9
---

## Set up

```bash
mkdir -p /root/fde-lab/16-chunking
cd /root/fde-lab/16-chunking
cat > shipping-policy.md <<'EOF'
# Meridian Logistics Shipping Policy

## Scope
This policy applies to all parcel and pallet shipments booked through a Meridian business account. Consumer shipments follow the consumer terms on the website.

## Delivery times
Domestic parcels are delivered in 1 to 2 working days. EU parcels take 2 to 4 working days. Pallets are delivered on the booked date in a 4-hour window agreed with the receiver.

## Packaging requirements
Parcels must be packed in a rigid outer box. Fragile items need at least 5 cm of padding on every side. Pallets must be shrink-wrapped and the load must not overhang the pallet edge.

## Damage and loss
Damage must be reported within 7 days of delivery with photos. Lost parcels are confirmed after 10 working days without a tracking update. Compensation is limited to 25 EUR per kilogram unless extra cover was purchased.

## Extra cover
Extra cover raises compensation to the declared value, up to 10,000 EUR per shipment. It costs 1.5 percent of the declared value and must be added when booking.

## Prohibited items
Cash, live animals, weapons and human remains are never accepted. Dangerous goods are accepted only with a declaration and travel by road.

## Complaints
Complaints are acknowledged within 1 working day and answered within 10 working days. Unresolved complaints can be escalated to the customer relations manager.
EOF
```

## What to build

Write `/root/fde-lab/16-chunking/sizes.py`, used as `python sizes.py DOC QUESTION SIZE [SIZE...]`:

1. Split the whole document into words (`text.split()`).
2. For each SIZE, cut consecutive, non-overlapping windows of SIZE words (the last may be shorter), joined with single spaces.
3. Embed the chunks and the question with `lab-embed` and find the top-1 chunk.
4. Print JSON keyed by size: `{"40": {"chunks": N, "top": "<chunk text>", "score": 0.1234}, "200": {...}}` with the score rounded to 4.

```bash
cd /root/fde-lab/16-chunking
python sizes.py shipping-policy.md "How much compensation do I get for a lost parcel?" 40 200
```

Compare the two `top` chunks: which is more precise, and which carries more context?

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `[" ".join(words[i:i + n]) for i in range(0, len(words), n)]`.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/16-chunking
cat > sizes.py <<'EOF'
import json
import math
import sys

from openai import OpenAI

client = OpenAI()


def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    return dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))


words = open(sys.argv[1]).read().split()
question = sys.argv[2]
result = {}
for size in sys.argv[3:]:
    n = int(size)
    chunks = [" ".join(words[i:i + n]) for i in range(0, len(words), n)]
    vecs = [d.embedding for d in client.embeddings.create(model="lab-embed", input=chunks + [question]).data]
    q = vecs.pop()
    best = max(range(len(chunks)), key=lambda i: cosine(vecs[i], q))
    result[size] = {"chunks": len(chunks), "top": chunks[best], "score": round(cosine(vecs[best], q), 4)}
print(json.dumps(result, indent=2))
EOF
python sizes.py shipping-policy.md "How much compensation do I get for a lost parcel?" 40 200
```

</details>

## Check your work

```bash
D=/root/fde-lab/16-chunking; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/sizes.py 2>/dev/null && [ -s $D/sizes.py ] && echo "✅ sizes.py reads the key from the environment" || echo "❌ sizes.py must not contain a key - let the SDK read it from the environment"
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
words = Path("shipping-policy.md").read_text().split()
q = "What does extra cover cost?"
want = {}
for n in (25, 120):
    chunks = [" ".join(words[i:i + n]) for i in range(0, len(words), n)]
    vecs = E(chunks)
    qv = E([q])[0]
    best = max(range(len(chunks)), key=lambda i: cos(vecs[i], qv))
    want[str(n)] = {"chunks": len(chunks), "top": chunks[best], "score": round(cos(vecs[best], qv), 4)}
rc, out, err = run("sizes.py", "shipping-policy.md", q, "25", "120")
try:
    got = json.loads(out)
except ValueError:
    got = {}
for n in ("25", "120"):
    g, w = got.get(n) or {}, want[n]
    ok(g.get("chunks") == w["chunks"] and g.get("top") == w["top"] and abs(g.get("score", 9) - w["score"]) < 0.0006, f"size {n}: {w['chunks']} chunks and the right top chunk", f"size {n}: expected {w['chunks']} chunks, top chunk starting '{w['top'][:50]}' and score {w['score']} - got {str(g)[:200]} {err[-150:]}")
PYEOF
jq -se 'any(.[]; .ok and .api == "embeddings" and .model == "lab-embed" and (.client | startswith("OpenAI/Python")))' /var/log/ailab/requests.jsonl >/dev/null 2>&1 && echo "✅ the gateway logged your lab-embed calls" || echo "❌ the gateway has no lab-embed call from your script yet"
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Small chunks retrieve precisely but lose context; large chunks keep context but dilute the match.
- Overlap protects sentences cut at boundaries.
- Pick a size by measuring on real questions, not by rule of thumb.
