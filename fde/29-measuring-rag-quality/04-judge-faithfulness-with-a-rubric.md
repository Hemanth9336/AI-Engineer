---
type: task
title: "Judge faithfulness with a rubric"
minutes: 9
---

## Set up

`answers.jsonl` holds three bot answers with the ids of the sources each was given.

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
cat > answers.jsonl <<'EOF'
{"id": "f1", "answer": "Report damage within 7 days of delivery with photos [a1].", "sources": ["a1"]}
{"id": "f2", "answer": "Report damage within 7 days; approved claims are refunded within 24 hours [a1].", "sources": ["a1"]}
{"id": "f3", "answer": "Customs checks usually add 2 to 5 working days [a3].", "sources": ["a3"]}
EOF
```

## What to build

Write `/root/fde-lab/29-rag-quality/faithful.py`:

- `judge_faithfulness(answer, source_ids)` sends the sources (`[id] title. text`, one per line) and the answer to `lab-smart` at `temperature=0` in JSON mode, with this system prompt:
  ```text
  You check a support answer against its sources. List every claim in the answer that the sources do not support. Reply with JSON: {"faithful": true or false, "unsupported": ["claim", ...]}
  ```
  It returns `{"faithful": bool, "unsupported": [str]}`. Any unsupported claim makes `faithful` false, whatever the judge said.
- `python faithful.py ANSWERS` prints `<id> faithful []` or `<id> UNFAITHFUL [claims]` per line, then `faithfulness: N/M`.

```bash
cd /root/fde-lab/29-rag-quality
python faithful.py answers.jsonl
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Put the sources first and the answer last in the user message: `Sources:\n...\n\nAnswer: ...`.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/29-rag-quality
cat > faithful.py <<'EOF'
import json
import sys
from pathlib import Path

from openai import OpenAI

client = OpenAI()
ARTICLES = {a["id"]: a for a in json.loads(Path(__file__).with_name("articles.json").read_text())}
SYSTEM = 'You check a support answer against its sources. List every claim in the answer that the sources do not support. Reply with JSON: {"faithful": true or false, "unsupported": ["claim", ...]}'


def judge_faithfulness(answer, source_ids):
    sources = "\n".join(f"[{i}] {ARTICLES[i]['title']}. {ARTICLES[i]['text']}" for i in source_ids)
    raw = client.chat.completions.create(
        model="lab-smart",
        temperature=0,
        response_format={"type": "json_object"},
        messages=[{"role": "system", "content": SYSTEM}, {"role": "user", "content": f"Sources:\n{sources}\n\nAnswer: {answer}"}],
    ).choices[0].message.content
    result = json.loads(raw)
    unsupported = [str(c) for c in result.get("unsupported") or []]
    return {"faithful": bool(result.get("faithful")) and not unsupported, "unsupported": unsupported}


if __name__ == "__main__":
    rows = [json.loads(l) for l in open(sys.argv[1]) if l.strip()]
    good = 0
    for r in rows:
        v = judge_faithfulness(r["answer"], r["sources"])
        good += v["faithful"]
        print(f"{r['id']} {'faithful' if v['faithful'] else 'UNFAITHFUL'} {v['unsupported']}")
    print(f"faithfulness: {good}/{len(rows)}")

EOF
python faithful.py answers.jsonl
```

</details>

## Check your work

```bash
D=/root/fde-lab/29-rag-quality; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/faithful.py 2>/dev/null && [ -s $D/faithful.py ] && echo "✅ faithful.py reads the key from the environment" || echo "❌ faithful.py must not contain a key - let the SDK read it from the environment"
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
Path("/tmp/a29.jsonl").write_text("".join(json.dumps(r) + "\n" for r in [
    {"id": "k1", "answer": "After dispatch an address change costs 6 EUR [a2].", "sources": ["a2"]},
    {"id": "k2", "answer": "Address changes after dispatch are free and instant [a2].", "sources": ["a2"]},
]))
rc, out, err = run("faithful.py", "/tmp/a29.jsonl")
lines = out.splitlines()
ok(rc == 0 and len(lines) == 3 and lines[0].startswith("k1 faithful") and lines[1].startswith("k2 UNFAITHFUL") and "free" in lines[1] and lines[2] == "faithfulness: 1/2",
   "the judge flagged the invented claim and passed the supported one", f"expected 'k1 faithful', 'k2 UNFAITHFUL [...free...]', 'faithfulness: 1/2' - got {lines} {err[-200:]}")
sys.path.insert(0, ".")
try:
    import faithful, types
    reply = '{"faithful": true, "unsupported": ["refunds within 24 hours"]}'
    faithful.client = types.SimpleNamespace(chat=types.SimpleNamespace(completions=types.SimpleNamespace(create=lambda **k: types.SimpleNamespace(choices=[types.SimpleNamespace(message=types.SimpleNamespace(content=reply))]))))
    v = faithful.judge_faithfulness("x", ["a1"])
    ok(v == {"faithful": False, "unsupported": ["refunds within 24 hours"]}, "a judge that says true but lists a claim counts as unfaithful", f"any unsupported claim must make faithful false - got {v}")
except Exception as e:
    print(f"❌ import faithful failed: {e}")
PYEOF
jq -se 'any(.[]; .ok and .api == "chat.completions" and .model == "lab-smart" and (.client | startswith("OpenAI/Python")) and .json_mode and .temperature == 0 and .system)' /var/log/ailab/requests.jsonl >/dev/null 2>&1 && echo "✅ the gateway logged your lab-smart call" || echo "❌ the gateway has no lab-smart call from your script yet"
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Faithfulness checks every claim against the sources actually sent.
- It needs no expected answer, so it works on live traffic too.
- Ask the judge to list unsupported claims - the list is the evidence.
