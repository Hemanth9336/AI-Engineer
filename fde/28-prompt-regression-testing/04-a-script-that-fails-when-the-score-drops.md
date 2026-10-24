---
type: task
title: "A script that fails when the score drops"
minutes: 10
---

## Set up

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

Write `/root/fde-lab/28-regression/gate.py`, used as:

```bash
python gate.py BASELINE_JSON CANDIDATE_JSON [--max-drop 0.0]
```

Both files have the format `evals.py` writes.

- Print `regressed: g1, g2` listing candidate failures that weren't baseline failures (skip the line if there are none).
- If `baseline score - candidate score` is greater than `--max-drop`, print `FAIL: ...` and exit `1`.
- Otherwise print `PASS: ...` and exit `0`.

```bash
cd /root/fde-lab/28-regression
python evals.py prompts/v1.txt golden.jsonl
python evals.py prompts/v2.txt golden.jsonl
python gate.py results/v1.json results/v2.json; echo "exit $?"
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Compare floats with a small tolerance (`+ 1e-9`) so a drop of exactly `--max-drop` passes.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/28-regression
[ -f evals.py ] || cat > evals.py <<'EOF'
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
cat > gate.py <<'EOF'
import argparse
import json
import sys

p = argparse.ArgumentParser()
p.add_argument("baseline")
p.add_argument("candidate")
p.add_argument("--max-drop", type=float, default=0.0)
args = p.parse_args()

base = json.load(open(args.baseline))
cand = json.load(open(args.candidate))
regressed = [c for c in cand["failures"] if c not in base["failures"]]
if regressed:
    print("regressed: " + ", ".join(regressed))
if base["score"] - cand["score"] > args.max_drop + 1e-9:
    print(f"FAIL: score {cand['score']:.2f} < baseline {base['score']:.2f} (max drop {args.max_drop:.2f})")
    sys.exit(1)
print(f"PASS: score {cand['score']:.2f} (baseline {base['score']:.2f})")

EOF
python evals.py prompts/v1.txt golden.jsonl
python evals.py prompts/v2.txt golden.jsonl
python gate.py results/v1.json results/v2.json || echo "gate failed as expected"
```

</details>

## Check your work

```bash
D=/root/fde-lab/28-regression; cd $D 2>/dev/null || echo "❌ create $D"
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
def res(name, passed, total, failures):
    p = Path(f"/tmp/gate-{name}.json")
    p.write_text(json.dumps({"prompt": name, "passed": passed, "total": total, "score": passed / total, "failures": failures}))
    return str(p)
base, worse, same, better = res("base", 9, 10, ["c4"]), res("worse", 8, 10, ["c4", "c7"]), res("same", 9, 10, ["c2"]), res("better", 10, 10, [])
rc, out, err = run("gate.py", base, worse)
ok(rc == 1 and "regressed: c7" in out and "FAIL" in out, "a drop from 0.9 to 0.8 fails the gate and names c7", f"expected exit 1, 'regressed: c7' and FAIL - got exit {rc}, {out!r} {err[-200:]}")
rc, out, err = run("gate.py", base, worse, "--max-drop", "0.1")
ok(rc == 0 and "PASS" in out and "regressed: c7" in out, "--max-drop 0.1 allows that drop but still reports the regression", f"with --max-drop 0.1 expected exit 0 with PASS and the regressed line - got exit {rc}, {out!r}")
rc, out, err = run("gate.py", base, same)
ok(rc == 0 and "regressed: c2" in out, "same score with a different failing case passes and reports it", f"expected exit 0 and 'regressed: c2' - got exit {rc}, {out!r}")
rc, out, err = run("gate.py", base, better)
ok(rc == 0 and "regressed" not in out, "an improvement passes with no regressed line", f"expected exit 0 and no regressed line - got exit {rc}, {out!r}")
PYEOF
```

## What you learned

- A gate turns 'compare the results' into an exit code a pipeline can enforce.
- Always print the regressed cases - they're what you fix.
- Allow small noise for judged suites; allow none on safety slices.
