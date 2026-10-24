---
type: task
title: "Hand-build a minimal RAG script"
minutes: 9
---

## Set up

`articles.json` holds twelve Meridian help articles: `id`, `title` and `text`.

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

Write `/root/fde-lab/15-rag/rag.py`, used as `python rag.py QUESTION`:

1. Embed every article as `"<title>. <text>"` together with the question (one `lab-embed` call), and rank articles by cosine similarity.
2. Take the top **3**.
3. Call `lab-fast` at `temperature=0` with this system message, followed by a blank line, `Sources:` and one line per source as `[id] title. text`:
   ```text
   Answer the question using only the sources below. If the sources don't contain the answer, reply exactly: I don't know.
   ```
   and the question as the user message.
4. Print JSON: `{"answer": "...", "sources": ["a3", "a1", "a5"]}` - source ids in rank order.

```bash
cd /root/fde-lab/15-rag
python rag.py "How long do customs checks take?"
```

Keep `rank()` and `answer()` as functions - the next task reuses them.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `vecs.pop()` takes the question vector off the end of the list.
- Put the sources in the system message after the instructions.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/15-rag
cat > ragcore.py <<'EOF'
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
cat > rag.py <<'EOF'
import json
import sys

from ragcore import answer, rank

sources = rank(sys.argv[1])[:3]
print(json.dumps({"answer": answer(sys.argv[1], sources), "sources": [a["id"] for a in sources]}))
EOF
python rag.py "How long do customs checks take?"
```

</details>

## Check your work

```bash
D=/root/fde-lab/15-rag; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/rag.py 2>/dev/null && [ -s $D/rag.py ] && echo "✅ rag.py reads the key from the environment" || echo "❌ rag.py must not contain a key - let the SDK read it from the environment"
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
def top(q, k=3):
    qv = E([q])[0]
    return [a["id"] for _, a in sorted(zip([cos(v, qv) for v in vecs], arts), key=lambda x: x[0], reverse=True)[:k]]
q = "How heavy can a standard pallet be?"
before = sum(1 for _ in open("/var/log/ailab/requests.jsonl"))
rc, out, err = run("rag.py", q)
rows = [json.loads(l) for l in open("/var/log/ailab/requests.jsonl")][before:]
try:
    r = json.loads(out)
except ValueError:
    r = {}
ok(r.get("sources") == top(q), f"the top-3 sources are {top(q)}", f"sources should be the top 3 article ids {top(q)} - got {r.get('sources')} {err[-200:]}")
ok("800" in str(r.get("answer")), "the answer uses the pallet article (800 kg)", f"the answer should come from the sources (800 kg) - got {r.get('answer')!r}")
chat = [x for x in rows if x.get("api") == "chat.completions"]
ok(len(chat) == 1 and chat[0].get("model") == "lab-fast" and chat[0].get("temperature") == 0 and chat[0].get("roles") == ["system", "user"], "one lab-fast call at temperature 0 with the sources in the system message", f"expected one lab-fast call at temperature 0 with system + user messages - got {[(x.get('model'), x.get('temperature'), x.get('roles')) for x in chat]}")
PYEOF
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- RAG = retrieve the top-k chunks, put them in the prompt, generate.
- 'Only the sources' plus an exact 'I don't know' keeps answers grounded.
- Return source ids with every answer - for citations and debugging.
