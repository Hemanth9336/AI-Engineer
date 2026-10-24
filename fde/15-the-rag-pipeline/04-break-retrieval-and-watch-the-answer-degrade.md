---
type: task
title: "Break retrieval and watch the answer degrade"
minutes: 10
---

## Set up

```bash
mkdir -p /root/fde-lab/15-rag
cd /root/fde-lab/15-rag
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

Simulate a retrieval failure. Write `/root/fde-lab/15-rag/broken.py`, used as `python broken.py QUESTION`, that prints JSON:

```json
{"good":   {"sources": [top 3 ids],          "answer": "..."},
 "broken": {"sources": [3 LEAST similar ids], "answer": "..."}}
```

- **good** - the normal pipeline from `rag.py`.
- **broken** - the same prompt, but with the three *least* similar articles, least similar first.

Reuse `rank()` and `answer()` from the previous task (copy them, or import them).

```bash
cd /root/fde-lab/15-rag
python broken.py "How long do customs checks take?"
```

With the wrong sources, a well-grounded prompt should produce `I don't know` rather than an invented answer.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `ranked = rank(q)` then `ranked[:3]` and `ranked[::-1][:3]`.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/15-rag
[ -f ragcore.py ] || cat > ragcore.py <<'EOF'
import json
import math
import sys
from pathlib import Path

from openai import OpenAI

client = OpenAI()
SYSTEM = "Answer the question using only the sources below. If the sources don't contain the answer, reply exactly: I don't know."
ARTICLES = json.loads(Path(__file__).with_name("articles.json").read_text())


def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    return dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))


def embed(texts):
    return [d.embedding for d in client.embeddings.create(model="lab-embed", input=texts).data]


def rank(question):
    vecs = embed([f"{a['title']}. {a['text']}" for a in ARTICLES] + [question])
    q = vecs.pop()
    return sorted(ARTICLES, key=lambda a: cosine(vecs[ARTICLES.index(a)], q), reverse=True)


def answer(question, sources):
    context = "\n".join(f"[{a['id']}] {a['title']}. {a['text']}" for a in sources)
    resp = client.chat.completions.create(
        model="lab-fast",
        temperature=0,
        messages=[{"role": "system", "content": f"{SYSTEM}\n\nSources:\n{context}"}, {"role": "user", "content": question}],
    )
    return resp.choices[0].message.content.strip()

EOF
cat > broken.py <<'EOF'
import json
import sys

from ragcore import answer, rank

q = sys.argv[1]
ranked = rank(q)
result = {}
for name, sources in (("good", ranked[:3]), ("broken", ranked[::-1][:3])):
    result[name] = {"sources": [a["id"] for a in sources], "answer": answer(q, sources)}
print(json.dumps(result, indent=2))
EOF
python broken.py "How long do customs checks take?"
```

</details>

## Check your work

```bash
D=/root/fde-lab/15-rag; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/broken.py 2>/dev/null && [ -s $D/broken.py ] && echo "✅ broken.py reads the key from the environment" || echo "❌ broken.py must not contain a key - let the SDK read it from the environment"
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
q = "How heavy can a standard pallet be?"
qv = E([q])[0]
ranked = [a["id"] for _, a in sorted(zip([cos(v, qv) for v in vecs], arts), key=lambda x: x[0], reverse=True)]
rc, out, err = run("broken.py", q)
try:
    r = json.loads(out)
except ValueError:
    r = {}
g, b = r.get("good") or {}, r.get("broken") or {}
ok(g.get("sources") == ranked[:3] and b.get("sources") == ranked[::-1][:3], "good uses the top 3, broken the 3 least similar", f"expected good {ranked[:3]} and broken {ranked[::-1][:3]} - got {g.get('sources')} and {b.get('sources')} {err[-150:]}")
ok("800" in str(g.get("answer")), "the good answer is right (800 kg)", f"the good answer should say 800 kg - got {g.get('answer')!r}")
ok("i don't know" in str(b.get("answer")).lower(), "with the wrong sources the model says I don't know", f"the broken answer should be I don't know - got {b.get('answer')!r}")
PYEOF
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- RAG fails at ingest, retrieval, prompt or generation - debug left to right.
- Wrong sources plus a grounded prompt should give 'I don't know', not an invention.
- Log retrieved ids and scores so failures can be diagnosed from logs.
