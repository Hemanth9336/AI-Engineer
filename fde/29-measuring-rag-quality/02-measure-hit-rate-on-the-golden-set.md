---
type: task
title: "Measure hit rate on the golden set"
minutes: 9
---

## Set up

`golden.jsonl` has twelve customer-style questions, each with the `source` article that answers it.

```bash
mkdir -p /root/fde-lab/29-rag-quality
cd /root/fde-lab/29-rag-quality
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
cat > golden.jsonl <<'EOF'
{"id": "r01", "question": "My box arrived crushed - how do I claim?", "source": "a1"}
{"id": "r02", "question": "I moved house, can I redirect my parcel?", "source": "a2"}
{"id": "r03", "question": "Do I pay import tax on a parcel from the US?", "source": "a3"}
{"id": "r04", "question": "Is anyone available on Saturday?", "source": "a4"}
{"id": "r05", "question": "Where can I see where my order is?", "source": "a5"}
{"id": "r06", "question": "What's the maximum height for a pallet?", "source": "a6"}
{"id": "r07", "question": "Can I send aerosol cans?", "source": "a7"}
{"id": "r08", "question": "Why is there an extra charge for diesel on my bill?", "source": "a8"}
{"id": "r09", "question": "Nobody was home when the driver came. What now?", "source": "a9"}
{"id": "r10", "question": "My handheld says the barcode can't be read", "source": "a10"}
{"id": "r11", "question": "Can we send back opened goods?", "source": "a11"}
{"id": "r12", "question": "What temperature do chilled shipments travel at?", "source": "a12"}
EOF
```

## What to build

Write `/root/fde-lab/29-rag-quality/hitrate.py`, used as `python hitrate.py GOLDEN`:

- Embed every article as `"<title>. <text>"` **once**, and all questions in one more call.
- For each case, rank articles by cosine similarity to the question.
- Print one JSON line:
  ```json
  {"cases": 12, "hit@1": 0.83, "hit@3": 1.0, "misses": []}
  ```
  `hit@1` and `hit@3` rounded to 2 decimals; `misses` lists case ids whose source isn't in the top 3, in file order. Skip cases with no `source`.

```bash
cd /root/fde-lab/29-rag-quality
python hitrate.py golden.jsonl
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Two embedding calls in total: one for the articles, one for the questions.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/29-rag-quality
cat > hitrate.py <<'EOF'
import json
import math
import sys
from pathlib import Path

from openai import OpenAI

client = OpenAI()
ARTICLES = json.loads(Path(__file__).with_name("articles.json").read_text())


def embed(texts):
    return [d.embedding for d in client.embeddings.create(model="lab-embed", input=texts).data]


def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    return dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))


def hit_rate(cases):
    doc_vecs = embed([f"{a['title']}. {a['text']}" for a in ARTICLES])
    q_vecs = embed([c["question"] for c in cases])
    hit1 = hit3 = 0
    misses = []
    for c, q in zip(cases, q_vecs):
        ranked = [ARTICLES[i]["id"] for i in sorted(range(len(ARTICLES)), key=lambda i: cosine(doc_vecs[i], q), reverse=True)]
        hit1 += ranked[0] == c["source"]
        hit3 += c["source"] in ranked[:3]
        if c["source"] not in ranked[:3]:
            misses.append(c["id"])
    n = len(cases)
    return {"cases": n, "hit@1": round(hit1 / n, 2), "hit@3": round(hit3 / n, 2), "misses": misses}


if __name__ == "__main__":
    cases = [json.loads(l) for l in open(sys.argv[1]) if l.strip()]
    print(json.dumps(hit_rate([c for c in cases if c.get("source")])))

EOF
python hitrate.py golden.jsonl
```

</details>

## Check your work

```bash
D=/root/fde-lab/29-rag-quality; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/hitrate.py 2>/dev/null && [ -s $D/hitrate.py ] && echo "✅ hitrate.py reads the key from the environment" || echo "❌ hitrate.py must not contain a key - let the SDK read it from the environment"
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
cases = [{"id": "q1", "question": "Is the shop open on Sunday?", "source": "a4"},
         {"id": "q2", "question": "Can I fly a pallet of aerosols to Spain?", "source": "a7"},
         {"id": "q3", "question": "Who pays customs duty?", "source": "a3"},
         {"id": "q4", "question": "When will I be invoiced?", "source": "a8"},
         {"id": "q5", "question": "Fridge temperature for food deliveries?", "source": "a12"},
         {"id": "q6", "question": "How do I complain?", "source": "a11"},
         {"id": "q7", "question": "This one has no source", "source": None}]
av = E([f"{a['title']}. {a['text']}" for a in arts])
qv = E([c["question"] for c in cases[:6]])
h1 = h3 = 0
misses = []
for c, q in zip(cases, qv):
    ranked = [a["id"] for _, a in sorted(zip([cos(v, q) for v in av], arts), key=lambda x: x[0], reverse=True)]
    h1 += ranked[0] == c["source"]
    h3 += c["source"] in ranked[:3]
    if c["source"] not in ranked[:3]:
        misses.append(c["id"])
want = {"cases": 6, "hit@1": round(h1 / 6, 2), "hit@3": round(h3 / 6, 2), "misses": misses}
Path("/tmp/g29.jsonl").write_text("".join(json.dumps(c) + "\n" for c in cases))
before = sum(1 for _ in open("/var/log/ailab/requests.jsonl"))
rc, out, err = run("hitrate.py", "/tmp/g29.jsonl")
rows = [json.loads(l) for l in open("/var/log/ailab/requests.jsonl")][before:]
try:
    got = json.loads(out.splitlines()[-1])
except Exception:
    got = None
ok(got == want, f"hit rate on an unseen set matches: {want}", f"on an unseen set expected {want} - got {out[-300:]!r} {err[-200:]}")
emb = [r for r in rows if r.get("api") == "embeddings"]
ok(len(emb) == 2 and sorted(r.get("inputs") for r in emb) == [6, 12], "articles and questions were embedded in two calls", f"expected two embedding calls (12 articles, 6 questions) - got {[r.get('inputs') for r in emb]}")
PYEOF
```

## What you learned

- Measure retrieval separately from generation - they have different fixes.
- hit@k is the share of questions whose source is in the top k; it caps answer quality.
- Hit rate needs only embeddings, so run it on every retrieval change.
