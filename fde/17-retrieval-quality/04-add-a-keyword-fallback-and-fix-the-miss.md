---
type: task
title: "Add a keyword fallback and fix the miss"
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

Write `/root/fde-lab/17-retrieval/hybrid.py`, used as `python hybrid.py QUERY K`, that prints a JSON list of the top K article ids by hybrid search:

- Tokens: lowercase, `re.findall(r"[a-z0-9]+(?:-[a-z0-9]+)*", text)`, as a set.
- Stop words: `a an and are can do does for how i in is it me my of on or our the to we what when where which who why will with you your`
- Keyword score = number of the query's non-stop tokens found in the article's `title + " " + text` tokens. Only articles with a score above 0 get a keyword rank: by score (highest first), ties broken by vector rank.
- RRF score = `1 / (60 + vector_rank) + 1 / (60 + keyword_rank)`, ranks starting at 1, the keyword term only when the article has one.
- Order by RRF score, highest first; break exact ties by vector rank.

```bash
cd /root/fde-lab/17-retrieval
python hybrid.py "Can we get DDP?" 3          # a3 should now be first
python hybrid.py "How long do customs checks take?" 3
```

Check that the fix didn't break normal queries - that matters as much as fixing the miss.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `vec = vector_rank(query)` then `vrank = {id_: i + 1 for i, id_ in enumerate(vec)}`.
- `kw = sorted([a for a in ids if score[a] > 0], key=lambda a: (-score[a], vrank[a]))`.

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
cat > hybrid.py <<'EOF'
import json
import re
import sys

from vectors import ARTICLES, vector_rank

STOP = set("a an and are can do does for how i in is it me my of on or our the to we what when where which who why will with you your".split())


def tokens(s):
    return set(re.findall(r"[a-z0-9]+(?:-[a-z0-9]+)*", s.lower()))


def hybrid(query):
    vec = vector_rank(query)
    vrank = {id_: i + 1 for i, id_ in enumerate(vec)}
    terms = tokens(query) - STOP
    score = {a["id"]: len(terms & tokens(a["title"] + " " + a["text"])) for a in ARTICLES}
    kw = sorted([i for i in vec if score[i] > 0], key=lambda i: (-score[i], vrank[i]))
    krank = {id_: n + 1 for n, id_ in enumerate(kw)}
    rrf = {i: 1 / (60 + vrank[i]) + (1 / (60 + krank[i]) if i in krank else 0) for i in vec}
    return sorted(vec, key=lambda i: (-rrf[i], vrank[i]))


if __name__ == "__main__":
    print(json.dumps(hybrid(sys.argv[1])[: int(sys.argv[2])]))
EOF
python hybrid.py "Can we get DDP?" 3
python hybrid.py "How long do customs checks take?" 3
```

</details>

## Check your work

```bash
D=/root/fde-lab/17-retrieval; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/hybrid.py 2>/dev/null && [ -s $D/hybrid.py ] && echo "✅ hybrid.py reads the key from the environment" || echo "❌ hybrid.py must not contain a key - let the SDK read it from the environment"
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
import re
STOP = set('a an and are can do does for how i in is it me my of on or our the to we what when where which who why will with you your'.split())
arts = load("articles.json")
vecs = E([f"{a['title']}. {a['text']}" for a in arts])
def tokens(s):
    return set(re.findall(r"[a-z0-9]+(?:-[a-z0-9]+)*", s.lower()))
def ref(q):
    qv = E([q])[0]
    vec = [a["id"] for _, a in sorted(zip([cos(v, qv) for v in vecs], arts), key=lambda x: x[0], reverse=True)]
    vr = {i: n + 1 for n, i in enumerate(vec)}
    terms = tokens(q) - STOP
    sc = {a["id"]: len(terms & tokens(a["title"] + " " + a["text"])) for a in arts}
    kw = sorted([i for i in vec if sc[i] > 0], key=lambda i: (-sc[i], vr[i]))
    kr = {i: n + 1 for n, i in enumerate(kw)}
    rrf = {i: 1 / (60 + vr[i]) + (1 / (60 + kr[i]) if i in kr else 0) for i in vec}
    return sorted(vec, key=lambda i: (-rrf[i], vr[i]))
for q, k in (("Do you offer DDP?", 3), ("Is DDP an option?", 2), ("My scanner shows error E-2210", 4), ("What happens if nobody is home?", 3)):
    rc, out, err = run("hybrid.py", q, str(k))
    try:
        got = json.loads(out)
    except ValueError:
        got = None
    w = ref(q)[:k]
    ok(got == w, f"'{q}' k={k} -> {w}", f"for '{q}' k={k} expected {w} - got {out[:200]!r} {err[-150:]}")
ok(ref("Do you offer DDP?")[0] == "a3", "the DDP miss is fixed: the customs article ranks first", "the customs article should rank first for 'Do you offer DDP?'")
PYEOF
jq -se 'any(.[]; .ok and .api == "embeddings" and .model == "lab-embed" and (.client | startswith("OpenAI/Python")))' /var/log/ailab/requests.jsonl >/dev/null 2>&1 && echo "✅ the gateway logged your lab-embed calls" || echo "❌ the gateway has no lab-embed call from your script yet"
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Hybrid search merges vector search (meaning) and keyword search (exact terms).
- Reciprocal rank fusion combines ranks, so scores don't need calibrating.
- Always re-check normal queries after a retrieval fix.
