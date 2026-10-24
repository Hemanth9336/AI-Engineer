---
type: task
title: "Embed two sentences and compare them"
minutes: 8
---

## Set up

```bash
ailab status
mkdir -p /root/fde-lab/13-embeddings
```

## What to build

Write `/root/fde-lab/13-embeddings/similarity.py`, used as `python similarity.py TEXT_A TEXT_B`:

1. Embed both texts with `lab-embed` in **one** API call.
2. Print their cosine similarity, rounded to 4 decimals.

```bash
cd /root/fde-lab/13-embeddings
python similarity.py "My parcel arrived broken" "Reporting a damaged parcel"
python similarity.py "My parcel arrived broken" "Support is open 8:00 to 18:00"
```

The first pair should score clearly higher than the second.

When everything is in place, press **Submit**.

<details><summary>Hints</summary>

- `a, b = [d.embedding for d in client.embeddings.create(model="lab-embed", input=[A, B]).data]`.

</details>

<details><summary>Solution</summary>

```bash
cd /root/fde-lab/13-embeddings
cat > similarity.py <<'EOF'
import math
import sys

from openai import OpenAI


def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    return dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))


resp = OpenAI().embeddings.create(model="lab-embed", input=[sys.argv[1], sys.argv[2]])
a, b = [d.embedding for d in resp.data]
print(round(cosine(a, b), 4))
EOF
python similarity.py "My parcel arrived broken" "Reporting a damaged parcel"
python similarity.py "My parcel arrived broken" "Support is open 8:00 to 18:00"
```

</details>

## Check your work

```bash
D=/root/fde-lab/13-embeddings; cd $D 2>/dev/null || echo "❌ create $D"
! grep -qE 'sk-[A-Za-z0-9_-]{8,}' $D/similarity.py 2>/dev/null && [ -s $D/similarity.py ] && echo "✅ similarity.py reads the key from the environment" || echo "❌ similarity.py must not contain a key - let the SDK read it from the environment"
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
for a, b in (("Can I send lithium batteries by air?", "Dangerous goods travel by road only"), ("Invoice payment terms", "Chilled goods in refrigerated trucks")):
    want = round(cos(*E([a, b])), 4)
    before = sum(1 for _ in open("/var/log/ailab/requests.jsonl"))
    rc, out, err = run("similarity.py", a, b)
    rows = [json.loads(l) for l in open("/var/log/ailab/requests.jsonl")][before:]
    try:
        got = float(out)
    except ValueError:
        got = None
    ok(got is not None and abs(got - want) < 0.0006, f"'{a[:25]}' vs '{b[:25]}' -> {want}", f"expected {want} - got {out[:100]!r} {err[-150:]}")
    ok(len([r for r in rows if r.get("api") == "embeddings"]) == 1, "both texts were embedded in one call", "embed both texts in a single embeddings call")
PYEOF
jq -se 'any(.[]; .ok and .api == "embeddings" and .model == "lab-embed" and (.client | startswith("OpenAI/Python")))' /var/log/ailab/requests.jsonl >/dev/null 2>&1 && echo "✅ the gateway logged your lab-embed calls" || echo "❌ the gateway has no lab-embed call from your script yet"
! grep -rqF "$LAB_AI_KEY" $D 2>/dev/null && echo "✅ no file in $D contains your lab key" || echo "❌ a file in $D contains your lab key - pass it with \$LAB_AI_KEY, never paste it"
```

## What you learned

- An embedding is a vector that places similar meanings close together.
- Batch texts into one embeddings call.
- Cosine similarity compares vectors; the ranking matters more than the raw number.
