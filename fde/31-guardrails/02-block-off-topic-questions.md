---
type: task
title: "Block off-topic questions"
minutes: 9
---

## Set up

`vectors.py` gives you `scored(query)` - a list of `(score, article)` pairs, best first - and the shared `client`.

```bash
mkdir -p /root/fde-lab/31-guardrails
cd /root/fde-lab/31-guardrails
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
cat > vectors.py <<'EOF'
import json
import math
from pathlib import Path

from openai import OpenAI

client = OpenAI()
ARTICLES = json.loads(Path(__file__).with_name("articles.json").read_text())


def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    return dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))


def scored(query, articles=None):
    articles = ARTICLES if articles is None else articles
    vecs = [d.embedding for d in client.embeddings.create(model="lab-embed", input=[f"{a['title']}. {a['text']}" for a in articles] + [query]).data]
    q = vecs.pop()
    return sorted(((cosine(v, q), a) for v, a in zip(vecs, articles)), key=lambda x: x[0], reverse=True)
EOF
```

## What to build

Write `/root/fde-lab/31-guardrails/guard.py`:

- `is_on_topic(question)` returns `(on_topic, score)`: the best cosine score against the articles, rounded to 3 decimals, and whether it's at least `THRESHOLD = 0.3`.
- `answer(question)` returns `{"on_topic": bool, "score": float, "answer": str}`. Off-topic questions get exactly `I can only help with Meridian shipping and delivery questions.` **with no chat call**. On-topic ones go to `lab-fast` at `temperature=0` with the top 3 articles as sources.
- `python guard.py QUESTION` prints that dict as JSON.

```bash
cd /root/fde-lab/31-guardrails
python guard.py "Can I change my delivery address?"
python guard.py "Write me a poem about the sea"
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Look at the scores for a few on-topic and off-topic questions before trusting the threshold.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/31-guardrails
cat > guard.py <<'EOF'
import json
import sys

from vectors import client, scored

THRESHOLD = 0.3
OFF_TOPIC = "I can only help with Meridian shipping and delivery questions."


def is_on_topic(question):
    best = scored(question)[0][0]
    return best >= THRESHOLD, round(best, 3)


def answer(question):
    on_topic, score = is_on_topic(question)
    if not on_topic:
        return {"on_topic": False, "score": score, "answer": OFF_TOPIC}
    sources = "\n".join(f"[{a['id']}] {a['title']}. {a['text']}" for _, a in scored(question)[:3])
    reply = client.chat.completions.create(
        model="lab-fast",
        temperature=0,
        messages=[{"role": "system", "content": f"You are Meridian Logistics' support assistant. Answer from the sources.\n\nSources:\n{sources}"},
                  {"role": "user", "content": question}],
    ).choices[0].message.content
    return {"on_topic": True, "score": score, "answer": reply}


if __name__ == "__main__":
    print(json.dumps(answer(sys.argv[1])))

EOF
python guard.py "Can I change my delivery address?"
python guard.py "Write me a poem about the sea"
```

</details>

## Check your work

```bash
D=/root/fde-lab/31-guardrails; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/guard.py 2>/dev/null && [ -s $D/guard.py ] && echo "✅ guard.py reads the key from the environment" || echo "❌ guard.py must not contain a key - let the SDK read it from the environment"
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
OFF = 'I can only help with Meridian shipping and delivery questions.'
def chats():
    return sum(1 for l in open("/var/log/ailab/requests.jsonl") if '"chat.completions"' in l)
for q in ("Give me a recipe for lasagne", "What's the best laptop to buy?"):
    before = chats()
    rc, out, err = run("guard.py", q)
    try:
        r = json.loads(out)
    except ValueError:
        r = {}
    ok(rc == 0 and r.get("on_topic") is False and r.get("answer") == OFF and chats() == before and isinstance(r.get("score"), float) and r["score"] < 0.3,
       f"'{q}' is blocked with the fixed reply and no chat call", f"'{q}' should be off-topic: on_topic false, the fixed reply, a score below 0.3 and no chat call - got {out[:200]!r} {err[-150:]}")
before = chats()
rc, out, err = run("guard.py", "Can I report a damaged box?")
try:
    r = json.loads(out)
except ValueError:
    r = {}
ok(rc == 0 and r.get("on_topic") is True and r.get("score", 0) >= 0.3 and chats() == before + 1 and r.get("answer") and r["answer"] != OFF,
   "an on-topic question passes the filter and gets one model call", f"'Can I report a damaged box?' should be on-topic and answered with one chat call - got {out[:200]!r} {err[-150:]}")
PYEOF
jq -se 'any(.[]; .ok and .api == "chat.completions" and .model == "lab-fast" and (.client | startswith("OpenAI/Python")) and .temperature == 0 and .system)' /var/log/ailab/requests.jsonl >/dev/null 2>&1 && echo "✅ the gateway logged your lab-fast call" || echo "❌ the gateway has no lab-fast call from your script yet"
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Input filters decide whether a request reaches the model at all.
- The best retrieval score doubles as a cheap topic filter - pick the threshold from real data.
- Off-topic requests get a fixed, helpful reply with no model call.
