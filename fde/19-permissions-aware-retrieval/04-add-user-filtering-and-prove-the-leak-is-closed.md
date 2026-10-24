---
type: task
title: "Add user filtering and prove the leak is closed"
minutes: 9
---

## Set up

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

Write `/root/fde-lab/19-permissions/secure.py` with `search(user, query, k=3)`:

- Look up the user's groups in `users.json`; an **unknown user gets an empty list**.
- Filter to documents sharing at least one group with the user, **then** rank by cosine and return the top k as `[{"id", "title", "text"}]`.

Then write `test_permissions.py` that, for every user in `users.json` and at least four questions (include your leak question), asserts no result is outside the user's groups, and prints `permissions OK: N searches`.

```bash
cd /root/fde-lab/19-permissions
python -c "from secure import search; print([d['id'] for d in search('tom', 'What do D2 drivers earn?')])"
python test_permissions.py
```

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Reuse `ranked()` and `allowed()` from `common.py`.
- Return copies without the `groups` field: `{k: d[k] for k in ("id", "title", "text")}`.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/19-permissions
[ -f common.py ] || cat > common.py <<'EOF'
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
cat > secure.py <<'EOF'
from common import DOCS, USERS, allowed, ranked


def search(user, query, k=3):
    if user not in USERS:
        return []
    visible = [d for d in DOCS if allowed(user, d)]
    return [{key: d[key] for key in ("id", "title", "text")} for d in ranked(query, visible)[:k]]
EOF
cat > test_permissions.py <<'EOF'
from common import DOCS, USERS
from secure import search

QUESTIONS = ["What do D2 drivers earn?", "What is Harbor Foods' credit limit?", "What was the Q1 margin?", "How do I reset my fuel card PIN?"]
GROUPS = {d["id"]: set(d["groups"]) for d in DOCS}
n = 0
for user, groups in USERS.items():
    for q in QUESTIONS:
        for doc in search(user, q):
            assert GROUPS[doc["id"]] & set(groups), f"LEAK: {user} retrieved {doc['id']} for {q!r}"
        n += 1
assert search("mallory", QUESTIONS[0]) == [], "unknown users must get nothing"
print(f"permissions OK: {n} searches")
EOF
python -c "from secure import search; print([d['id'] for d in search('tom', 'What do D2 drivers earn?')])"
python test_permissions.py
```

</details>

## Check your work

```bash
D=/root/fde-lab/19-permissions; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/secure.py 2>/dev/null && [ -s $D/secure.py ] && echo "✅ secure.py reads the key from the environment" || echo "❌ secure.py must not contain a key - let the SDK read it from the environment"
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
docs, users = load("docs.json"), load("users.json")
vecs = E([f"{d['title']}. {d['text']}" for d in docs])
def ref(u, q, k):
    g = set(users.get(u, []))
    qv = E([q])[0]
    vis = [(cos(v, qv), d) for v, d in zip(vecs, docs) if g & set(d["groups"])]
    return [d["id"] for _, d in sorted(vis, key=lambda x: x[0], reverse=True)[:k]]
try:
    from secure import search
except Exception as e:
    search = None
    print(f"❌ import secure failed: {e}")
if search:
    qs = ["What do D2 drivers earn?", "Which customers have a credit limit above 30,000 EUR?", "How long does a written warning stay on file?", "Did Rotterdam make a loss?"]
    bad = []
    for u in users:
        for q in qs:
            for k in (2, 3):
                got = [d.get("id") for d in search(u, q, k)]
                if got != ref(u, q, k):
                    bad.append((u, q, k, got, ref(u, q, k)))
    ok(not bad, f"search() returns the right top-k among visible documents for {len(users)} users x {len(qs)} questions", f"search() results differ from the expected filtered ranking, e.g. {bad[:1]}")
    ok(search("mallory", qs[0]) == [] and search("", qs[0]) == [], "unknown users get no documents", "an unknown user must get an empty list")
    ok(all(set(d) == {"id", "title", "text"} for d in search("sam", qs[0])), "results carry id, title and text only", "return {id, title, text} for each result")
r = subprocess.run([sys.executable, "test_permissions.py"], capture_output=True, text=True)
ok(r.returncode == 0 and r.stdout.strip().startswith("permissions OK:"), "test_permissions.py passes", f"python test_permissions.py should print 'permissions OK: N searches' - got {r.stdout[-200:]!r} {r.stderr[-200:]}")
PYEOF
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Filter by the user's permissions before ranking, never after.
- Fail closed: unknown users and untagged documents get nothing.
- Keep a permission test that runs every release.
