---
type: task
title: "Reproduce a cross-user leak in a toy index"
minutes: 9
---

## Set up

`docs.json` holds eight Meridian documents, each tagged with the `groups` allowed to read it. `users.json` maps users to their groups.

```bash
mkdir -p /root/fde-lab/19-permissions
cd /root/fde-lab/19-permissions
cat > docs.json <<'EOF'
[
  {
    "id": "d1",
    "groups": [
      "public"
    ],
    "title": "Support hours",
    "text": "Customer support is open 8:00 to 18:00 CET, Monday to Friday."
  },
  {
    "id": "d2",
    "groups": [
      "drivers"
    ],
    "title": "Driver shift rota",
    "text": "Driver shifts start at 6:00 and 14:00. Swap shifts through the depot supervisor at least 48 hours ahead."
  },
  {
    "id": "d3",
    "groups": [
      "hr"
    ],
    "title": "Salary bands 2026",
    "text": "Driver grade D1 earns 28,000 to 31,000 EUR. Driver grade D2 earns 31,000 to 34,500 EUR. Depot managers earn 52,000 to 61,000 EUR."
  },
  {
    "id": "d4",
    "groups": [
      "hr"
    ],
    "title": "Disciplinary process",
    "text": "A first written warning stays on file for 12 months. Dismissal requires a hearing with an HR partner present."
  },
  {
    "id": "d5",
    "groups": [
      "finance"
    ],
    "title": "Q1 margin report",
    "text": "Q1 gross margin was 18.2 percent. The Rotterdam depot ran at a loss because of fuel costs."
  },
  {
    "id": "d6",
    "groups": [
      "public"
    ],
    "title": "Damage claims",
    "text": "Report damage within 7 days of delivery with photos of the item and packaging."
  },
  {
    "id": "d7",
    "groups": [
      "drivers"
    ],
    "title": "Fuel card PIN reset",
    "text": "Drivers reset a fuel card PIN in the driver app under Cards. Three wrong PINs block the card for 24 hours."
  },
  {
    "id": "d8",
    "groups": [
      "finance",
      "sales"
    ],
    "title": "Customer credit limits",
    "text": "Harbor Foods has a credit limit of 50,000 EUR. Dockside Retail has a credit limit of 20,000 EUR."
  }
]
EOF
cat > users.json <<'EOF'
{
  "tom": [
    "public",
    "drivers"
  ],
  "priya": [
    "public",
    "hr"
  ],
  "sam": [
    "public",
    "finance",
    "hr"
  ],
  "lena": [
    "public",
    "sales"
  ]
}
EOF
```

## What to build

Write `/root/fde-lab/19-permissions/leak.py`, used as `python leak.py USER QUERY`, that searches **all** documents with no permission check (embed `"<title>. <text>"`, rank by cosine) and prints:

```json
{"user": "tom", "query": "...", "top": "d3", "allowed": false}
```

`allowed` is `true` when the user shares at least one group with the top document.

Find a question that makes `tom` (a driver) retrieve a document he must not see, and save its output:

```bash
cd /root/fde-lab/19-permissions
python leak.py tom "What do D2 drivers earn?" > leak.json
cat leak.json
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `bool(set(USERS[user]) & set(doc["groups"]))`.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/19-permissions
cat > common.py <<'EOF'
import json
import math
from pathlib import Path

from openai import OpenAI

client = OpenAI()
HERE = Path(__file__).parent
DOCS = json.loads((HERE / "docs.json").read_text())
USERS = json.loads((HERE / "users.json").read_text())


def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    return dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))


def ranked(query, docs):
    if not docs:
        return []
    vecs = [d.embedding for d in client.embeddings.create(model="lab-embed", input=[f"{d['title']}. {d['text']}" for d in docs] + [query]).data]
    q = vecs.pop()
    return [d for _, d in sorted(zip([cosine(v, q) for v in vecs], docs), key=lambda x: x[0], reverse=True)]


def allowed(user, doc):
    return bool(set(USERS.get(user, [])) & set(doc["groups"]))

EOF
cat > leak.py <<'EOF'
import json
import sys

from common import DOCS, allowed, ranked

user, query = sys.argv[1], sys.argv[2]
top = ranked(query, DOCS)[0]
print(json.dumps({"user": user, "query": query, "top": top["id"], "allowed": allowed(user, top)}))
EOF
python leak.py tom "What do D2 drivers earn?" > leak.json
cat leak.json
```

</details>

## Check your work

```bash
D=/root/fde-lab/19-permissions; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/leak.py 2>/dev/null && [ -s $D/leak.py ] && echo "✅ leak.py reads the key from the environment" || echo "❌ leak.py must not contain a key - let the SDK read it from the environment"
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
docs, users = load("docs.json"), load("users.json")
vecs = E([f"{d['title']}. {d['text']}" for d in docs])
def top(q):
    qv = E([q])[0]
    return max(zip([cos(v, qv) for v in vecs], docs), key=lambda x: x[0])[1]
def allowed(u, d):
    return bool(set(users.get(u, [])) & set(d["groups"]))
saved = load("leak.json") or {}
t = top(saved.get("query", "")) if saved.get("query") else None
ok(saved.get("user") == "tom" and t and saved.get("top") == t["id"] and saved.get("allowed") is False and not allowed("tom", t), "leak.json shows tom retrieving a document he must not see", f"leak.json should hold a query for which tom's top result is a document outside his groups - got {saved}")
for u, q in (("priya", "What is Harbor Foods' credit limit?"), ("lena", "When do driver shifts start?"), ("tom", "How do I reset my fuel card PIN?")):
    rc, out, err = run("leak.py", u, q)
    try:
        got = json.loads(out)
    except ValueError:
        got = {}
    t = top(q)
    want = {"user": u, "query": q, "top": t["id"], "allowed": allowed(u, t)}
    ok(got == want, f"{u}: '{q}' -> {t['id']} (allowed {want['allowed']})", f"expected {want} - got {out[:200]!r} {err[-150:]}")
PYEOF
jq -se 'any(.[]; .ok and .api == "embeddings" and .model == "lab-embed" and (.client | startswith("OpenAI/Python")))' /var/log/ailab/requests.jsonl >/dev/null 2>&1 && echo "✅ the gateway logged your lab-embed calls" || echo "❌ the gateway has no lab-embed call from your script yet"
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- One shared index with no permission checks leaks documents through normal questions.
- Demos with admin users hide the bug completely.
- Reproduce the leak to get a regression test for the fix.
