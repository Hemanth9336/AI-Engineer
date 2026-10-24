---
type: task
title: "Query the store and inspect the top-k"
minutes: 8
---

## Set up

```bash
mkdir -p /root/fde-lab/14-vectors
```

## What to build

Write `/root/fde-lab/14-vectors/search.py`, used as `python search.py STORE_FILE QUERY K`:

1. Load the store (the format from the previous task).
2. Embed the query with `lab-embed`.
3. Print a JSON list of the top K records, highest score first: `{"id", "text", "score"}` with the score rounded to 4 decimals.

```bash
cd /root/fde-lab/14-vectors
python search.py store.json "who pays duties on imports" 3
```

Try a query nothing in the store answers, like "do you sell coffee", and look at how the scores change.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- Sort `(score, record)` pairs with `key=lambda x: x[0], reverse=True`.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/14-vectors
cat > search.py <<'EOF'
import json
import math
import sys

from openai import OpenAI


def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    return dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))


store = json.load(open(sys.argv[1]))
q = OpenAI().embeddings.create(model="lab-embed", input=[sys.argv[2]]).data[0].embedding
scored = sorted(((cosine(r["embedding"], q), r) for r in store), key=lambda x: x[0], reverse=True)
print(json.dumps([{"id": r["id"], "text": r["text"], "score": round(s, 4)} for s, r in scored[: int(sys.argv[3])]], indent=2))
EOF
python search.py store.json "who pays duties on imports" 3
```

</details>

## Check your work

```bash
D=/root/fde-lab/14-vectors; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/search.py 2>/dev/null && [ -s $D/search.py ] && echo "✅ search.py reads the key from the environment" || echo "❌ search.py must not contain a key - let the SDK read it from the environment"
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
texts = ["Fragile items need 5 cm of padding", "Pallets must be shrink-wrapped", "Invoices are issued monthly", "Lost parcels are confirmed after 10 days", "Extra cover costs 1.5 percent", "Complaints are answered in 10 days"]
Path("/tmp/cstore.json").write_text(json.dumps([{"id": f"c{i}", "text": t, "embedding": v} for i, (t, v) in enumerate(zip(texts, E(texts)), 1)]))
store = load("/tmp/cstore.json")
for q, k in (("how should I wrap a pallet", 2), ("what if my parcel disappears", 4)):
    qv = E([q])[0]
    want = sorted(((cos(r["embedding"], qv), r) for r in store), key=lambda x: x[0], reverse=True)[:k]
    rc, out, err = run("search.py", "/tmp/cstore.json", q, str(k))
    try:
        got = json.loads(out)
    except ValueError:
        got = None
    good = isinstance(got, list) and [g.get("id") for g in got] == [r["id"] for _, r in want] and all(g.get("text") == r["text"] and abs(g.get("score", 9) - s) < 0.0006 for g, (s, r) in zip(got, want))
    ok(good, f"'{q}' with k={k} returns the right top-{k} and scores", f"for '{q}' k={k} expected {[(r['id'], round(s, 4)) for s, r in want]} - got {out[:300]!r} {err[-150:]}")
PYEOF
jq -se 'any(.[]; .ok and .api == "embeddings" and .model == "lab-embed" and (.client | startswith("OpenAI/Python")))' /var/log/ailab/requests.jsonl >/dev/null 2>&1 && echo "✅ the gateway logged your lab-embed calls" || echo "❌ the gateway has no lab-embed call from your script yet"
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- Top-k returns the k most similar records; k is a tuning knob.
- Read the scores - flat, low scores often mean nothing relevant exists.
- Debug retrieval on its own before blaming the prompt.
