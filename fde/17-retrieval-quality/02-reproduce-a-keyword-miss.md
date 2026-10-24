---
type: task
title: "Reproduce a keyword miss"
minutes: 9
---

## Set up

```bash
mkdir -p /root/fde-lab/17-retrieval
cd /root/fde-lab/17-retrieval
cat > articles.json <<'EOF'
[
  {
    "id": "a1",
    "title": "Reporting a damaged parcel",
    "text": "Report damage within 7 days of delivery through the claims page. Attach photos of the item and the packaging. Claims are reviewed within 3 working days and approved claims are refunded to the original payment method."
  },
  {
    "id": "a2",
    "title": "Changing a delivery address",
    "text": "You can change the delivery address until the parcel leaves the depot. Open the order in your account and choose Edit address. After dispatch, address changes cost 6 EUR and add one working day."
  },
  {
    "id": "a3",
    "title": "International shipping and customs",
    "text": "International parcels outside the EU need a commercial invoice. Customs checks usually add 2 to 5 working days. Import duties are paid by the receiver unless the sender booked DDP (Delivered Duty Paid)."
  },
  {
    "id": "a4",
    "title": "Support hours",
    "text": "Customer support is open 8:00 to 18:00 CET, Monday to Friday. Urgent pallet issues for business accounts can use the 24/7 operations line."
  },
  {
    "id": "a5",
    "title": "Tracking a parcel",
    "text": "Enter the order id, for example MER-55120, on the tracking page. Status updates appear at every hub scan. If tracking has not changed for 3 working days, contact support."
  },
  {
    "id": "a6",
    "title": "Pallet weight limits",
    "text": "Standard pallets can weigh up to 800 kg and be up to 1.8 m high. Heavier pallets need a freight booking at least 2 working days in advance."
  },
  {
    "id": "a7",
    "title": "Dangerous goods",
    "text": "Lithium batteries, aerosols and flammable liquids are dangerous goods. They need a dangerous goods declaration and can only travel by road, never by air."
  },
  {
    "id": "a8",
    "title": "Invoices and payment terms",
    "text": "Business invoices are issued on the 1st of each month. Payment terms are 30 days. A fuel surcharge applies when the diesel index rises above the contract level."
  },
  {
    "id": "a9",
    "title": "Missed delivery",
    "text": "If nobody is home, the driver leaves a card and tries again the next working day. After two failed attempts the parcel waits at the local depot for 7 days, then returns to the sender."
  },
  {
    "id": "a10",
    "title": "Scanner error codes",
    "text": "Error E-4417 on a handheld scanner means the label barcode is unreadable. Re-print the label from the depot terminal. Error E-2210 means the scanner has lost its network connection."
  },
  {
    "id": "a11",
    "title": "Returns for business customers",
    "text": "Business customers can book a return collection up to 30 days after delivery. Returns of opened goods are accepted only if the original packaging is included."
  },
  {
    "id": "a12",
    "title": "Cold chain shipments",
    "text": "Chilled goods travel in refrigerated trucks between 2 and 8 degrees Celsius. Temperature logs are available on request for every cold chain shipment."
  }
]
EOF
```

## What to build

Write `/root/fde-lab/17-retrieval/miss.py`, used as `python miss.py QUERY TERM`, that prints JSON:

```json
{"query": "Can we get DDP?", "vector_top3": ["a4", "a2", "a3"], "contains_term": ["a3"], "missed": true}
```

- `vector_top3` - the top 3 article ids by cosine similarity (embed `"<title>. <text>"`, as in topic 15).
- `contains_term` - ids of articles whose title or text contains TERM, case-insensitive, in file order.
- `missed` - `true` when the vector **top-1** isn't in `contains_term`.

```bash
cd /root/fde-lab/17-retrieval
python miss.py "Can we get DDP?" DDP
python miss.py "How long do customs checks take?" customs
```

Put the ranking in a function `vector_rank(query)` that returns all ids in order - the next task reuses it.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `term.lower() in (a["title"] + " " + a["text"]).lower()`.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/17-retrieval
cat > vectors.py <<'EOF'
import json
import math
import re
from pathlib import Path

from openai import OpenAI

client = OpenAI()
ARTICLES = json.loads(Path(__file__).with_name("articles.json").read_text())


def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    return dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))


def vector_rank(query):
    vecs = [d.embedding for d in client.embeddings.create(model="lab-embed", input=[f"{a['title']}. {a['text']}" for a in ARTICLES] + [query]).data]
    q = vecs.pop()
    order = sorted(range(len(ARTICLES)), key=lambda i: cosine(vecs[i], q), reverse=True)
    return [ARTICLES[i]["id"] for i in order]

EOF
cat > miss.py <<'EOF'
import json
import sys

from vectors import ARTICLES, vector_rank

query, term = sys.argv[1], sys.argv[2]
ranked = vector_rank(query)
contains = [a["id"] for a in ARTICLES if term.lower() in (a["title"] + " " + a["text"]).lower()]
print(json.dumps({"query": query, "vector_top3": ranked[:3], "contains_term": contains, "missed": ranked[0] not in contains}))
EOF
python miss.py "Can we get DDP?" DDP
python miss.py "How long do customs checks take?" customs
```

</details>

## Check your work

```bash
D=/root/fde-lab/17-retrieval; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/miss.py 2>/dev/null && [ -s $D/miss.py ] && echo "✅ miss.py reads the key from the environment" || echo "❌ miss.py must not contain a key - let the SDK read it from the environment"
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
arts = load("articles.json")
vecs = E([f"{a['title']}. {a['text']}" for a in arts])
def want(q, term):
    qv = E([q])[0]
    ranked = [a["id"] for _, a in sorted(zip([cos(v, qv) for v in vecs], arts), key=lambda x: x[0], reverse=True)]
    contains = [a["id"] for a in arts if term.lower() in (a["title"] + " " + a["text"]).lower()]
    return {"query": q, "vector_top3": ranked[:3], "contains_term": contains, "missed": ranked[0] not in contains}
for q, term, missed in (("Is DDP an option?", "DDP", True), ("Can goods travel in refrigerated trucks?", "refrigerated", False)):
    rc, out, err = run("miss.py", q, term)
    try:
        got = json.loads(out)
    except ValueError:
        got = None
    w = want(q, term)
    ok(got == w, f"'{q}' / {term}: missed is {w['missed']}", f"for '{q}' / {term} expected {w} - got {out[:250]!r} {err[-150:]}")
PYEOF
jq -se 'any(.[]; .ok and .api == "embeddings" and .model == "lab-embed" and (.client | startswith("OpenAI/Python")))' /var/log/ailab/requests.jsonl >/dev/null 2>&1 && echo "✅ the gateway logged your lab-embed calls" || echo "❌ the gateway has no lab-embed call from your script yet"
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Embeddings can miss exact strings - codes, abbreviations, names.
- Reproduce a miss with a real query before fixing anything.
- The failing case becomes the proof that the fix works.
