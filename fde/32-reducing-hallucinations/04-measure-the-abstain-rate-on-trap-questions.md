---
type: task
title: "Measure the abstain rate on trap questions"
minutes: 8
---

## Set up

`golden.jsonl` mixes four trap questions with three answerable ones. If you skipped the previous task, Set up writes `abstain.py` for you.

```bash
mkdir -p /root/fde-lab/32-hallucinations
cd /root/fde-lab/32-hallucinations
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
[ -f abstain.py ] || cat > abstain.py <<'EOF'
import json
import sys

from vectors import client, scored

REFUSE = "I don't know based on the provided sources."
SYSTEM = ("Answer the question using only the sources below. "
          f"If the sources don't contain the answer, reply exactly: {REFUSE} "
          "Do not use outside knowledge, even if you are confident. "
          "If the sources answer only part of the question, answer that part and say which part they don't cover.")


def answer(question, min_score=0.3, k=3):
    sources = [a for s, a in scored(question)[:k] if s >= min_score]
    if not sources:
        return {"answer": REFUSE, "sources": [], "called_model": False}
    context = "\n".join(f"[{a['id']}] {a['title']}. {a['text']}" for a in sources)
    reply = client.chat.completions.create(
        model="lab-fast",
        temperature=0,
        messages=[{"role": "system", "content": f"{SYSTEM}\n\nSources:\n{context}"}, {"role": "user", "content": question}],
    ).choices[0].message.content.strip()
    return {"answer": reply, "sources": [a["id"] for a in sources], "called_model": True}


if __name__ == "__main__":
    print(json.dumps(answer(sys.argv[1])))
EOF
cat > golden.jsonl <<'EOF'
{"id": "t01", "question": "How much does DDP cost?", "type": "trap"}
{"id": "t02", "question": "Do you deliver to Iceland?", "type": "trap"}
{"id": "t03", "question": "What is the fuel surcharge percentage this month?", "type": "trap"}
{"id": "t04", "question": "Can I get a discount if I ship 500 parcels a month?", "type": "trap"}
{"id": "g01", "question": "How many days does a parcel wait at the local depot?", "type": "easy"}
{"id": "g02", "question": "When is customer support open?", "type": "easy"}
{"id": "g03", "question": "Can I send lithium batteries by air?", "type": "easy"}
EOF
```

## What to build

Write `/root/fde-lab/32-hallucinations/abstain_rate.py`, used as `python abstain_rate.py GOLDEN`. Run every case through `abstain.answer` and print one JSON line:

```json
{"traps": 4, "abstain_rate": 0.75, "invented": ["t04"], "answerable": 3, "false_abstain_rate": 0.0, "false_abstain": []}
```

- `invented` - trap ids that did **not** get the exact refusal.
- `false_abstain` - answerable ids that **did** get it.
- Rates rounded to 2 decimals.

```bash
cd /root/fde-lab/32-hallucinations
python abstain_rate.py golden.jsonl
```

Read the trap that got through. What would you change: the threshold, the prompt, or the documents?

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Import `REFUSE` from `abstain` so both scripts use the same sentence.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/32-hallucinations
cat > abstain_rate.py <<'EOF'
import json
import sys

from abstain import REFUSE, answer

cases = [json.loads(l) for l in open(sys.argv[1]) if l.strip()]
traps = [c for c in cases if c["type"] == "trap"]
real = [c for c in cases if c["type"] != "trap"]
invented = [c["id"] for c in traps if answer(c["question"])["answer"] != REFUSE]
false_abstain = [c["id"] for c in real if answer(c["question"])["answer"] == REFUSE]
print(json.dumps({
    "traps": len(traps),
    "abstain_rate": round((len(traps) - len(invented)) / len(traps), 2) if traps else None,
    "invented": invented,
    "answerable": len(real),
    "false_abstain_rate": round(len(false_abstain) / len(real), 2) if real else None,
    "false_abstain": false_abstain,
}))

EOF
python abstain_rate.py golden.jsonl
```

</details>

## Check your work

```bash
D=/root/fde-lab/32-hallucinations; cd $D 2>/dev/null || echo "❌ create $D"
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
Path("/tmp/g32.jsonl").write_text("".join(json.dumps(c) + "\n" for c in [
    {"id": "x1", "question": "Can I get a discount if I ship 500 parcels a month?", "type": "trap"},
    {"id": "x2", "question": "How much does DDP cost?", "type": "trap"},
    {"id": "x3", "question": "Do you deliver to Iceland?", "type": "trap"},
    {"id": "x4", "question": "How many days does a parcel wait at the local depot?", "type": "easy"},
    {"id": "x5", "question": "Who will win the football tonight?", "type": "hard"},
]))
rc, out, err = run("abstain_rate.py", "/tmp/g32.jsonl")
try:
    got = json.loads(out.splitlines()[-1])
except Exception:
    got = None
want = {"traps": 3, "abstain_rate": 0.67, "invented": ["x1"], "answerable": 2, "false_abstain_rate": 0.5, "false_abstain": ["x5"]}
ok(got == want, "abstain_rate.py measured an unseen set correctly", f"expected {want} - got {out[-300:]!r} {err[-200:]}")
PYEOF
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Measure abstain rate on traps and false-abstain rate on answerable questions together.
- Stricter settings refuse more of both - the trade-off is a decision for the customer.
- Every invented trap answer is a concrete case to fix.
