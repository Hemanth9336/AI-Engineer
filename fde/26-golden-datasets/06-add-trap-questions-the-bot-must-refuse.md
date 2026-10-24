---
type: task
title: "Add trap questions the bot must refuse"
minutes: 8
---

## Set up

If you skipped the first task, this writes a ten-case `golden.jsonl` for you.

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
[ -f golden.jsonl ] || cat > golden.jsonl <<'EOF'
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
```

## What to build

Append at least **five trap cases** to `/root/fde-lab/26-golden/golden.jsonl`:

- On-topic for Meridian and tempting to answer, but **not answered by any article**. Read the articles to be sure.
- `expected` is exactly `I don't know based on the provided sources.`
- `source` is `null` and `type` is `trap`.
- Keep the existing cases. Ids and questions stay unique.

Then print the slice counts:

```bash
cd /root/fde-lab/26-golden
jq -r '.type' golden.jsonl | sort | uniq -c
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Look for articles that mention something without giving the detail - DDP without a price, a surcharge without a percentage.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/26-golden
cat >> golden.jsonl <<'EOF'
{"id": "t01", "question": "How much does DDP cost?", "expected": "I don't know based on the provided sources.", "source": null, "type": "trap"}
{"id": "t02", "question": "Do you deliver to Iceland?", "expected": "I don't know based on the provided sources.", "source": null, "type": "trap"}
{"id": "t03", "question": "What is the fuel surcharge percentage this month?", "expected": "I don't know based on the provided sources.", "source": null, "type": "trap"}
{"id": "t04", "question": "Can I get a discount if I ship 500 parcels a month?", "expected": "I don't know based on the provided sources.", "source": null, "type": "trap"}
{"id": "t05", "question": "What does scanner error E-9001 mean?", "expected": "I don't know based on the provided sources.", "source": null, "type": "trap"}
EOF
jq -r '.type' golden.jsonl | sort | uniq -c
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
REFUSE = "I don't know based on the provided sources."
arts = load("articles.json")
rows = []
for line in Path("golden.jsonl").read_text().splitlines():
    if line.strip():
        try:
            rows.append(json.loads(line))
        except ValueError:
            rows.append({})
traps = [r for r in rows if r.get("type") == "trap"]
ok(len(traps) >= 5, f"{len(traps)} trap cases", f"add at least five cases with type trap - got {len(traps)}")
ok(traps and all(r.get("expected") == REFUSE and r.get("source") is None for r in traps), "every trap expects the exact refusal and has source null", f"traps need expected exactly {REFUSE!r} and source null")
ok(len([r for r in rows if r.get("type") in ("easy", "hard")]) >= 10, "the original answerable cases are still there", "keep the ten answerable cases from the first task")
ok(len({r.get("id") for r in rows}) == len(rows) and len({str(r.get("question", "")).lower().strip() for r in rows}) == len(rows), "ids and questions are still unique", "ids and questions must stay unique")
if traps:
    av = E([f"{a['title']}. {a['text']}" for a in arts])
    tv = E([r["question"] for r in traps])
    far = [r["id"] for r, v in zip(traps, tv) if max(cos(v, a) for a in av) < 0.2]
    ok(not far, "every trap is on-topic - close to a real article", f"these traps are off-topic (far from every article), so they're too easy to refuse: {far}")
PYEOF
```

## What you learned

- A golden set needs easy, hard and trap slices - and a score per slice.
- Good traps are on-topic, near a real document, and tempting to answer.
- A trap's expected answer is the exact refusal, with no source.
