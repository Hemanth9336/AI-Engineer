---
type: task
title: "A prompt that refuses off-source answers"
minutes: 9
---

## Set up

```bash
mkdir -p /root/fde-lab/18-grounding
cd /root/fde-lab/18-grounding
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

Write `/root/fde-lab/18-grounding/grounded.py`, used as `python grounded.py QUESTION`:

1. Retrieve the vector top 3 articles (reuse `vector_rank` - copy `vectors.py` from topic 17 or write it again).
2. Call `lab-fast` at `temperature=0` with a grounding system prompt and the sources, as in the lesson.
3. When the sources don't answer the question, the reply must be **exactly**: `I don't know based on the provided sources.`
4. Print the reply.

```bash
cd /root/fde-lab/18-grounding
python grounded.py "How long does a parcel wait at the depot after two failed deliveries?"
python grounded.py "Who is Meridian's CEO?"
```

The checker asks trap questions: on-topic, plausible, and not in any article.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Write the refusal into the system prompt word for word, and say it must be the whole reply.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/18-grounding
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
cat > grounded.py <<'EOF'
import sys

from vectors import ARTICLES, client, vector_rank

BY_ID = {a["id"]: a for a in ARTICLES}
REFUSE = "I don't know based on the provided sources."
SYSTEM = ("Answer the question using only the sources below. "
          f"If the sources don't contain the answer, reply exactly: {REFUSE} "
          "Do not use outside knowledge, even if you are confident.")


def grounded(question):
    sources = vector_rank(question)[:3]
    context = "\n".join(f"[{i}] {BY_ID[i]['title']}. {BY_ID[i]['text']}" for i in sources)
    resp = client.chat.completions.create(
        model="lab-fast",
        temperature=0,
        messages=[{"role": "system", "content": f"{SYSTEM}\n\nSources:\n{context}"}, {"role": "user", "content": question}],
    )
    return resp.choices[0].message.content.strip()


if __name__ == "__main__":
    print(grounded(sys.argv[1]))

EOF
python grounded.py "How long does a parcel wait at the depot after two failed deliveries?"
python grounded.py "Who is Meridian's CEO?"
```

</details>

## Check your work

```bash
D=/root/fde-lab/18-grounding; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/grounded.py 2>/dev/null && [ -s $D/grounded.py ] && echo "✅ grounded.py reads the key from the environment" || echo "❌ grounded.py must not contain a key - let the SDK read it from the environment"
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
REFUSE = "I don't know based on the provided sources."
for q in ("How much does DDP cost?", "What is the fuel surcharge percentage this month?", "Do you deliver to Iceland?"):
    rc, out, err = run("grounded.py", q)
    ok(rc == 0 and out.strip() == REFUSE, f"trap question '{q}' gets exactly the refusal", f"'{q}' isn't answered by any article - expected exactly {REFUSE!r}, got {out[:200]!r} {err[-150:]}")
rc, out, err = run("grounded.py", "How many days does a parcel wait at the local depot?")
ok(rc == 0 and "7" in out and out.strip() != REFUSE, "a covered question is answered from the sources", f"a covered question should be answered (7 days) - got {out[:200]!r}")
PYEOF
jq -se 'any(.[]; .ok and .api == "chat.completions" and .model == "lab-fast" and (.client | startswith("OpenAI/Python")) and .temperature == 0 and .system)' /var/log/ailab/requests.jsonl >/dev/null 2>&1 && echo "✅ the gateway logged your lab-fast call" || echo "❌ the gateway has no lab-fast call from your script yet"
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Grounding needs three things: 'only the sources', an exact refusal, and no outside knowledge.
- An exact refusal sentence is detectable by code and by evals.
- Test with trap questions - easy questions can't reveal grounding failures.
