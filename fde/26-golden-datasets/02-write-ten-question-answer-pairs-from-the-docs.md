---
type: task
title: "Write ten question-answer pairs from the docs"
minutes: 7
---

## Set up

`articles.json` holds Meridian's twelve help articles - the documents the support bot answers from.

```bash
mkdir -p /root/fde-lab/26-golden
cd /root/fde-lab/26-golden
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

Read the articles and write `/root/fde-lab/26-golden/golden.jsonl`: at least **10** cases, one JSON object per line, with the fields from the lesson.

- `id` - unique, like `g01`.
- `question` - phrased the way a customer would ask, **not** copied from the article title. Every question is different.
- `expected` - the key facts, including the article's numbers where it has them.
- `source` - the id of the article that answers it. Use at least **six different** articles.
- `type` - `easy` or `hard`. Include at least two `hard` ones: questions that need a small inference, like "Can I send a 950 kg pallet?".

```bash
cd /root/fde-lab/26-golden
wc -l golden.jsonl
jq -r '.source' golden.jsonl | sort | uniq -c
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `jq -c . golden.jsonl` fails loudly on a broken line - a quick way to validate the file.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/26-golden
cat > golden.jsonl <<'EOF'
{"id": "g01", "question": "How long do I have to report a damaged parcel?", "expected": "Within 7 days of delivery, with photos of the item and packaging.", "source": "a1", "type": "easy"}
{"id": "g02", "question": "What does changing the address cost after dispatch?", "expected": "6 EUR, and it adds one working day.", "source": "a2", "type": "easy"}
{"id": "g03", "question": "Who pays import duties on a parcel to Norway?", "expected": "The receiver, unless the sender booked DDP.", "source": "a3", "type": "hard"}
{"id": "g04", "question": "When is customer support open?", "expected": "8:00 to 18:00 CET, Monday to Friday.", "source": "a4", "type": "easy"}
{"id": "g05", "question": "Tracking hasn't changed since Monday and it's Thursday - what should I do?", "expected": "Contact support - tracking unchanged for 3 working days.", "source": "a5", "type": "hard"}
{"id": "g06", "question": "Can I send a 950 kg pallet tomorrow?", "expected": "Not as a standard pallet - over 800 kg needs a freight booking 2 working days in advance.", "source": "a6", "type": "hard"}
{"id": "g07", "question": "Can lithium batteries go by air?", "expected": "No - dangerous goods travel by road only, with a declaration.", "source": "a7", "type": "easy"}
{"id": "g08", "question": "What are the payment terms on business invoices?", "expected": "30 days; invoices are issued on the 1st of each month.", "source": "a8", "type": "easy"}
{"id": "g09", "question": "What happens after two failed delivery attempts?", "expected": "The parcel waits at the local depot for 7 days, then returns to the sender.", "source": "a9", "type": "easy"}
{"id": "g10", "question": "My scanner shows E-4417. What do I do?", "expected": "The label barcode is unreadable - re-print the label from the depot terminal.", "source": "a10", "type": "hard"}
EOF
wc -l golden.jsonl
jq -r '.source' golden.jsonl | sort | uniq -c
```

</details>

## Check your work

```bash
D=/root/fde-lab/26-golden; cd $D 2>/dev/null || echo "❌ create $D"
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
arts = {a["id"]: a for a in load("articles.json")}
rows, bad = [], []
for i, line in enumerate(Path("golden.jsonl").read_text().splitlines() if Path("golden.jsonl").exists() else [], 1):
    if line.strip():
        try:
            rows.append(json.loads(line))
        except ValueError:
            bad.append(i)
ok(not bad and len(rows) >= 10, f"golden.jsonl has {len(rows)} valid cases", f"golden.jsonl needs at least 10 valid JSON lines - got {len(rows)}, broken lines {bad}")
keys = {"id", "question", "expected", "source", "type"}
ok(rows and all(keys <= set(r) and all(str(r[k]).strip() for k in keys) for r in rows), "every case has id, question, expected, source and type", f"every case needs non-empty {sorted(keys)}")
ok(len({r.get("id") for r in rows}) == len(rows) and len({str(r.get("question", "")).strip().lower() for r in rows}) == len(rows), "ids and questions are unique", "ids and questions must be unique")
srcs = [r.get("source") for r in rows]
ok(rows and all(s in arts for s in srcs) and len(set(srcs)) >= 6, f"sources are real article ids covering {len(set(srcs))} articles", f"every source must be an article id, covering at least 6 articles - got {sorted(set(map(str, srcs)))}")
ok(rows and not any(str(r.get("question", "")).strip().lower() == arts.get(r.get("source"), {}).get("title", "").lower() for r in rows), "questions aren't copied from article titles", "phrase questions as a customer would, not as the article title")
def facts(s):
    return set(re.findall(r"\d+", s))
import re
miss = [r["id"] for r in rows if r.get("source") in arts and facts(arts[r["source"]]["text"]) and r.get("type") == "easy" and not (facts(str(r.get("expected"))) & facts(arts[r["source"]]["text"]))]
ok(rows and not miss, "expected answers carry the articles' numbers", f"these cases' expected answers have none of their article's numbers: {miss}")
types = [r.get("type") for r in rows]
ok(set(types) <= {"easy", "hard"} and types.count("hard") >= 2, "the set mixes easy and at least two hard cases", f"type must be easy or hard, with at least two hard - got {types}")
PYEOF
```

## What you learned

- A golden case is id, question, expected facts, source and type - one JSON line.
- Expected answers list checkable facts, not exact wording.
- Cover many documents and include some hard questions from the start.
