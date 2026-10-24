---
type: task
title: "Return the answer with source chunk ids"
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

Write `/root/fde-lab/18-grounding/cite.py`:

- `check_citations(result, source_ids)` returns a list of problems (empty when fine), applying the four checks from the lesson. The refusal is `I don't know based on the provided sources.`
- `cite(question)` retrieves the vector top 3, calls `lab-fast` at `temperature=0` in JSON mode with this system prompt plus the sources, and returns the parsed object with two extra keys: `sources` (the ids sent) and `problems`.
  ```text
  Answer the question using only the sources. After each fact, cite its source id in square brackets, like [a3]. If the sources don't contain the answer, reply exactly: I don't know based on the provided sources. Reply with JSON: {"answer": "...", "citations": ["a3"]}
  ```
- `python cite.py QUESTION` prints the result as JSON and exits with status 2 if there are problems, 0 otherwise.

```bash
cd /root/fde-lab/18-grounding
python cite.py "What happens after two failed delivery attempts?"
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Check `c not in source_ids` before checking the brackets - an unknown id is one problem, not two.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/18-grounding
[ -f vectors.py ] || cat > vectors.py <<'EOF'
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
cat > cite.py <<'EOF'
import json
import sys

from vectors import ARTICLES, client, vector_rank

BY_ID = {a["id"]: a for a in ARTICLES}
REFUSE = "I don't know based on the provided sources."
SYSTEM = 'Answer the question using only the sources. After each fact, cite its source id in square brackets, like [a3]. If the sources don\'t contain the answer, reply exactly: I don\'t know based on the provided sources. Reply with JSON: {"answer": "...", "citations": ["a3"]}'


def check_citations(result, source_ids):
    answer, cites = result.get("answer") or "", result.get("citations") or []
    problems = []
    for c in cites:
        if c not in source_ids:
            problems.append(f"unknown source {c}")
        elif f"[{c}]" not in answer:
            problems.append(f"{c} not cited in the answer")
    if answer == REFUSE and cites:
        problems.append("a refusal must not cite sources")
    if answer != REFUSE and not cites:
        problems.append("an answer needs at least one citation")
    return problems


def cite(question):
    sources = vector_rank(question)[:3]
    context = "\n".join(f"[{i}] {BY_ID[i]['title']}. {BY_ID[i]['text']}" for i in sources)
    raw = client.chat.completions.create(
        model="lab-fast",
        temperature=0,
        response_format={"type": "json_object"},
        messages=[{"role": "system", "content": f"{SYSTEM}\n\nSources:\n{context}"}, {"role": "user", "content": question}],
    ).choices[0].message.content
    result = json.loads(raw)
    result["sources"] = sources
    result["problems"] = check_citations(result, sources)
    return result


if __name__ == "__main__":
    r = cite(sys.argv[1])
    print(json.dumps(r))
    sys.exit(2 if r["problems"] else 0)

EOF
python cite.py "What happens after two failed delivery attempts?"
```

</details>

## Check your work

```bash
D=/root/fde-lab/18-grounding; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/cite.py 2>/dev/null && [ -s $D/cite.py ] && echo "✅ cite.py reads the key from the environment" || echo "❌ cite.py must not contain a key - let the SDK read it from the environment"
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
sys.path.insert(0, ".")
try:
    from cite import check_citations as cc
    cases = [
        ({"answer": "Wait 7 days [a9].", "citations": ["a9"]}, ["a9", "a2"], 0),
        ({"answer": "Wait 7 days [a7].", "citations": ["a7"]}, ["a9", "a2"], 1),
        ({"answer": "Wait 7 days.", "citations": ["a9"]}, ["a9"], 1),
        ({"answer": "Wait 7 days.", "citations": []}, ["a9"], 1),
        ({"answer": REFUSE, "citations": []}, ["a9"], 0),
        ({"answer": REFUSE, "citations": ["a9"]}, ["a9"], 2),
    ]
    res = [len(cc(r, s)) for r, s, _ in cases]
    good = res == [n for _, _, n in cases]
except Exception as e:
    good, res = False, str(e)
ok(good, "check_citations finds unknown ids, missing brackets, uncited answers and cited refusals", f"check_citations problem counts should be {[n for _, _, n in cases] if 'cases' in dir() else ''} - got {res}")
arts = load("articles.json")
vecs = E([f"{a['title']}. {a['text']}" for a in arts])
q = "What happens to my parcel if the driver fails twice?"
qv = E([q])[0]
top3 = [a["id"] for _, a in sorted(zip([cos(v, qv) for v in vecs], arts), key=lambda x: x[0], reverse=True)[:3]]
rc, out, err = run("cite.py", q)
try:
    r = json.loads(out)
except ValueError:
    r = {}
ok(rc == 0 and r.get("sources") == top3 and r.get("problems") == [] and "a9" in (r.get("citations") or []), "the answer cites the missed-delivery article with no problems", f"expected exit 0, sources {top3}, no problems and a citation of a9 - got exit {rc}, {str(r)[:300]} {err[-150:]}")
PYEOF
jq -se 'any(.[]; .ok and .api == "chat.completions" and .model == "lab-fast" and (.client | startswith("OpenAI/Python")) and .json_mode and .temperature == 0)' /var/log/ailab/requests.jsonl >/dev/null 2>&1 && echo "✅ the gateway logged your lab-fast call" || echo "❌ the gateway has no lab-fast call from your script yet"
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Ask for citations inside a JSON structure so code can read them.
- Validate every citation against the ids you actually sent.
- Citations make checking possible; faithfulness evals do the checking.
