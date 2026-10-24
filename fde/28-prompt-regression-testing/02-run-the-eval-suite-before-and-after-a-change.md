---
type: task
title: "Run the eval suite before and after a change"
minutes: 9
---

## Set up

Set up writes the support bot (`bot.py`, whose `answer(question, prompt_file)` answers from all twelve articles), a six-case `golden.jsonl` with the strings each answer must include, and two prompt versions: `prompts/v1.txt` and a 'friendlier, shorter' `prompts/v2.txt`.

```bash
mkdir -p /root/fde-lab/28-regression/prompts
cd /root/fde-lab/28-regression
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
cat > bot.py <<'EOF'
import json
from pathlib import Path

from openai import OpenAI

client = OpenAI()
ARTICLES = json.loads(Path(__file__).with_name("articles.json").read_text())
SOURCES = "\n".join(f"[{a['id']}] {a['title']}. {a['text']}" for a in ARTICLES)


def answer(question, prompt_file):
    system = Path(prompt_file).read_text().strip()
    resp = client.chat.completions.create(
        model="lab-fast",
        temperature=0,
        messages=[{"role": "system", "content": f"{system}\n\nSources:\n{SOURCES}"}, {"role": "user", "content": question}],
    )
    return resp.choices[0].message.content.strip()
EOF
cat > golden.jsonl <<'EOF'
{"id": "g1", "question": "How long do I have to report a damaged parcel?", "must_include": ["7 days", "photos"]}
{"id": "g2", "question": "Can I change the address after the parcel has been dispatched?", "must_include": ["6 EUR", "one working day"]}
{"id": "g3", "question": "When is customer support open?", "must_include": ["8:00", "18:00"]}
{"id": "g4", "question": "How heavy can a standard pallet be?", "must_include": ["800 kg"]}
{"id": "g5", "question": "What happens if I miss two deliveries?", "must_include": ["7 days"]}
{"id": "g6", "question": "What are your payment terms for business invoices?", "must_include": ["30 days"]}
EOF
cat > prompts/v1.txt <<'EOF'
You are Meridian Logistics' support assistant. Answer from the sources. Include every number, deadline and fee the sources give.
EOF
cat > prompts/v2.txt <<'EOF'
You are Meridian Logistics' support assistant. Answer from the sources in one short, friendly sentence.
EOF
```

## What to build

Write `/root/fde-lab/28-regression/evals.py`, used as `python evals.py PROMPT_FILE GOLDEN`:

- `run_suite(prompt_file, golden_file)` answers every case with `bot.answer` and passes a case when **every** `must_include` string appears in the answer (case-insensitive). It returns:
  ```json
  {"prompt": "prompts/v1.txt", "passed": 6, "total": 6, "score": 1.0, "failures": []}
  ```
  with `failures` listing failed case ids in golden-file order.
- The script saves that to `results/<prompt name>.json` (`results/v1.json` for `prompts/v1.txt`) and prints `v1: 6/6 failures=[]`.

Run it on both versions and decide whether v2 can ship:

```bash
cd /root/fde-lab/28-regression
python evals.py prompts/v1.txt golden.jsonl
python evals.py prompts/v2.txt golden.jsonl
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `Path(prompt_file).stem` turns `prompts/v2.txt` into `v2`.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/28-regression
cat > evals.py <<'EOF'
import json
import sys
from pathlib import Path

from bot import answer


def run_suite(prompt_file, golden_file):
    cases = [json.loads(l) for l in open(golden_file) if l.strip()]
    failures = []
    for c in cases:
        reply = answer(c["question"], prompt_file).lower()
        if not all(s.lower() in reply for s in c["must_include"]):
            failures.append(c["id"])
    passed = len(cases) - len(failures)
    return {"prompt": prompt_file, "passed": passed, "total": len(cases), "score": passed / len(cases), "failures": failures}


if __name__ == "__main__":
    result = run_suite(sys.argv[1], sys.argv[2])
    out = Path("results") / (Path(sys.argv[1]).stem + ".json")
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(result, indent=2))
    print(f"{Path(sys.argv[1]).stem}: {result['passed']}/{result['total']} failures={result['failures']}")

EOF
python evals.py prompts/v1.txt golden.jsonl
python evals.py prompts/v2.txt golden.jsonl
```

</details>

## Check your work

```bash
D=/root/fde-lab/28-regression; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/evals.py 2>/dev/null && [ -s $D/evals.py ] && echo "✅ evals.py reads the key from the environment" || echo "❌ evals.py must not contain a key - let the SDK read it from the environment"
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
r1, r2 = load("results/v1.json") or {}, load("results/v2.json") or {}
ok(r1.get("passed") == 6 and r1.get("total") == 6 and r1.get("failures") == [] and r1.get("score") == 1.0, "results/v1.json: v1 passes 6/6", f"expected results/v1.json with 6/6 and no failures - got {r1}")
ok(r2.get("passed") == 4 and r2.get("failures") == ["g1", "g2"] and abs(r2.get("score", 0) - 4 / 6) < 1e-6, "results/v2.json: v2 drops to 4/6, failing g1 and g2", f"expected results/v2.json with 4/6 and failures ['g1', 'g2'] - got {r2}")
Path("/tmp/g28.jsonl").write_text(json.dumps({"id": "z1", "question": "When is customer support open?", "must_include": ["8:00", "CET", "Saturday"]}) + "\n")
sys.path.insert(0, ".")
try:
    from evals import run_suite
    r = run_suite("prompts/v1.txt", "/tmp/g28.jsonl")
    ok(r.get("passed") == 0 and r.get("failures") == ["z1"], "a case passes only if every must_include string is present", f"an answer missing one required string must fail - got {r}")
except Exception as e:
    print(f"❌ import evals failed: {e}")
PYEOF
jq -se 'any(.[]; .ok and .api == "chat.completions" and .model == "lab-fast" and (.client | startswith("OpenAI/Python")) and .temperature == 0 and .system)' /var/log/ailab/requests.jsonl >/dev/null 2>&1 && echo "✅ the gateway logged your lab-fast call" || echo "❌ the gateway has no lab-fast call from your script yet"
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Run the same golden set before and after every prompt change.
- Save results per version and compare case by case, not just the score.
- Code checks like 'contains 6 EUR' are fast, free and exact - use them first.
