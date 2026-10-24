---
type: task
title: "Rerank candidates with the model"
minutes: 9
---

## Set up

```bash
mkdir -p /root/fde-lab/17-retrieval
cd /root/fde-lab/17-retrieval
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

Write `/root/fde-lab/17-retrieval/rerank.py`:

- `merge_ranking(candidates, ranking)` from the lesson.
- `rerank(query)`:
  1. Takes the vector top **5** as candidates.
  2. Asks `lab-fast` at `temperature=0` with `response_format={"type": "json_object"}` to rank them (system prompt as in the lesson; candidates as `[id] title. text` lines).
  3. Parses `{"ranking": [...]}` - treat invalid JSON or a missing list as an empty ranking - and returns `(candidates, merge_ranking(candidates, ranking))`.
- `python rerank.py QUERY` prints `{"candidates": [...], "reranked": [...]}`.

```bash
cd /root/fde-lab/17-retrieval
python rerank.py "What happens if nobody is home for the delivery?"
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `try: ranking = json.loads(raw).get("ranking") or [] except (ValueError, AttributeError): ranking = []`.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/17-retrieval
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
cat > rerank.py <<'EOF'
import json
import sys

from vectors import ARTICLES, client, vector_rank

BY_ID = {a["id"]: a for a in ARTICLES}
SYSTEM = ('Rank the candidate articles by how well they answer the question. '
          'Reply with JSON: {"ranking": ["id", ...]} using only the candidate ids, most relevant first.')


def merge_ranking(candidates, ranking):
    seen, out = set(), []
    for i in ranking:
        if i in candidates and i not in seen:
            out.append(i)
            seen.add(i)
    return out + [c for c in candidates if c not in seen]


def rerank(query):
    candidates = vector_rank(query)[:5]
    lines = "\n".join(f"[{i}] {BY_ID[i]['title']}. {BY_ID[i]['text']}" for i in candidates)
    raw = client.chat.completions.create(
        model="lab-fast",
        temperature=0,
        response_format={"type": "json_object"},
        messages=[{"role": "system", "content": SYSTEM}, {"role": "user", "content": f"Question: {query}\nCandidates:\n{lines}"}],
    ).choices[0].message.content
    try:
        ranking = json.loads(raw).get("ranking") or []
    except (ValueError, AttributeError):
        ranking = []
    return candidates, merge_ranking(candidates, ranking)


if __name__ == "__main__":
    c, r = rerank(sys.argv[1])
    print(json.dumps({"candidates": c, "reranked": r}))
EOF
python rerank.py "What happens if nobody is home for the delivery?"
```

</details>

## Check your work

```bash
D=/root/fde-lab/17-retrieval; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/rerank.py 2>/dev/null && [ -s $D/rerank.py ] && echo "✅ rerank.py reads the key from the environment" || echo "❌ rerank.py must not contain a key - let the SDK read it from the environment"
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
sys.path.insert(0, ".")
try:
    from rerank import merge_ranking as m
    good = (m(["a", "b", "c"], ["c", "a", "b"]) == ["c", "a", "b"] and m(["a", "b", "c"], ["x", "b", "b"]) == ["b", "a", "c"] and m(["a", "b"], []) == ["a", "b"])
except Exception as e:
    good = False
ok(good, "merge_ranking keeps valid ids in the model's order and appends the rest", "merge_ranking should drop unknown and repeated ids and append skipped candidates in their original order")
arts = load("articles.json")
vecs = E([f"{a['title']}. {a['text']}" for a in arts])
q = "My driver couldn't deliver because the office was closed - what now?"
qv = E([q])[0]
top5 = [a["id"] for _, a in sorted(zip([cos(v, qv) for v in vecs], arts), key=lambda x: x[0], reverse=True)[:5]]
rc, out, err = run("rerank.py", q)
try:
    r = json.loads(out)
except ValueError:
    r = {}
ok(r.get("candidates") == top5 and sorted(r.get("reranked") or []) == sorted(top5), "candidates are the vector top 5 and reranked is a reordering of them", f"expected candidates {top5} and reranked a permutation of them - got {r} {err[-150:]}")
ok((r.get("reranked") or [None])[0] == "a9", "the missed-delivery article is ranked first after reranking", f"the reranker should put a9 (Missed delivery) first - got {r.get('reranked')}")
PYEOF
jq -se 'any(.[]; .ok and .api == "chat.completions" and .model == "lab-fast" and (.client | startswith("OpenAI/Python")) and .json_mode and .temperature == 0)' /var/log/ailab/requests.jsonl >/dev/null 2>&1 && echo "✅ the gateway logged a JSON-mode lab-fast rerank call" || echo "❌ no lab-fast call in JSON mode at temperature 0"
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Rerank a handful of fast-search candidates with a model that reads question and document together.
- Merge the model's ranking defensively - the output must be a reordering of real candidates.
- Keep reranking only if it improves the measured hit rate.
